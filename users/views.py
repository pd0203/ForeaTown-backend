from users.models import *
from users.serializers import *
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.kakao import views as kakao_views
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from json.decoder import JSONDecodeError
from myforeatown.settings import SIMPLE_JWT
from utils import S3Client 
from rest_framework.generics import CreateAPIView
from django.db import transaction 
from utils.token import generate_token_set 

import requests, json

# SNS Login
kakao_redirect_uri = getattr(settings, 'KAKAO_CALLBACK_URI')
kakao_rest_api_key = getattr(settings, 'KAKAO_RESTAPI_KEY')
service_base_url = getattr(settings, 'SERVICE_BASE_URL')

# AWS S3 
AWS_ACCESS_KEY_ID = getattr(settings, 'AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = getattr(settings, 'AWS_SECRET_ACCESS_KEY')
AWS_S3_BUCKET_NAME = getattr(settings, 'AWS_S3_BUCKET_NAME')

class CountryListAPI(ModelViewSet):
    serializer_class = CountryReadSerializer
    def get_queryset(self): 
        try: 
          queryset = Country.objects.all()
          country = self.request.query_params.get('name', '') 
          if country: 
             queryset = Country.objects.order_by('name').values('name').distinct()
             queryset = queryset.filter(name__icontains=country)
          return queryset 
        except Exception as e:
           return Response({'ERROR_MESSAGE': e.args}, status=status.HTTP_400_BAD_REQUEST)

class MyUserInfoAPI(ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]   
    s3_client = S3Client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET_NAME)
    def get_object(self): 
        queryset = self.get_queryset()
        if self.action == 'retrieve':
           return get_object_or_404(queryset, id=self.kwargs.get('user_id'))
        if self.action == 'partial_update':
           return get_object_or_404(queryset, id=self.request.user.id)
        return get_object_or_404(self.get_queryset()) 
    def get_serializer_class(self):
        if self.action == 'partial_update':
           return UserUpdateSerializer
        if self.action == 'retrieve':
           return UserReadSerializer 
    def retrieve(self, request, *args, **kwargs):
        try:
          instance = self.get_object()
          serializer = self.get_serializer(instance)
          return Response(serializer.data)
        except Exception as e:
           return Response({'ERROR_MESSAGE': e.args}, status=status.HTTP_400_BAD_REQUEST) 
    def partial_update(self, request, *args, **kwargs):
        try: 
          kwargs['partial'] = True
          partial = kwargs.pop('partial', False)
          user_instance = self.get_object()
          json_data = self.formdata_to_json(request)
          serializer = self.get_serializer(user_instance, data=json_data, partial=partial)
          serializer.is_valid(raise_exception=True)
          self.perform_update(serializer)
          if getattr(user_instance, '_prefetched_objects_cache', None):
             user_instance._prefetched_objects_cache = {}
          return Response(serializer.data)
        except Exception as e:
           return Response({'ERROR_MESSAGE': e.args}, status=status.HTTP_400_BAD_REQUEST) 
    def formdata_to_json(self, request): 
        form_data = request.data
        profile_image_file = request.FILES.get('profile_image')
        json_data = {
            'nickname': form_data['nickname'],
            'age': form_data['age'],
            'is_male': form_data['is_male'],
            'location': form_data['location'], 
            'country': {
               'name': form_data['country']
            },
            'profile_img_url': self.s3_client.upload(profile_image_file) 
        }
        return json_data

class UserSignUpAPI(CreateAPIView): 
      serializer_class = UserSignUpSerializer
      @transaction.atomic
      def create(self, request, *args, **kwargs):
          try:
            instance = self.get_serializer(data=request.data)
            instance.is_valid(raise_exception=True)
            instance.save()
            user_id = instance.data['id']
            token_set = generate_token_set(user_id) 
            return Response(token_set, status=status.HTTP_201_CREATED)
          except Exception as e:
            return Response({'ERROR_MESSAGE': e.args}, status=status.HTTP_400_BAD_REQUEST) 
      
class UserLoginAPI(CreateAPIView):
      serializer_class = UserLoginSerializer 
      @transaction.atomic
      def create(self, request, *args, **kwargs):
          try:
            instance = self.get_serializer(data=request.data)
            instance.is_valid(raise_exception=True)
            instance.save()
            user_id = instance.data['id']
            token_set = generate_token_set(user_id) 
            return Response(token_set, status=status.HTTP_200_OK)
          except NotFound as n:
            return Response({'ERROR_MESSAGE': n.args}, status=status.HTTP_404_NOT_FOUND)
          except Exception as e:
            return Response({'ERROR_MESSAGE': e.args}, status=status.HTTP_400_BAD_REQUEST) 

def kakao_login(request): 
    try :
      data = json.loads(request.body)
      authentication_code = data["code"]
      access_token_json = requests.get(
          f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={kakao_rest_api_key}&redirect_uri={kakao_redirect_uri}&code={authentication_code}").json()
      error = access_token_json.get("error") 
      if error: 
         raise JSONDecodeError(error)
      access_token = access_token_json.get("access_token") 
      user_data_json = requests.get("https://kapi.kakao.com/v2/user/me", headers={'Authorization': 'Bearer {}'.format(access_token)}).json()
      error = user_data_json.get("error")  
      if error:
         raise JSONDecodeError(error) 
      kakao_account = user_data_json.get("kakao_account") 
      email = kakao_account.get("email")
      name = kakao_account.get("profile").get("nickname")
      profile_image_url = kakao_account.get("profile").get("profile_image_url")
      user = User.objects.get(email=email) 
      social_user = SocialAccount.objects.filter(user=user).first()
      if social_user is None:
         raise ValueError('해당 이메일은 서비스에 존재하지만, SNS 유저가 아닙니다') 
      if social_user.provider != 'kakao':
         raise ValueError('해당 이메일은 이미', social_user.provider, 'SNS 계정으로 회원가입 되어 있습니다') 
      data = {'access_token': access_token, 'code': authentication_code}
      accept = requests.post(
           f"{service_base_url}users/kakao/login/finish/", data=data)
      accept_status = accept.status_code
      if accept_status != 200:
         raise ValueError('로그인에 실패했습니다. 다시 시도해주시기 바랍니다')
      accept_json = accept.json()
      accept_json.pop('user', None)
      User.objects.filter(email=email).update(profile_img_url=profile_image_url)
      return JsonResponse(accept_json)
    except User.DoesNotExist:
        data = {'access_token': access_token, 'code': authentication_code}
        accept = requests.post(
            f"{service_base_url}users/kakao/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
           raise ValueError('로그인에 실패했습니다. 다시 시도해주시기 바랍니다') 
        accept_json = accept.json()
        accept_json.pop('user', None)
        User.objects.filter(email=email).update(name=name, password="", sns_type="카카오톡", profile_img_url=profile_image_url)
        return JsonResponse(accept_json)
    except ValueError as v:
        return JsonResponse({'ERROR_MESSAGE': v.args[0]}, status=status.HTTP_400_BAD_REQUEST) 
    except Exception as e:
           return Response({'ERROR_MESSAGE': e.args}, status=status.HTTP_400_BAD_REQUEST)

class KakaoLogin(SocialLoginView):
    adapter_class = kakao_views.KakaoOAuth2Adapter
    client_class = OAuth2Client
    callback_url = kakao_redirect_uri