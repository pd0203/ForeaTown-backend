from users.models import *
from users.serializers import *
from foreatown.models import *
from foreatown.serializers import *
from rest_framework import generics, status
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

class GatherRoomAPI(ModelViewSet):
   #  permission_classes = [IsAuthenticated]
    queryset = GatherRoom.objects.all()    
    s3_client = boto3.client(
      's3', 
      aws_access_key_id=AWS_ACCESS_KEY_ID, 
      aws_secret_access_key=AWS_ACCESS_KEY_SECRET
    )
    def get_object(self): 
        if self.action == 'retrieve' or self.action == 'partial_update':
           return get_object_or_404(self.queryset, creator=self.request.user)
        if self.action == 'create' or self.action == 'list':
           return get_object_or_404(self.get_queryset())
    def get_serializer_class(self):
        if self.action == 'list':
           return GatherRoomReadSerializer       
        if self.action == 'retrieve':
           return GatherRoomRetrieveSerializer 
        if ((self.action == 'create' and not self.request.data['is_online']) or  
            self.request.data['gather_room_category'] == 'Hiring'):
           return GatherRoomOfflinePostSerializer
        if self.action == 'create' and self.request.data['is_online']:
           return GatherRoomOnlinePostSerializer
        if self.action == 'partial_update':
           return GatherRoomUpdateSerializer 

    # 1. GatherRoomListWithFilteringAPI()
    # def list(self, request, *args, **kwargs):
    
    # 2. GatherRoomRetrieveAPI()
    # def retrieve(self, request, *args, **kwargs):
    
    # 3. GatherRoomPostAPI()
    # GatherRoom 생성시 사용하는 Class
    # 사진파일이 있으면 S3에 저장후 URL을 DB에 저장
   #  def create(self, validated_data):
   #      instance = GatherRoom.objects.create(**validated_data)
   #      image_set = self.context['request'].FILES
   #      for image_data in image_set.getlist('postfile'):
   #          filename = 'free' + str(uuid.uuid1()).replace('-', '')
   #          self.s3_client.upload_fileobj(
   #              image_data,
   #              "copacabana-bucket",
   #              filename,
   #              ExtraArgs={
   #                  "ContentType": image_data.content_type
   #              })
   #          GatherRoom.objects.create(
   #              post=instance, file_url=f"https://copacabana-bucket.s3.ap-northeast-2.amazonaws.com/{filename}")
   #      return instance
    def create(self, request, *args, **kwargs):
        try:
            # user 
            request.data['creator'] = self.request.user.id
            # formdata process
            print('self.request', self.request)
            print('self.context[]', self.context['request'])
            image_set = self.context['request'].FILES
            print("image_set", image_set)
            for image_data in image_set.getlist('gather_room_image'):
                filename = 'free' + str(uuid.uuid1()).replace('-', '')
                self.s3_client.upload_fileobj(
                     image_data,
                     "foreatown",
                     filename,
                     ExtraArgs={
                         "ContentType": image_data.content_type
                     }) 
            request.data['gather_room_image']['img_url'] = f"https://copacabana-bucket.s3.ap-northeast-2.amazonaws.com/{filename}"
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            return Response({'ERROR_MESSAGE': e.args}, status=status.HTTP_400_BAD_REQUEST) 
   
    # 4. GatherRoomPatchAPI()
    # def partial_update(self, request, *args, **kwargs): 


# class ReservationsAPI(ModelViewSet):
#     permission_classes = [IsAuthenticated]
#     queryset = GatherRoom.objects.all()   
#     def get_object(self): 
        # queryset = self.get_queryset()
        # if self.action == 'partial_update' or self.action == 'retrieve':
        #    return get_object_or_404(queryset, id=self.request.user.id)
        # return get_object_or_404(self.get_queryset()) 
    # def get_serializer_class(self):
    #     if self.action == 'create':
    #        return ReservationPostSerializer
    #     if self.action == 'list':
    #        return ReservationReadSerializer       
    #     if self.action == 'delete': 
    #        return ReservationDeleteSerializer  
    # queryset = 
    # serializer_class = 

    # 4. ReservationPostAPI()
    # def post(self, request, *args, **kwargs):

    # 5. ReservationListAPI() 
    # def list(self, request, *args, **kwargs):

    # 6. ReservationDeleteAPI()
    # def delete(self, request, *args, **kwargs): 



