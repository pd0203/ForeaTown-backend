from django.urls import path, include
# from users.views import KakaoLogin, kakao_login, UserAPI, LoginAPI, SignupAPI, HighschoolRead, HighSchoolView, MyPageView
from users.views import KakaoLogin, kakao_login, UserAPI, LoginAPI, SignupAPI
urlpatterns = [
    path('', include('dj_rest_auth.urls')),
    path('user', UserAPI.as_view({'get': 'retrieve', 'put': 'update'}), name='user'),
    path('user/list', UserAPI.as_view({'get': 'list'}), name='user_list'),
    path('login', LoginAPI.as_view(), name='login'),
    path('signup', SignupAPI.as_view(), name='signup'),
    path('kakao/login/', kakao_login, name='kakao_login'),
    path('kakao/login/finish/', KakaoLogin.as_view(), name='kakao_login_todjango'),
    path('mypage/', MyPageView.as_view(), name='mypage'),
    path('school/list/', HighschoolRead.as_view()),
    path("school/", HighSchoolView.as_view({"get": "school_all_list"})),
    path("school/<int:pk>", HighSchoolView.as_view({"get": "retrieve", "patch": "partial_update"})),
    path("school/search/", HighSchoolView.as_view({"get": "school_search"}))
]
