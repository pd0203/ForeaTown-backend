from queue import Empty
from rest_framework import serializers
from foreatown.models import *
from django.conf import settings
from drf_writable_nested.serializers import WritableNestedModelSerializer
from users.serializers import CreatorSerializer, ParticipantSerializer

class GatherRoomReadSerializer(serializers.ModelSerializer):
    participants_count = serializers.SerializerMethodField()
    class Meta:
        model = GatherRoom
        fields = ['id', 'subject', 'address', 'is_online', 'user_limit', 'participants_count', 'date_time', 'gather_room_category'] 
    def get_participants_count(self, obj): 
        return UserGatherRoomReservation.objects.filter(gather_room=obj.id).count()

class GatherRoomCategoryRetrieveSerializer(serializers.RelatedField):
    def to_representation(self, value):
        return value.name
    def to_internal_value(self, data):
        try :
          return GatherRoomCategory.objects.get(name=data['name'])
        except GatherRoomCategory.DoesNotExist:
          raise ValueError('Matching GatherRoomCategory does not exist') 
    def get_queryset(self, *args):
        pass

class GatherRoomCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GatherRoomCategory
        fields = ['name',]

class GatherRoomImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GatherRoomImage
        fields = ('img_url',)

class GatherRoomOnlineCreateSerializer(WritableNestedModelSerializer):
    gather_room_category = GatherRoomCategoryRetrieveSerializer()
    # GatherRoom model에는 gather_room_image field는 없지만, GatherRoomImage model에 create()가 필요하기에 required=False로 처리
    gather_room_images = GatherRoomImageSerializer(many=True, required=False)
    class Meta: 
        model = GatherRoom   
        fields = ['subject', 'content', 'is_online', 'user_limit', 'date_time', 'creator', 'gather_room_category', 'gather_room_images']
    # def create(self, validated_data):
    #     gather_room_img_url_list = validated_data.pop('gather_room_images')
    #     gather_room = GatherRoom.objects.create(**validated_data)
    #     for img_url in gather_room_img_url_list:
    #         GatherRoomImage.objects.create(gather_room=gather_room, img_url=img_url['img_url'])
    #     return gather_room
    def validate(self, data):
        if data['user_limit'] < 2 or data['user_limit'] > 25: 
           raise ValueError('User limit must be between 2 and 25')
        ## 추가할 조건문 
        ## 1. 만약 creator가 겹치는 시간 대에 또다른 GatherRoom을 생성한 레코드가 있다면 raise ValueError
        return data

class GatherRoomOfflineCreateSerializer(WritableNestedModelSerializer):
    gather_room_category = GatherRoomCategoryRetrieveSerializer()
    # GatherRoom model에는 gather_room_image field는 없지만, GatherRoomImage model에 create()가 필요하기에 required=False로 처리
    gather_room_images = GatherRoomImageSerializer(many=True, required=False)
    class Meta: 
        model = GatherRoom   
        fields = ['subject', 'content', 'address', 'is_online', 'user_limit', 'date_time', 'creator', 'gather_room_category', 'gather_room_images']
    def validate(self, data):
        if data['address'] == '': 
           raise ValueError('Address must be specified for offline event')
        if data['user_limit'] < 2: 
           raise ValueError('User limit must be more than or equal to 2')
        ## 추가할 조건문 
        ## 1. 만약 creator가 겹치는 시간 대에 또다른 GatherRoom을 생성한 레코드가 있다면 raise ValueError
        return data

class GatherRoomRetrieveSerializer(serializers.ModelSerializer):
    creator = CreatorSerializer(read_only=True)
    participants = ParticipantSerializer(many=True, read_only=True)
    gather_room_category = GatherRoomCategorySerializer()
    gather_room_images = GatherRoomImageSerializer(many=True, read_only=True) 
    class Meta: 
        model = GatherRoom   
        fields = ['id', 'subject', 'content', 'is_online', 'user_limit', 'date_time', 'creator', 'participants', 'gather_room_category', 'gather_room_images']

class GatherRoomOfflineUpdateSerializer(WritableNestedModelSerializer):
    gather_room_category = GatherRoomCategoryRetrieveSerializer()
    gather_room_images = GatherRoomImageSerializer(many=True, required=False)
    class Meta: 
        model = GatherRoom   
        fields = ['subject', 'content', 'address', 'user_limit', 'date_time', 'gather_room_category', 'gather_room_images']
    def validate(self, data):
        if data['address'] == '': 
           raise ValueError('Address must be specified for offline event')
        if data['user_limit'] < 2: 
           raise ValueError('User limit must be more than or equal to 2')
        ## 추가할 조건문 
        ## 1. 만약 creator가 겹치는 시간 대에 또다른 GatherRoom을 생성한 레코드가 있다면 raise ValueError
        return data

class GatherRoomOnlineUpdateSerializer(WritableNestedModelSerializer):
    gather_room_category = GatherRoomCategoryRetrieveSerializer()
    gather_room_images = GatherRoomImageSerializer(many=True, required=False)
    class Meta: 
        model = GatherRoom   
        fields = ['subject', 'content', 'user_limit', 'date_time', 'gather_room_category', 'gather_room_images']
    def validate(self, data):
        if data['user_limit'] < 2 or data['user_limit'] > 25: 
           raise ValueError('User limit must be between 2 and 25')
        ## 추가할 조건문 
        ## 1. 만약 creator가 겹치는 시간 대에 또다른 GatherRoom을 생성한 레코드가 있다면 raise ValueError
        return data

class GatherRoomReservationSerializer(serializers.ModelSerializer):
    gather_room = GatherRoomReadSerializer()
    class Meta:
        model = UserGatherRoomReservation
        fields = ['gather_room']