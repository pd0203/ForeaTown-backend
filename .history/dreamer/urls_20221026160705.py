from django.urls import path, include
# from users.views import KakaoLogin, kakao_login, UserAPI, LoginAPI, SignupAPI, HighschoolRead, HighSchoolView, MyPageView
from users.views import KakaoLogin, kakao_login, UserAPI, LoginAPI, SignupAPI

urlpatterns = [
    path('myinfo', UserAPI.as_view({'get': 'retrieve', 'put': 'update'}), name='user'),
    path('additional-info', UserAPI.as_view({'get': 'retrieve', 'put': 'update'}), name='user'),
    path('list', UserAPI.as_view({'get': 'list'}), name='user_list'),
    
    #############################################################################  -  완료
    path('', include('dj_rest_auth.urls')),
    path('login', LoginAPI.as_view(), name='login'),
    path('signup', SignupAPI.as_view(), name='signup'),
    path('kakao/login/', kakao_login, name='kakao_login'),
    path('kakao/login/finish/', KakaoLogin.as_view(), name='kakao_login_todjango'),

    # 앞으로 만들 API
    # path("class/list", ClassAPI.as_view({"get": "class_list"})),
    # path("class/<int:pk>", ClassAPI.as_view({"get": "retrieve", "patch": "partial_update"})),
    # path("class/search", ClassAPI.as_view({"get": "class_search"}))

    # 이전 노필터 API 
    # path('school/list/', HighschoolRead.as_view()),
    # path("school/", HighSchoolView.as_view({"get": "school_all_list"})),
    # path("school/<int:pk>", HighSchoolView.as_view({"get": "retrieve", "patch": "partial_update"})),
    # path("school/search/", HighSchoolView.as_view({"get": "school_search"}))
]