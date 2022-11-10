from users.models import *
from users.serializers import *
from foreatown.models import *
from foreatown.serializers import *
from rest_framework import status, generics
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from django.conf import settings
from datetime import datetime
import boto3, uuid 

# AWS ACCESS FOR BOTO3
AWS_ACCESS_KEY_ID = getattr(settings, 'AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = getattr(settings, 'AWS_SECRET_ACCESS_KEY')
AWS_S3_BUCKET_NAME = getattr(settings, 'AWS_S3_BUCKET_NAME')

# S3용 객체 인스턴스 생성 클래스 
class S3Client:
    def __init__(self, access_key, secret_key, bucket_name):
        boto3_s3 = boto3.client(
            's3',
            aws_access_key_id     = access_key,
            aws_secret_access_key = secret_key
        )
        self.s3_client   = boto3_s3
        self.bucket_name = bucket_name

    def upload(self, file):
        try: 
            file_id    = 'free' + str(uuid.uuid1()).replace('-', '')
            extra_args = { 'ContentType' : file.content_type }
            self.s3_client.upload_fileobj(
                    file,
                    self.bucket_name,
                    file_id,
                    ExtraArgs = extra_args
            )
            return f'https://{self.bucket_name}.s3.ap-northeast-2.amazonaws.com/{file_id}'
        except:
            return None
      # uuid로 file_id가 설정되어 있어 해당 file_id를 찾아 수정하려면 프론트에서 해당 아이디를 보내줘 여기서 파일
      # 아이디를 똑같이한채로 수정하거나 삭제하고 재 생성하는 법이 있다 
      # def delete(self, file): 
      #    try: 
      #       file_id    = 'free' + str(uuid.uuid1()).replace('-', '')
      #       extra_args = { 'ContentType' : file.content_type }
      #       self.s3_client.upload_fileobj(
      #               file,
      #               self.bucket_name,
      #               file_id,
      #               ExtraArgs = extra_args
      #       )
      #       return f'https://{self.bucket_name}.s3.ap-northeast-2.amazonaws.com/{file_id}'
      #   except:
      #       return None


class GatherRoomAPI(ModelViewSet):
    queryset = GatherRoom.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]    
    s3_client = S3Client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET_NAME)
    def get_object(self):
        if self.action == 'created_list':
           return get_object_or_404(self.queryset, creator=self.request.user) 
    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'created_list':
           return GatherRoomReadSerializer       
        if self.action == 'retrieve':
           return GatherRoomRetrieveSerializer
        if ((self.action == 'create' and not self.request.data['is_online']) or  
            self.request.data['gather_room_category'] == 'Hiring'):
            return GatherRoomOfflineCreateSerializer
        if self.action == 'create' and self.request.data['is_online']:
           return GatherRoomOnlineCreateSerializer
        if ((self.action == 'partial_update' and not self.request.data['is_online']) or  
            self.request.data['gather_room_category'] == 'Hiring'):
            return GatherRoomOfflineUpdateSerializer
        if self.action == 'partial_update' and self.request.data['is_online']:
           return GatherRoomOnlineUpdateSerializer 
    ########################################################################################## - 완성
    # 1. GatherRoomListWithFilteringAPI()
    def list(self, request, *args, **kwargs):
        try: 
           gather_room_category = kwargs.get('gather_room_category_id') 
           gather_room_instance = GatherRoom.objects.all()
           if gather_room_category: 
              gather_room_instance = GatherRoom.objects.filter(gather_room_category=kwargs.get('gather_room_category_id'))
           serializer = self.get_serializer(gather_room_instance, many=True)
           return Response(serializer.data)
        except Exception as e:
           return Response({'ERROR_MESSAGE': e.args}, status=status.HTTP_400_BAD_REQUEST)
    ########################################################################################## - 완성
    # 2. GatherRoomCreatedListAPI() 
    def created_list(self, request):
        try: 
           gather_room_instance = GatherRoom.objects.all()
           serializer = self.get_serializer(gather_room_instance, many=True)
           return Response(serializer.data)
        except Exception as e:
           return Response({'ERROR_MESSAGE': e.args}, status=status.HTTP_400_BAD_REQUEST)
    ########################################################################################## - 완성 
    # GatherRoomRetrieveAPI()
    # GatherRoom 디테일 페이지 보여줄 때 사용하는 Method
    def retrieve(self, request, *args, **kwargs):
        try:
           queryset = self.get_queryset()
           gather_room_instance = get_object_or_404(queryset, id=kwargs.get('id'))
           serializer = self.get_serializer(gather_room_instance)
           return Response(serializer.data)
        except Exception as e:
           return Response({'ERROR_MESSAGE': e.args}, status=status.HTTP_400_BAD_REQUEST)
    ########################################################################################## - 완성
    # GatherRoomPostAPI()
    # GatherRoom 포스팅할 떄 사용하는 Method이며, 사진 파일이 첨부되어 있으면 S3에 저장후 해당 파일 URL을 DB에 저장
    def create(self, request, *args, **kwargs):
        try:
            # convert formdata to json format  
            data = {
               'subject': request.data['subject'],
               'content': request.data['content'],
               # 'room_thema_id': int(request.data['room_thema_id']),
               'address': request.data['address'],
               'is_online': True if request.data['is_online'] == 'True' else False, 
               'user_limit': int(request.data['user_limit']),
               'date_time': datetime.strptime(request.data['date_time'], '%Y-%m-%d %H:%M:%S'),
               'creator': self.request.user.id,
               'gather_room_category': {'name': request.data['gather_room_category']},
               'gather_room_images': self.retrieve_gather_room_image_url_list(request.FILES, 'gather_room_images')
            }
            # Validate the data through serializer
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            return Response({'ERROR_MESSAGE': e.args}, status=status.HTTP_400_BAD_REQUEST) 
    ########################################################################################## - 완성
    # 4. GatherRoomUpdateAPI()
    def partial_update(self, request, *args, **kwargs): 
        try :
           partial = kwargs.pop('partial', False)
           queryset = self.get_queryset()
           gather_room_instance = get_object_or_404(queryset, creator=self.request.user, id=kwargs.get('id'))
           # convert formdata to json format 
           data = {
              'subject': request.data['subject'],
              'content': request.data['content'],
              # 'room_thema_id': int(request.data['room_thema_id']),
              'address': request.data['address'],
              'is_online': True if request.data['is_online'] == 'True' else False, 
              'user_limit': int(request.data['user_limit']),
              'date_time': datetime.strptime(request.data['date_time'], '%Y-%m-%d %H:%M:%S'),
              'creator': self.request.user.id,
              'gather_room_category': {'name': request.data['gather_room_category']},
              'gather_room_images': self.retrieve_gather_room_image_url_list(request.FILES, 'gather_room_images')  
            }
           serializer = self.get_serializer(gather_room_instance, data=data, partial=partial)
           serializer.is_valid(raise_exception=True)
           self.perform_update(serializer)
           if getattr(gather_room_instance, '_prefetched_objects_cache', None):
               # If 'prefetch_related' has been applied to a queryset, we need to
               # forcibly invalidate the prefetch cache on the instance.
               gather_room_instance._prefetched_objects_cache = {}
           return Response(serializer.data)
        except Exception as e:
           return Response({'ERROR_MESSAGE': e.args}, status=status.HTTP_400_BAD_REQUEST)
    # Upload image files into AWS S3 storage and retrieve the list of S3 image file url
    def retrieve_gather_room_image_url_list(self, files, files_key):  
        images_list = [] 
        for image_file in files.getlist(files_key):
            image_obj = {}
            image_obj['img_url'] = self.s3_client.upload(image_file)
            images_list.append(image_obj)
        return images_list 
    # Upload image files into AWS S3 storage and retrieve the list of S3 image file url
    

