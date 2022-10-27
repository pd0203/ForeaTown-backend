from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import NofilferUserRegister, KakaoLogin, kakao_login, UserRead, HighschoolRead, HighSchoolView, MyPageView


router = DefaultRouter()
router.register('user-read', UserRead, basename='user_read')

school_list = HighSchoolView.as_view({"get": "list", "post": "create"})
school_detail = HighSchoolView.as_view(
    {"get": "retrieve", "patch": "partial_update"})


urlpatterns = [
    path('', include(router.urls)),
    path('mypage/', MyPageView.as_view(), name='mypage'),
    path('kakao/login/', kakao_login, name='kakao_login'),
    path('kakao/login/finish/', KakaoLogin.as_view(), name='kakao_login_todjango'),
    path('register/', NofilferUserRegister.as_view(), name='nofilter_register'),
    path('school/list/', HighschoolRead.as_view()),
    path("school/", HighSchoolView.as_view({"get": "school_all_list"})),
    path("school/<int:pk>", school_detail),
    path("school/search/", HighSchoolView.as_view({"get": "school_search"}))
]
