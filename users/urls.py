from django.urls import path, include
from users.views import CountryListAPI, KakaoLogin, kakao_login, MyUserInfoAPI, AdditionalInfoPatchAPI, LoginAPI, SignupAPI

urlpatterns = [
    path('country/list', CountryListAPI.as_view({'get': 'list'}), name='country_list'),
    path('myinfo', MyUserInfoAPI.as_view({'get': 'retrieve', 'patch': 'partial_update'}), name='user_info'),
    path('additional-info', AdditionalInfoPatchAPI.as_view(), name='user_additional_info'),
    path('', include('dj_rest_auth.urls')),
    path('login', LoginAPI.as_view(), name='login'),
    path('signup', SignupAPI.as_view(), name='signup'),
    path('kakao/login/', kakao_login, name='kakao_login'),
    path('kakao/login/finish/', KakaoLogin.as_view(), name='kakao_login_todjango'),
]
