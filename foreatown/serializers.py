from rest_framework import serializers
from foreatown.models import *
from django.conf import settings
from drf_writable_nested.serializers import WritableNestedModelSerializer

class GatherRoomReadSerializer(serializers.ModelSerializer):
    gender = serializers.SerializerMethodField()
    # country = CountryReadSerializer() 
    class Meta:
        model = GatherRoom
        fields = ['nickname', 'age', 'gender', 'location', 'profile_img_url', 'country']
    def get_gender(self, obj): 
        gender = 'male' if obj.is_male else 'female'
        return gender

class GatherRoomRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = GatherRoom
        fields = ['nickname', 'age', 'gender', 'location', 'profile_img_url', 'country']

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

class GatherRoomImageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GatherRoomImage
        fields = ('img_url',)

class GatherRoomOnlinePostSerializer(WritableNestedModelSerializer):
    gather_room_category = GatherRoomCategoryRetrieveSerializer()
    # GatherRoom model에는 gather_room_image field는 없지만, GatherRoomImage model에 create()가 필요하기에 required=False로 처리
    gather_room_image = GatherRoomImageCreateSerializer(many=True, required=False)
    class Meta: 
        model = GatherRoom   
        fields = ('subject', 'content', 'room_thema_id', 'is_online', 'user_limit', 'start_datetime', 'end_datetime', 'creator', 'gather_room_category', 'gather_room_image')
    def create(self, validated_data):
        gather_room_img_url_list = validated_data.pop('gather_room_image')
        gather_room = GatherRoom.objects.create(**validated_data)
        for img_url in gather_room_img_url_list:
            GatherRoomImage.objects.create(gather_room=gather_room, img_url=img_url)
        return gather_room
    def validate(self, data):
        if data['user_limit'] < 2 or data['user_limit'] > 25: 
           raise ValueError('User limit must be between 2 and 25')
        if data['end_datetime'] <= data['start_datetime']:
           raise ValueError('End datetime must come after start datetime')
        ## 추가할 조건문 
        ## 1. 만약 creator가 겹치는 시간 대에 또다른 GatherRoom을 생성한 레코드가 있다면 raise ValueError
        return data

class GatherRoomOfflinePostSerializer(WritableNestedModelSerializer):
    gather_room_category = GatherRoomCategoryRetrieveSerializer()
    # GatherRoom model에는 gather_room_image field는 없지만, GatherRoomImage model에 create()가 필요하기에 required=False로 처리
    gather_room_image = GatherRoomImageCreateSerializer(many=True, required=False)
    class Meta: 
        model = GatherRoom   
        fields = ('subject', 'content', 'address', 'is_online', 'user_limit', 'start_datetime', 'end_datetime', 'creator', 'gather_room_category', 'gather_room_image')
    def create(self, validated_data):
        gather_room_img_url_list = validated_data.pop('gather_room_image')
        gather_room = GatherRoom.objects.create(**validated_data)
        for img_url in gather_room_img_url_list:
            GatherRoomImage.objects.create(gather_room=gather_room, img_url=img_url)
        return gather_room
    def validate(self, data):
        if data['address'] == '': 
           raise ValueError('Address must be specified for offline event')
        if data['user_limit'] < 2: 
           raise ValueError('User limit must be more than or equal to 2')
        if data['end_datetime'] <= data['start_datetime']:
           raise ValueError('End datetime must come after start datetime')  
        ## 추가할 조건문 
        ## 1. 만약 creator가 겹치는 시간 대에 또다른 GatherRoom을 생성한 레코드가 있다면 raise ValueError
        return data

class GatherRoomUpdateSerializer(WritableNestedModelSerializer):
    class Meta: 
        model = GatherRoom   
        fields = ('nickname', 'age', 'is_male', 'location', 'country')
    def validate(self, data):
        if data['age'] < 19:
           raise ValueError('A ForeaTown user must be 19 years old or above')
        return data