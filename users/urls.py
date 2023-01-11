from django.urls import path, include
from users.views import CountryListAPI, KakaoLogin, kakao_login, MyUserInfoAPI, LoginAPI, UserSignUpAPI

urlpatterns = [
    path('country/list', CountryListAPI.as_view({'get': 'list'}), name='country_list'),
    path('myinfo', MyUserInfoAPI.as_view({'patch': 'partial_update'}), name='user_info'),
    path('myinfo/<int:user_id>', MyUserInfoAPI.as_view({'get': 'retrieve'}), name='public_user_info'),
    path('', include('dj_rest_auth.urls')),
    path('login', LoginAPI.as_view(), name='login'),
    path('signup', UserSignUpAPI.as_view(), name='signup'),
    path('kakao/login/', kakao_login, name='kakao_login'),
    path('kakao/login/finish/', KakaoLogin.as_view(), name='kakao_login_todjango'),
]
