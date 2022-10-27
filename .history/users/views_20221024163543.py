from users.models import *
from users.serializers import *
from nofilter.serializers import *
from rest_framework import generics, viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
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
from copacabana.settings import SIMPLE_JWT
from datetime import datetime

import requests, json, jwt

# SNS Login Redirect URL
kakao_redirect_uri = getattr(settings, 'KAKAO_CALLBACK_URI')
# SNS Login RestAPI Key
kakao_rest_api_key = getattr(settings, 'KAKAO_RESTAPI_KEY')
# SNS BASE_URL
service_base_url = getattr(settings, 'SERVICE_BASE_URL')

# user validation 함수
# DRF에서 제공하는 permission으로 대체 가능합니다.
# 나중에 좀 더 많은 분류가 필요할때 쓰면 좋을것 같습니다.
def user_validator(func):
    def wrapper(self, request, *args, **kwargs):
        try:
            JWT_authenticator = JWTAuthentication()
            response = JWT_authenticator.authenticate(request)
            if response == None:
                raise Exception('No Token in Headers')
            token = request.headers.get('Authorization', None).split()[1]
            payload = jwt.decode(
                token,
                SIMPLE_JWT['SIGNING_KEY'],
                SIMPLE_JWT['ALGORITHM']
            )
            user = User.objects.get(id=payload["user_id"])
            request.user = user
            user_info_status = Nofilter_user_info.objects.get(user=user).status
            request.user_status = user_info_status
        except jwt.exceptions.DecodeError:
            return JsonResponse({'message': 'INVALID_TOKEN'}, status=400)
        except User.DoesNotExist:
            return JsonResponse({'message': 'INVALID_USER'}, status=400)
        except Exception as e:
            return JsonResponse({'message': f'{e}'}, status=400)
        return func(self, request, *args, **kwargs)
    return wrapper

def status_validator(func):
    def wrapper(self, request, *args, **kwargs):
        try:
            user_status = request.user_status

            if user_status != "학생":
                return JsonResponse({'message': '학생만 접근 가능합니다.'})

        except Exception as e:
            return JsonResponse({'message': f'{e}'}, status=400)

        return func(self, request, *args, **kwargs)

    return wrapper


# user 정보를 read하는 class
# user, user_info, post, liked_post를 불러옴
class UserRead(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserReadSerializer


# user 가입 후 user info 입력 받을 때 사용하는 class
class NofilferUserRegister(generics.UpdateAPIView):
    serializer_class = NofilterUserUpdateSerializer
    queryset = Nofilter_user_info

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, user=self.request.user)
        return obj

    def get_queryset(self):
        return Nofilter_user_info.objects.all()

    def perform_update(self, serializer):
        JWT_authenticator = JWTAuthentication()
        response = JWT_authenticator.authenticate(self.request)
        data = self.request.data
        if response is not None:
            # unpacking
            user, token = response
            school_serializer = self.get_serializer(data=data)
            if school_serializer.is_valid():
                serializer.save()
        else:
            print("no token is provided in the header or the header is missing")


# 고등학교 리스트를 가져오는 class
class HighschoolRead(generics.ListCreateAPIView):
    queryset = Nofilter_highschool.objects.all()
    serializer_class = NofilterHighschoolListSerializer
    def list(self, request):
        try:
            queryset = self.get_queryset()
            serializer = NofilterHighschoolListSerializer(queryset, many=True)
            return Response(serializer.data)

        except Exception as e:
            print(e)
            raise APIException(detail=e)


# user 가입시, user_info에 필요한 고등학교 입력을 하는데
# DB에 저장 되어있는 입력하는 고등학교의 이름과 지역을 가져오는 class
# DB에 정보가 있으면 가져오고 없으면 생성
class HighSchoolView(viewsets.ModelViewSet):
    queryset = Nofilter_highschool.objects.all()
    serializer_class = NofilterHighschoolListSerializer

    @action(detail=False, methods=['GET'])
    def school_all_list(self, request):
        try:
            schools = Nofilter_highschool.objects.all().order_by('name')
            serializer = NofilterHighschoolListSerializer(schools, many=True)
            return Response({"schools": serializer.data})

        except Exception as e:
            print(e)
            raise APIException(detail=e)

    @ action(detail=True, method=['GET'])
    def school_search(self, request):
        try:
            data = request.data["nofilter_highschool"]
            name = data["name"]
            location = data["location"]

            name_filter_school = Nofilter_highschool.objects.filter(name=name)
            location_filter_school = Nofilter_highschool.objects.filter(
                name=name).filter(location=location)

            name_filter_serializer = self.get_serializer(
                name_filter_school, many=True)
            location_filter_serializer = self.get_serializer(
                location_filter_school, many=True)

            if not name_filter_serializer.data:
                school_serializer = NofilterHighschoolCreateSerializer(
                    data=data)
                if school_serializer.is_valid():
                    school_serializer.save()
                    return Response({"schools": school_serializer.data})

            elif (name_filter_serializer) and (not location_filter_serializer.data):
                school_serializer = NofilterHighschoolCreateSerializer(
                    data=data)
                if school_serializer.is_valid():
                    school_serializer.save()
                    return Response({"schools": school_serializer.data})

            return Response({"schools": location_filter_serializer.data})

        except Exception as e:
            print(e)
            raise APIException(detail=e)


