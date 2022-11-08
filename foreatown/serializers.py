from rest_framework import serializers
from foreatown.models import *
from django.conf import settings
from drf_writable_nested.serializers import WritableNestedModelSerializer
from users.serializers import CreatorSerializer, ParticipantSerializer

     # [  
      #   # 온라인 
      #   {
      #      "subject": "Wanna drink with me?",
      #      "datetime": "",
      #      "address": "", 
      #      "user_limit": 20,   
      #      "user_participation": 5,     # 임의로 만든 필드 
      #      "is_online": True,       
      #      "gather_room_category_id": 1,
      #   },
      #   # 오프라인
      #   {
      #      "subject": "I wanna learn speaking English!",
      #      "datetime": "",
      #      "address": "",
      #      "user_limit": 20,
      #      "user_participation": 5, 
      #      "is_online": False,
      #      "gather_room_category_id": 1,
      #   }
      # ]

class GatherRoomReadSerializer(serializers.ModelSerializer):
    # user_participation = serializers.SerializerMethodField()
    class Meta:
        model = GatherRoom
        fields = ['id', 'subject', 'address', 'is_online', 'user_limit', 'user_participation', 'date_time', 'gather_room_category']
    # def get_user_participation(self, obj): 
    #     # gender = 'male' if obj.is_male else 'female'
    #     # return gender

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

class GatherRoomCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GatherRoomCategory
        fields = ['name',]

class GatherRoomImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GatherRoomImage
        fields = ('img_url',)

class GatherRoomOnlinePostSerializer(WritableNestedModelSerializer):
    gather_room_category = GatherRoomCategoryRetrieveSerializer()
    # GatherRoom model에는 gather_room_image field는 없지만, GatherRoomImage model에 create()가 필요하기에 required=False로 처리
    gather_room_images = GatherRoomImageSerializer(many=True, required=False)
    class Meta: 
        model = GatherRoom   
        fields = ('subject', 'content', 'is_online', 'user_limit', 'date_time', 'creator', 'gather_room_category', 'gather_room_images')
    def create(self, validated_data):
        gather_room_img_url_list = validated_data.pop('gather_room_images')
            # data['gather_room_images'][0]['img_url']
        gather_room = GatherRoom.objects.create(**validated_data)
        for img_url in gather_room_img_url_list:
            GatherRoomImage.objects.create(gather_room=gather_room, img_url=img_url['img_url'])
        return gather_room
    def validate(self, data):
        if data['user_limit'] < 2 or data['user_limit'] > 25: 
           raise ValueError('User limit must be between 2 and 25')
        ## 추가할 조건문 
        ## 1. 만약 creator가 겹치는 시간 대에 또다른 GatherRoom을 생성한 레코드가 있다면 raise ValueError
        return data

class GatherRoomOfflinePostSerializer(WritableNestedModelSerializer):
    gather_room_category = GatherRoomCategoryRetrieveSerializer()
    # GatherRoom model에는 gather_room_image field는 없지만, GatherRoomImage model에 create()가 필요하기에 required=False로 처리
    gather_room_images = GatherRoomImageSerializer(many=True, required=False)
    class Meta: 
        model = GatherRoom   
        fields = ('subject', 'content', 'address', 'is_online', 'user_limit', 'date_time', 'creator', 'gather_room_category', 'gather_room_images')
    def create(self, validated_data):
        gather_room_img_url_list = validated_data.pop('gather_room_images')
        gather_room = GatherRoom.objects.create(**validated_data)
        for img_url in gather_room_img_url_list:
            GatherRoomImage.objects.create(gather_room=gather_room, img_url=img_url)
        return gather_room
    def validate(self, data):
        if data['address'] == '': 
           raise ValueError('Address must be specified for offline event')
        if data['user_limit'] < 2: 
           raise ValueError('User limit must be more than or equal to 2')
        ## 추가할 조건문 
        ## 1. 만약 creator가 겹치는 시간 대에 또다른 GatherRoom을 생성한 레코드가 있다면 raise ValueError
        return data

class GatherRoomDetailReadSerializer(serializers.ModelSerializer):
    creator = CreatorSerializer(read_only=True)
    participants = ParticipantSerializer(many=True, read_only=True)
    gather_room_category = GatherRoomCategorySerializer()
    gather_room_images = GatherRoomImageSerializer(many=True, read_only=True) 
    class Meta: 
        model = GatherRoom   
        fields = ('subject', 'content', 'is_online', 'user_limit', 'date_time', 'creator', 'participants', 'gather_room_category', 'gather_room_images')

class GatherRoomUpdateSerializer(WritableNestedModelSerializer):
    class Meta: 
        model = GatherRoom   
        fields = ('nickname', 'age', 'is_male', 'location', 'country')
    def validate(self, data):
        if data['age'] < 19:
           raise ValueError('A ForeaTown user must be 19 years old or above')
        return data