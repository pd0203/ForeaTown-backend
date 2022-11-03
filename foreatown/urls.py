from django.urls import path, include
# from users.views import KakaoLogin, kakao_login, UserAPI, LoginAPI, SignupAPI, HighschoolRead, HighSchoolView, MyPageView
from foreatown.views import GatherRoomAPI  

urlpatterns = [
    # 앞으로 만들 API
    # path("class/list", ClassAPI.as_view({"get": "class_list"})),
    # path("class/<int:pk>", ClassAPI.as_view({"get": "retrieve", "patch": "partial_update"})),
    # path("class/search", ClassAPI.as_view({"get": "class_search"}))
    path("gather-room", GatherRoomAPI.as_view({"get": "list"})), 
    path("gather-room/<int:pk>", GatherRoomAPI.as_view({"get": "retrieve"})),
    path("gather-room/post", GatherRoomAPI.as_view({"post": "create"})),
    path("gather-room/update/<int:pk>", GatherRoomAPI.as_view({"patch": "partial_update"})),   
    # 이전 노필터 API 
    # path('school/list/', HighschoolRead.as_view()),
    # path("school/", HighSchoolView.as_view({"get": "school_all_list"})),
    # path("school/<int:pk>", HighSchoolView.as_view({"get": "retrieve", "patch": "partial_update"})),
    # path("school/search/", HighSchoolView.as_view({"get": "school_search"}))
]