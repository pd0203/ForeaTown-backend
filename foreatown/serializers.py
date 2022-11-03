from rest_framework import serializers
from foreatown.models import *
from django.conf import settings
from drf_writable_nested.serializers import WritableNestedModelSerializer
import boto3, uuid 

# AWS ACCESS FOR BOTO3
AWS_ACCESS_KEY_ID = getattr(settings, 'AWS_ACCESS_KEY_ID')
AWS_ACCESS_KEY_SECRET = getattr(settings, 'AWS_ACCESS_KEY_SECRET')

class GatherRoomReadSerializer(serializers.ModelSerializer):
    # gender = serializers.SerializerMethodField()
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

class GatherRoomCategoryRetrieveSerializer(serializers.ModelSerializer):
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
        fields = ['img_url',]

class GatherRoomOnlinePostSerializer(WritableNestedModelSerializer):
    gather_room_category = GatherRoomCategoryRetrieveSerializer()
    gather_room_image = GatherRoomImageCreateSerializer()
    class Meta: 
        model = GatherRoom   
        fields = ('subject', 'content', 'room_thema_id', 'is_online', 'user_limit', 'male_ratio', 'start_datetime', 'end_datetime', 'creator', 'gather_room_category', 'gather_room_image')
    def validate(self, data):
        if data['gather_room_category'] == 'Hiring':
           raise ValueError('Hiring has to be on offline')
        if data['end_datetime'] <= data['start_datetime']:
           raise ValueError('End datetime must come after start datetime')
        if data['male_ratio'] < 0 or data['male_ratio'] > 1:
           raise ValueError('Invalid male ratio. It must be between 0 and 1')
        ## 추가할 조건문 
        ## 1. 만약 creator가 겹치는 시간 대에 또다른 GatherRoom을 생성한 레코드가 있다면 raise ValueError
        
        return data

class GatherRoomOfflinePostSerializer(WritableNestedModelSerializer):
    gather_room_category = GatherRoomCategoryRetrieveSerializer()
    gather_room_image = GatherRoomImageCreateSerializer()
    class Meta: 
        model = GatherRoom   
        fields = ('subject', 'content', 'address', 'is_online', 'user_limit', 'male_ratio', 'start_datetime', 'end_datetime', 'creator', 'gather_room_category', 'gather_room_image')
    def validate(self, data):
        if data['gather_room_category'] == 'Hiring':
           data['male_ratio'] = None 
        if data['end_datetime'] <= data['start_datetime']:
           raise ValueError('End datetime must come after start datetime')  
        ## 추가할 조건문 
        ## 1. 만약 creator가 겹치는 시간 대에 또다른 GatherRoom을 생성한 레코드가 있다면 raise ValueError
        
        return data

# class PostCreateSerializer(WritableNestedModelSerializer):
#     postfile = PostFileUploadSerializer(required=False)
#     class Meta:
#         model = Post
#         fields = ("id", "category", "creator", "subject", "content",
#                   "created_at", "postfile")
class GatherRoomUpdateSerializer(WritableNestedModelSerializer):
    class Meta: 
        model = GatherRoom   
        fields = ('nickname', 'age', 'is_male', 'location', 'country')
    def validate(self, data):
        if data['age'] < 19:
           raise ValueError('A ForeaTown user must be 19 years old or above')
        return data