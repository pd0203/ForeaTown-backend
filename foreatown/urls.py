from django.urls import path, include
from foreatown.views import GatherRoomAPI, GatherRoomReservationAPI, GatherRoomReviewAPI 

urlpatterns = [
    path("gather-room", GatherRoomAPI.as_view({"post": "create"})),
    path("gather-room/<int:id>", GatherRoomAPI.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"})),
    path("gather-room/list", GatherRoomAPI.as_view({"get": "list"})),
    path("gather-room/list/<int:gather_room_category_id>", GatherRoomAPI.as_view({"get": "list"})), 
    path("gather-room/mylist", GatherRoomAPI.as_view({"get": "my_list"})),   
    path("gather-room/reservation", GatherRoomReservationAPI.as_view({"post": "create"})),
    path("gather-room/reservation/list", GatherRoomReservationAPI.as_view({"get": "list"})),
    path("gather-room/reservation/<int:reservation_id>", GatherRoomReservationAPI.as_view({"delete": "destroy"})),
    path("gather-room/review", GatherRoomReviewAPI.as_view({"post": "create"})), 
    path("gather-room/review/list", GatherRoomReviewAPI.as_view({"get": "list"})) 
]