class GatherRoomReservationAPI(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = UserGatherRoomReservation.objects.all()   
    def get_object(self): 
        queryset = self.get_queryset()
        return get_object_or_404(queryset, id=self.request.user.id)
    def get_serializer_class(self):
        if self.action == 'create':
           return GatherRoomReservationSerializer
        if self.action == 'list':
           return GatherRoomReservationSerializer       
   #      if self.action == 'destroy': 
   #         return ReservationDeleteSerializer  
    #  ReservationPostAPI()
    def create(self, request, *args, **kwargs):
        try:
           # convert formdata to json format  
           data = {
              'user': self.request.user.id, 
              'gather_room': request.data['gather_room_id']
           }
           # Validate the data through serializer
           serializer = self.get_serializer(data=data)
           serializer.is_valid(raise_exception=True)
           self.perform_create(serializer)
           headers = self.get_success_headers(serializer.data)
           return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
           return Response({'ERROR_MESSAGE': e.args}, status=status.HTTP_400_BAD_REQUEST)
    #  ReservationListAPI() 
    def list(self, request, *args, **kwargs):
        try: 
           gather_room_reservation_instance = UserGatherRoomReservation.objects.filter(user=self.request.user.id)
           serializer = self.get_serializer(gather_room_reservation_instance, many=True)
           return Response(serializer.data)
        except Exception as e:
           return Response({'ERROR_MESSAGE': e.args}, status=status.HTTP_400_BAD_REQUEST)
    def destroy(self, request, *args, **kwargs):
        try: 
           gather_room_reservation_instance = UserGatherRoomReservation.objects.filter(user=self.request.user.id)
           serializer = self.get_serializer(gather_room_reservation_instance, many=True)
           return Response(serializer.data)
        except Exception as e:
           return Response({'ERROR_MESSAGE': e.args}, status=status.HTTP_400_BAD_REQUEST)
    # def retrieve_gather_room_id_list(self, reservation_list): 
    #     reserved_gather_room_list = []
    #     for reservation in reservation_list: 
    #         reserved_gather_room_list.append(reservation['gather_room'])
    #     return reserved_gather_room_list
    #  ReservationDeleteAPI()
    #def destroy(self, request, *args, **kwargs): 



