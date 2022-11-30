from foreatown.models import *
from foreatown.serializers import *
from users.models import User 
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from django.conf import settings
from datetime import datetime
from utils import S3Client, GatherRoomListPagination

AWS_ACCESS_KEY_ID = getattr(settings, 'AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = getattr(settings, 'AWS_SECRET_ACCESS_KEY')
AWS_S3_BUCKET_NAME = getattr(settings, 'AWS_S3_BUCKET_NAME')

class GatherRoomAPI(ModelViewSet):
    queryset = GatherRoom.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]    
    pagination_class = GatherRoomListPagination
    s3_client = S3Client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET_NAME)
    def get_object(self):
        queryset = self.get_queryset()
        if self.action == 'retrieve':
           return get_object_or_404(queryset, id=self.kwargs.get('id')) 
        if self.action == 'partial_update' or self.action == 'destroy': 
           return get_object_or_404(queryset, creator=self.request.user, id=self.kwargs.get('id'))
        return get_object_or_404(queryset, user=self.request.user)
    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'my_list':
           return GatherRoomReadSerializer       
        if self.action == 'retrieve':
           return GatherRoomRetrieveSerializer
        if ((self.action == 'create' and self.request.data['is_online'] == 'False') or  
            (self.action == 'create' and self.request.data['gather_room_category'] == 'Hiring')):
            return GatherRoomOfflineCreateSerializer
        if self.action == 'create' and self.request.data['is_online'] == 'True':
           return GatherRoomOnlineCreateSerializer
        if ((self.action == 'partial_update' and self.request.data['is_online'] == 'False') or  
            (self.action == 'partial_update' and self.request.data['gather_room_category'] == 'Hiring')):
            return GatherRoomOfflineUpdateSerializer
        if self.action == 'partial_update' and self.request.data['is_online'] == 'True':
           return GatherRoomOnlineUpdateSerializer 
    def list(self, request, *args, **kwargs):
        try: 
           gather_room_queryset = self.filter_queryset(self.get_queryset())
           gather_room_category = kwargs.get('gather_room_category_id') 
           if gather_room_category: 
              gather_room_queryset = GatherRoom.objects.filter(gather_room_category=kwargs.get('gather_room_category_id'))
           page = self.paginate_queryset(gather_room_queryset)
           if page is not None:
              serializer = self.get_serializer(page, many=True)
              return self.get_paginated_response(serializer.data)
           serializer = self.get_serializer(gather_room_queryset, many=True)
           return Response(serializer.data)
        except Exception as e:
           return Response({'ERROR_MESSAGE': e.args}, status=status.HTTP_400_BAD_REQUEST)
    def my_list(self, request, *args, **kwargs):
        try: 
           gather_room_creator = kwargs.get('user_id')
           gather_room_instance = GatherRoom.objects.filter(creator=gather_room_creator)
           serializer = self.get_serializer(gather_room_instance, many=True)
           return Response(serializer.data)
        except Exception as e:
           return Response({'ERROR_MESSAGE': e.args}, status=status.HTTP_400_BAD_REQUEST)
    def retrieve(self, request, *args, **kwargs):
        try:
           gather_room_instance = self.get_object() 
           serializer = self.get_serializer(gather_room_instance)
           return Response(serializer.data)
        except Exception as e:
           return Response({'ERROR_MESSAGE': e.args}, status=status.HTTP_400_BAD_REQUEST)
    def create(self, request, *args, **kwargs):
        try:
            json_data = self.formdata_to_json(request)
            serializer = self.get_serializer(data=json_data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response({"SUCESSFULLY_CREATED"}, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            return Response({'ERROR_MESSAGE': e.args}, status=status.HTTP_400_BAD_REQUEST) 
    def partial_update(self, request, *args, **kwargs): 
        try :
           kwargs['partial'] = True
           partial = kwargs.pop('partial', False)
           gather_room_instance = self.get_object()
           json_data = self.formdata_to_json(request)
           serializer = self.get_serializer(gather_room_instance, data=json_data, partial=partial)
           serializer.is_valid(raise_exception=True)
           self.perform_update(serializer)
           if getattr(gather_room_instance, '_prefetched_objects_cache', None):
               gather_room_instance._prefetched_objects_cache = {}
           return Response(serializer.data)
        except Exception as e:
           return Response({'ERROR_MESSAGE': e.args}, status=status.HTTP_400_BAD_REQUEST)
    def destroy(self, request, *args, **kwargs):
        try: 
           instance = self.get_object()
           self.perform_destroy(instance)
           return Response({"SUCESSFULLY_DELETED"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
           return Response({'ERROR_MESSAGE': e.args}, status=status.HTTP_400_BAD_REQUEST)
    def retrieve_gather_room_image_url_list(self, files, files_key):  
        images_list = [] 
        for image_file in files.getlist(files_key):
            image_obj = {}
            image_obj['img_url'] = self.s3_client.upload(image_file)
            images_list.append(image_obj)
        return images_list 
    def formdata_to_json(self, request): 
        form_data = request.data
        json_data = {
            'subject': form_data['subject'],
            'content': form_data['content'],
            'address': form_data['address'],
            'is_online': True if form_data['is_online'] == 'True' else False, 
            'user_limit': int(form_data['user_limit']),
            'date_time': datetime.strptime(form_data['date_time'], '%Y-%m-%d %H:%M:%S'),
            'creator': request.user.id,
            'gather_room_category': {'name': form_data['gather_room_category']},
            'gather_room_images': self.retrieve_gather_room_image_url_list(request.FILES, 'gather_room_images')  
        }
        return json_data
    
class GatherRoomReservationAPI(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = UserGatherRoomReservation.objects.all()   
    def get_object(self): 
        queryset = self.get_queryset()
        if self.action == 'destroy': 
           return get_object_or_404(queryset, user=self.request.user, id=self.kwargs.get('reservation_id'))
        return get_object_or_404(queryset, user=self.request.user)
    def get_serializer_class(self):
        if self.action == 'create':
           return GatherRoomReservationCreateSerializer
        if self.action == 'list':
           return GatherRoomReservationReadSerializer  
    def create(self, request, *args, **kwargs):
        try: 
           json_data = {
              'user': request.user.id, 
              'gather_room': request.data['gather_room_id']
           }
           serializer = self.get_serializer(data=json_data)
           serializer.is_valid(raise_exception=True)
           self.perform_create(serializer)
           headers = self.get_success_headers(serializer.data)
           return Response({"SUCESSFULLY_CREATED"}, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
           return Response({'ERROR_MESSAGE': e.args}, status=status.HTTP_400_BAD_REQUEST)
    def list(self, request, *args, **kwargs):
        try: 
           gather_room_reservation_instance = UserGatherRoomReservation.objects.filter(user=self.request.user)
           serializer = self.get_serializer(gather_room_reservation_instance, many=True)
           return Response(serializer.data)
        except Exception as e:
           return Response({'ERROR_MESSAGE': e.args}, status=status.HTTP_400_BAD_REQUEST)
    def destroy(self, request, *args, **kwargs):
        try: 
           instance = self.get_object()
           self.perform_destroy(instance)
           return Response({"SUCESSFULLY_DELETED"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
           return Response({'ERROR_MESSAGE': e.args}, status=status.HTTP_400_BAD_REQUEST)

class GatherRoomReviewAPI(ModelViewSet):
    queryset = GatherRoomReview.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]    
    def get_serializer_class(self):
        if self.action == 'create': 
           return GatherRoomReviewCreateSerializer
    def create(self, request, *args, **kwargs): 
        try:
           json_data = {
              'content': request.data['content'],
              'rating': request.data['rating'], 
              'user': request.user.id, 
              'gather_room': request.data['gather_room_id']
           }
           serializer = self.get_serializer(data=json_data)
           serializer.is_valid(raise_exception=True)
           self.perform_create(serializer)
           headers = self.get_success_headers(serializer.data)
           return Response({"SUCESSFULLY_CREATED"}, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
           return Response({'ERROR_MESSAGE': e.args}, status=status.HTTP_400_BAD_REQUEST)