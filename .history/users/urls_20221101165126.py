from django.urls import path, include
from users.views import CountryListAPI, KakaoLogin, kakao_login, MyInfoAPI, UserInfoUpdateAPI, LoginAPI, SignupAPI
urlpatterns = [
    #############################################################################  -  완료
    path('country', CountryListAPI.as_view(), name='countries'),
    path('my-info', MyInfoAPI.as_view({'get': 'retrieve', 'patch': 'partial_update'}), name='user'),
    path('additional-info', UserInfoUpdateAPI.as_view(), name='user_additional_info'),
    path('', include('dj_rest_auth.urls')),
    path('login', LoginAPI.as_view(), name='login'),
    path('signup', SignupAPI.as_view(), name='signup'),
    path('kakao/login/', kakao_login, name='kakao_login'),
    path('kakao/login/finish/', KakaoLogin.as_view(), name='kakao_login_todjango'),
]
