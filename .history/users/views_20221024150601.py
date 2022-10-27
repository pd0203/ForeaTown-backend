from users.models import *
from users.serializers import *
from nofilter.serializers import *
from rest_framework import generics, viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework_simplejwt.authentication import JWTAuthentication
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.kakao import views as kakao_views
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings
from django.http import JsonResponse
from json.decoder import JSONDecodeError
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from copacabana.settings import SIMPLE_JWT

import requests, json, jwt

# SNS Login Redirect URL
kakao_redirect_uri = getattr(settings, 'KAKAO_CALLBACK_URI')
# SNS Login RestAPI Key
kakao_rest_api_key = getattr(settings, 'KAKAO_RESTAPI_KEY')
# SNS BASE_URL
kakao_base_url = getattr(settings, 'SERVICE_BASE_URL')

# user validation 함수
# DRF에서 제공하는 permission으로 대체 가능합니다.
# 나중에 좀 더 많은 분류가 필요할때 쓰면 좋을것 같습니다.
def user_validator(func):
    def wrapper(self, request, *args, **kwargs):
        try:
            JWT_authenticator = JWTAuthentication()
            response = JWT_authenticator.authenticate(request)
            # response2 = JWT_authenticator.get_header(request)
            # if request.headers.get('Authorization', None) == None:
            if response == None:
                raise Exception('No Token in Headers')

            token = request.headers.get('Authorization', None).split()[1]
            payload = jwt.decode(
                token,
                SIMPLE_JWT['SIGNING_KEY'],
                SIMPLE_JWT['ALGORITHM'])

            user = User.objects.get(id=payload["user_id"])
            request.user = user
            user_info_status = Nofilter_user_info.objects.get(user=user).status
            request.user_status = user_info_status

        except Exception as e:
            return JsonResponse({'message': f'{e}'}, status=400)

        except jwt.exceptions.DecodeError:
            return JsonResponse({'message': 'INVALID_TOKEN'}, status=400)

        except User.DoesNotExist:
            return JsonResponse({'message': 'INVALID_USER'}, status=400)

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
    # serializer_class = NofilterHighschoolReadSerializer
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
    # def get(self, request):
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

def kakao_login(request):
    # Access Token request to Kakao Server and Get the access token
    # code = request.GET.get('code')
    data = json.loads(request.body)
    authentication_code = data["code"]
    access_token_json = requests.get(
        f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={kakao_rest_api_key}&redirect_uri={kakao_redirect_uri}&code={authentication_code}").json()
    error = access_token_json.get("error")
    if error is not None:
        print("kakao request get error")
        raise JSONDecodeError(error)
    access_token = access_token_json.get("access_token")
    print("Access token: {}".format(access_token))
    # Get the User data from a Kakao server with the access token
    user_data_json = requests.get("https://kapi.kakao.com/v2/user/me", headers={
        'Authorization': 'Bearer {}'.format(access_token)}).json()
    error = user_data_json.get("error")
    if error is not None:
        print("kakao user data get error")
        raise JSONDecodeError(error)
    # Kakao Account Object
    kakao_account = user_data_json.get("kakao_account")
    print("Kakao account: {}".format(kakao_account))
    # Kakao Id
    email = kakao_account.get("email")
    nickname = kakao_account.get("profile").get("nickname")
    print("Kakao sns id: {}".format(email))
    print("Nickname: {}".format(nickname))
    # Login and Signup
    try:
        user = User.objects.get(email=email)
        # 기존에 가입된 유저의 Provider가 kakao가 아니면 에러 발생, 맞으면 로그인
        # 다른 SNS로 가입된 유저
        social_user = SocialAccount.objects.get(user=user)
        if social_user is None:
            return JsonResponse({'ERROR': 'email exists but not social user'}, status=status.HTTP_400_BAD_REQUEST)
        # if social_user.provider != 'kakao':
        #     return JsonResponse({'ERROR': 'no matching social type'}, status=status.HTTP_400_BAD_REQUEST)
        data = {'access_token': access_token, 'code': authentication_code}
        accept = requests.post(
            f"{kakao_base_url}nofilter/kakao/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse({'ERROR': 'failed to signin'}, status=accept_status)
        accept_json = accept.json()
        print(accept_json, "accept_json")
        accept_json.pop('user', None)
        return JsonResponse(accept_json)
    except User.DoesNotExist:
        # 기존에 가입된 유저가 없으면 새로 가입
        data = {'access_token': access_token, 'code': authentication_code}
        accept = requests.post(
            f"{kakao_base_url}nofilter/kakao/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse({'ERROR': 'failed to signup'}, status=accept_status)
        # user의 Access Token, Refresh token을 json 형태로 프론트에 반환
        accept_json = accept.json()
        User.objects.filter(email=email).update(
            name=nickname, password="")
        Nofilter_user_info.objects.create(
            user=User.objects.filter(email=email)[0])
        accept_json.pop('user', None)
        return JsonResponse(accept_json)


class KakaoLogin(SocialLoginView):
    adapter_class = kakao_views.KakaoOAuth2Adapter
    client_class = OAuth2Client
    callback_url = kakao_redirect_uri