# user가 mypage에 접근 했을때 보여주는 정보를 불러오고 수정하는  class
# user정보, user_info, user_posts, user_post_like, comment, recomment를 불러옴
class MyPageView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserReadSerializer

    @user_validator
    def retrieve(self, request):
        try:
            user = self.get_queryset().get(id=request.user.id)

            user_serializer = self.get_serializer(user)
            post_serializer = UserAllPostSerializer(user)

            data = {
                "user_info": user_serializer.data,
                "user_posts": post_serializer.data,
            }

            return Response(data)

        except Exception as e:
            print(e)
            raise APIException(detail=e)

    @user_validator
    def put(self, request, *args, **kwargs):
        try:
            user = self.get_queryset().get(id=request.user.id)
            user_info = Nofilter_user_info.objects.get(user=user)

            user_serializer = self.get_serializer(user)

            if request.data['status'] != user_info.status:
                raise APIException(detail="신분은 바꿀수 없습니다.")

            user_info_serializer = NofilterUserReadSerializer(
                user_info, data=request.data, partial=True)

            if user_info_serializer.is_valid(raise_exception=True):
                user_info_serializer.save()
            return Response(user_info_serializer.data)

        except Exception as e:
            print(e)
            raise APIException(detail=e)

# User 회원가입시 입력된 추가정보 처리 API 
class UserAPI(ModelViewSet):
    permission_classes = [IsAuthenticated]
    def get_queryset(self): 
       return User.objects.all()   
    def get_object(self): 
       queryset = self.get_queryset()
       if self.action == 'update':
          return get_object_or_404(queryset, user=self.request.user)
       return get_object_or_404(self.get_queryset()) 
    def get_serializer_class(self):
        if self.action == 'update':
            return UserUpdateSerializer
        return UserReadSerializer
    def update(self, request, *args, **kwargs):
        try: 
          partial = kwargs.pop('partial', False)
          instance = self.get_object()
          serializer = self.get_serializer(instance, data=request.data, partial=partial)
          serializer.is_valid(raise_exception=True)
          self.perform_update(serializer)
          if getattr(instance, '_prefetched_objects_cache', None):
              instance._prefetched_objects_cache = {}
          user_name = request.user.name
          return Response(user_name + "님, 환영합니다", status=status.HTTP_200_OK)
        except ValueError as v:
            return Response({'ERROR_MESSAGE': v.args}, status=status.HTTP_400_BAD_REQUEST) 

# 자체 서비스 회원가입 API - 기존 dj-rest-auth 제공 회원가입 기능을 커스터마이징
class SignupAPI(RegisterView):
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = self.get_response_data(user)
        if data:
            # User 테이블에 정상적으로 데이터 주입 완료시 연결된 selT_user_info 생성
            Nofilter_user_info.objects.create(user=User.objects.filter(email=user.email)[0])
            del(data['user'])
            # 기존 user 객체 대신 이름만 빼내기 
            data['name'] = user.name
            response = Response(
                data,
                status=status.HTTP_201_CREATED,
                headers=headers,
            )
        else:
            response = Response(status=status.HTTP_204_NO_CONTENT, headers=headers)
        return response

# 자체 서비스 로그인 API - 기존 dj-rest-auth 제공 로그인 기능을 커스터마이징 
class LoginAPI(LoginView): 
    def get_response(self):
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

# 카카오 로그인/회원가입 API - Oauth 2.0 방식  
def kakao_login(request): 
    try :
      # [1] 프론트로부터 건네받은 인가코드로 카카오 서버에 access token 요청 
      data = json.loads(request.body)
      authentication_code = data["code"]
      access_token_json = requests.get(
          f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={kakao_rest_api_key}&redirect_uri={kakao_redirect_uri}&code={authentication_code}").json()
      error = access_token_json.get("error") 
      if error: 
         raise JSONDecodeError(error)
      access_token = access_token_json.get("access_token")
      # [2] 해당 access token으로 카카오 서버로부터 유저 데이터 객체 응답 받기  
      user_data_json = requests.get("https://kapi.kakao.com/v2/user/me", headers={'Authorization': 'Bearer {}'.format(access_token)}).json()
      error = user_data_json.get("error")  
      if error:
         raise JSONDecodeError(error) 
      # [3] 건네받은 Kakao 유저 데이터 객체 파싱     
      kakao_account = user_data_json.get("kakao_account") 
      email = kakao_account.get("email")
      name = kakao_account.get("profile").get("nickname")
      # [4] Login and Signup 
      user = User.objects.get(email=email) 
      social_user = SocialAccount.objects.filter(user=user).first()
      # 유저가 입력한 이메일로 자체 서비스 회원가입 내역이 있다면 에러발생, 없다면 로그인 
      if social_user is None:
         raise ValueError('해당 이메일은 서비스에 존재하지만, SNS 유저가 아닙니다')
      # 유저가 입력한 이메일로 다른 SNS를 통한 회원가입 내역이 있다면 에러 발생, 없다면 로그인 
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
      # user의 access token, refresh token을 담은 객체를 프론트에 반환 
      return JsonResponse(accept_json)
    except User.DoesNotExist:
        # 기존에 가입된 유저가 없으면 새로 가입
        data = {'access_token': access_token, 'code': authentication_code}
        accept = requests.post(
            f"{service_base_url}users/kakao/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
           raise ValueError('로그인에 실패했습니다. 다시 시도해주시기 바랍니다') 
        # user의 access Token, refresh token을 json 형태로 프론트에 반환 
        accept_json = accept.json()
        accept_json.pop('user', None)
        User.objects.filter(email=email).update(name=name, password="", sns_type="카카오톡")
        return JsonResponse(accept_json)
    except ValueError as v:
        return JsonResponse({'ERROR_MESSAGE': v.args[0]}, status=status.HTTP_400_BAD_REQUEST) 

# 카카오 로그인/회원가입 API - Oauth 2.0 방식
class KakaoLogin(SocialLoginView):
    adapter_class = kakao_views.KakaoOAuth2Adapter
    client_class = OAuth2Client
    callback_url = kakao_redirect_uri