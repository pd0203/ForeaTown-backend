from django.urls import path, include
from foreatown.views import GatherRoomAPI, GatherRoomReservationAPI, GatherRoomReviewAPI 

urlpatterns = [
    path("gather-room", GatherRoomAPI.as_view({"post": "create"}), name="post_gather_room"),
    path("gather-room/<int:id>", GatherRoomAPI.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"}), name="create_update_delete_gather_room"),
    path("gather-room/list", GatherRoomAPI.as_view({"get": "list"}), name="get_gather_room_list"),
    path("gather-room/list/<int:gather_room_category_id>", GatherRoomAPI.as_view({"get": "list"}), name="get_gather_room_list_by_category"), 
    path("gather-room/mylist/<int:user_id>", GatherRoomAPI.as_view({"get": "my_list"}), name="get_my_gather_room_list"),   
    path("gather-room/reservation", GatherRoomReservationAPI.as_view({"post": "create"}), name="post_gather_room_reservation"),
    path("gather-room/reservation/list", GatherRoomReservationAPI.as_view({"get": "list"}), name="get_gather_room_reservation_list"),
    path("gather-room/reservation/<int:reservation_id>", GatherRoomReservationAPI.as_view({"delete": "destroy"}), name="delete_gather_room_reservation"),
    path("gather-room/review", GatherRoomReviewAPI.as_view({"post": "create"}), name="post_gather_room_review"), 
    path("gather-room/review/list", GatherRoomReviewAPI.as_view({"get": "list"}), name="get_gather_room_review_list") 
]