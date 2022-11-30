from rest_framework.pagination import PageNumberPagination

class GatherRoomListPagination(PageNumberPagination):
    page_size = 10