from users.models import *
from users.serializers import *
from rest_framework import generics, status
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.settings import (api_settings as jwt_settings,)
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.kakao import views as kakao_views
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView, RegisterView, LoginView
from dj_rest_auth.jwt_auth import set_jwt_cookies
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from json.decoder import JSONDecodeError
from myforeatown.settings import SIMPLE_JWT

import requests, json

# SNS Login
kakao_redirect_uri = getattr(settings, 'KAKAO_CALLBACK_URI')
kakao_rest_api_key = getattr(settings, 'KAKAO_RESTAPI_KEY')
service_base_url = getattr(settings, 'SERVICE_BASE_URL')

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
        except ValueError as v:
          return Response({'ERROR_MESSAGE': v.args}, status=status.HTTP_400_BAD_REQUEST)

class MyUserInfoAPI(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()   
    def get_object(self): 
        queryset = self.get_queryset()
        if self.action == 'partial_update' or self.action == 'retrieve':
           return get_object_or_404(queryset, id=self.request.user.id)
        return get_object_or_404(self.get_queryset()) 
    def get_serializer_class(self):
        if self.action == 'partial_update':
           return UserUpdateSerializer
        if self.action == 'retrieve':
           return UserReadSerializer 
    def retrieve(self, request):
        try:
          instance = self.get_object()
          serializer = self.get_serializer(instance)
          return Response(serializer.data)
        except ValueError as v:
          return Response({'ERROR_MESSAGE': v.args}, status=status.HTTP_400_BAD_REQUEST) 
    def partial_update(self, request, *args, **kwargs):
        try: 
          kwargs['partial'] = True
          return self.update(request, *args, **kwargs)
        except ValueError as v:
          return Response({'ERROR_MESSAGE': v.args}, status=status.HTTP_400_BAD_REQUEST) 

class AdditionalInfoPatchAPI(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    def get_object(self): 
        queryset = self.get_queryset()
        return get_object_or_404(queryset, id=self.request.user.id)
    def partial_update(self, request, *args, **kwargs):
        try: 
          kwargs['partial'] = True
          return self.update(request, *args, **kwargs)
        except ValueError as v:
          return Response({'ERROR_MESSAGE': v.args}, status=status.HTTP_400_BAD_REQUEST) 

class SignupAPI(RegisterView):
    def create(self, request, *args, **kwargs):
        try: 
          serializer = self.get_serializer(data=request.data)
          serializer.is_valid(raise_exception=True)
          user = self.perform_create(serializer)
          headers = self.get_success_headers(serializer.data)
          data = self.get_response_data(user)
          if data:
             del(data['user'])
             data['name'] = user.name
             response = Response(
                data,
                status=status.HTTP_201_CREATED,
                headers=headers,
             )
          else:
             response = Response(status=status.HTTP_204_NO_CONTENT, headers=headers)
          return response
        except ValueError as v:
          return Response({'ERROR_MESSAGE': v.args}, status=status.HTTP_400_BAD_REQUEST) 

class LoginAPI(LoginView): 
    def get_response(self):
        try: 
          serializer_class = self.get_response_serializer()
          if getattr(settings, 'REST_USE_JWT', False):
             access_token_expiration = (timezone.now() + jwt_settings.ACCESS_TOKEN_LIFETIME)
             refresh_token_expiration = (timezone.now() + jwt_settings.REFRESH_TOKEN_LIFETIME)
             return_expiration_times = getattr(settings, 'JWT_AUTH_RETURN_EXPIRATION', False)
             data = {
                'user': self.user,
                'access_token': self.access_token,
                'refresh_token': self.refresh_token,
             }
             if return_expiration_times:
                data['access_token_expiration'] = access_token_expiration
                data['refresh_token_expiration'] = refresh_token_expiration
             serializer = serializer_class(
                instance=data,
                context=self.get_serializer_context(),
             )
          elif self.token:
             serializer = serializer_class(
                instance=self.token,
                context=self.get_serializer_context(),
             )
          else:
            return Response(status=status.HTTP_204_NO_CONTENT)        
          response_obj = {} 
          response_obj['access_token'] = serializer.data['access_token']
          response_obj['refresh_token'] = serializer.data['refresh_token'] 
          response_obj['name'] = self.user.name 
          response = Response(response_obj, status=status.HTTP_200_OK)
          if getattr(settings, 'REST_USE_JWT', False):
             set_jwt_cookies(response, self.access_token, self.refresh_token)
          return response
        except ValueError as v: 
          return Response({'ERROR_MESSAGE': v.args}, status=status.HTTP_400_BAD_REQUEST)

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

class KakaoLogin(SocialLoginView):
    adapter_class = kakao_views.KakaoOAuth2Adapter
    client_class = OAuth2Client
    callback_url = kakao_redirect_uri