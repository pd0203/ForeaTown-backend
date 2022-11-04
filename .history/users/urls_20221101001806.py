from django.urls import path, include
# from users.views import KakaoLogin, kakao_login, UserAPI, LoginAPI, SignupAPI, HighschoolRead, HighSchoolView, MyPageView
from users.views import KakaoLogin, kakao_login, UserAPI, UserInfoUpdateAPI, LoginAPI, SignupAPI
urlpatterns = [
    path('myinfo', UserAPI.as_view({'get': 'retrieve', 'patch': 'update'}), name='user'),
    
    #############################################################################  -  완료
    path('additional-info', UserInfoUpdateAPI.as_view(), name='user_additional_info'),
    path('', include('dj_rest_auth.urls')),
    path('login', LoginAPI.as_view(), name='login'),
    path('signup', SignupAPI.as_view(), name='signup'),
    path('kakao/login/', kakao_login, name='kakao_login'),
    path('kakao/login/finish/', KakaoLogin.as_view(), name='kakao_login_todjango'),
]