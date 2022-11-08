from django.urls import path, include
# from foreatown.views import GatherRoomAPI, GatherRoomDetailAPI, GatherRoomReservationAPI 
from foreatown.views import GatherRoomAPI

urlpatterns = [
    path("gather-room/create", GatherRoomAPI.as_view({"post": "create"})),
    path("gather-room/list/", GatherRoomAPI.as_view({"get": "list"})),
    path("gather-room/list/creation", GatherRoomAPI.as_view({"get": "created_list"})), 
    path("gather-room/list/<int:gather_room_category_id>", GatherRoomAPI.as_view({"get": "list"})),   
    path("gather-room/<int:id>", GatherRoomAPI.as_view({"get": "retrieve", "patch": "partial_update"})),
     # path("gather-room/list/reservation", GatherRoomReservationAPI.as_view({"get": "list"})),
]

# ForeaTown
    # GatherRoom CRUD API - GatherRoomAPI (C,U,D는 인증 o | list&retrieve R는 인증 x)
    # GatherRoom Detail Retrieve API - GatherRoomDetailAPI (인증 x)
    # Reservation CRUD API - GatherRoomReservationAPI (인증 o)


# MyGatherRoomAPI - 나만 접근 가능 (permission 필요)

# (1) 나만 접근할 수 있는 내가 생성한 gather-room의 list page를 위한 list api - mypage    o  