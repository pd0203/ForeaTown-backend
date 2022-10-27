from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import KakaoLogin, kakao_login, UserRead, UserAPI, LoginAPI, SignupAPI, HighschoolRead, HighSchoolView, MyPageView

router = DefaultRouter()
router.register('user-read', UserRead, basename='user_read')

urlpatterns = [
    path('', include(router.urls)),
    path('mypage/', MyPageView.as_view(), name='mypage'),
    path('user', UserAPI.as_view({'get': 'list', 'put': 'update'}), name='users'),
    path('user/<int:pk>', UserAPI.as_view({'get': 'retrieve'}), name='users'),
    path('', include('dj_rest_auth.urls')),
    path('login', LoginAPI.as_view(), name='login'),
    path('signup', SignupAPI.as_view(), name='signup'),
    path('kakao/login/', kakao_login, name='kakao_login'),
    path('kakao/login/finish/', KakaoLogin.as_view(), name='kakao_login_todjango'),
    path('school/list/', HighschoolRead.as_view()),
    path("school/", HighSchoolView.as_view({"get": "school_all_list"})),
    path("school/<int:pk>", HighSchoolView.as_view({"get": "retrieve", "patch": "partial_update"})),
    path("school/search/", HighSchoolView.as_view({"get": "school_search"}))
]
