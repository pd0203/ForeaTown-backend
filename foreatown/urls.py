from django.urls import path, include
# from foreatown.views import GatherRoomAPI, GatherRoomDetailAPI, GatherRoomReservationAPI 
from foreatown.views import GatherRoomAPI

urlpatterns = [
    # 아무 유저 접근 가능한 내가 생성한 gather-room 조회 및 나만 접근가능한 내가 생성한 gather-room 수정용 
    path("gather-room/<int:id>", GatherRoomAPI.as_view({"get": "retrieve", "patch": "partial_update"})),
    # 나만 접근 가능한 내가 생성한 gather-room list 조회용
    path("gather-room/list/creation", GatherRoomAPI.as_view({"get": "creation_list"})), 
    # 나만 접근 가능한 내가 예약한 gather-room list 조회용
    # path("gather-room/list/reservation", GatherRoomReservationAPI.as_view({"get": "list"})),
    
    ################################################################################################ 완성
    # 1. 아무 유저 접근 가능한 내가 생성한 gather-room 조회 
    # 2. 아무 유저 접근 가능한 gather-room detail page 조회용 
    path("gather-room/create", GatherRoomAPI.as_view({"post": "create"})),
    # 3. 아무 유저 접근 가능한 gather-room main page 조회용 
    path("gather-room/list/", GatherRoomAPI.as_view({"get": "list"})),
    path("gather-room/list/<int:gather_room_category_id>", GatherRoomAPI.as_view({"get": "list"})),
]

# ForeaTown
    # GatherRoom CRUD API - GatherRoomAPI (C,U,D는 인증 o | list&retrieve R는 인증 x)
    # GatherRoom Detail Retrieve API - GatherRoomDetailAPI (인증 x)
    # Reservation CRUD API - GatherRoomReservationAPI (인증 o)


# MyGatherRoomAPI - 나만 접근 가능 (permission 필요)

# (1) 나만 접근할 수 있는 내가 생성한 gather-room의 list page를 위한 list api - mypage    o  