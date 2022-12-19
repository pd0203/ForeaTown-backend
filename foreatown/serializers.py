from queue import Empty
from rest_framework import serializers
from foreatown.models import *
from django.conf import settings
from rest_framework import exceptions
from drf_writable_nested.serializers import WritableNestedModelSerializer
from users.serializers import CreatorSerializer, ParticipantSerializer

class GatherRoomReadSerializer(serializers.ModelSerializer):
    participants_count = serializers.SerializerMethodField()
    class Meta:
        model = GatherRoom
        fields = ['id', 'subject', 'address', 'is_online', 'user_limit', 'participants_count', 'date_time', 'gather_room_category'] 
    def get_participants_count(self, obj): 
        return obj.participants.count()

class GatherRoomCategoryRetrieveIdByNameSerializer(serializers.RelatedField):
    def to_representation(self, value):
        return value.name
    def to_internal_value(self, data):
        try :
          return GatherRoomCategory.objects.get(name=data['name'])
        except GatherRoomCategory.DoesNotExist:
          raise ValueError('Matching GatherRoomCategory does not exist') 
    def get_queryset(self, *args):
        pass

class GatherRoomCategoryRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = GatherRoomCategory
        fields = ['name',]

class GatherRoomImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GatherRoomImage
        fields = ('img_url',)

class GatherRoomOnlineCreateSerializer(WritableNestedModelSerializer):
    gather_room_category = GatherRoomCategoryRetrieveIdByNameSerializer()
    gather_room_images = GatherRoomImageSerializer(many=True, required=False)
    class Meta: 
        model = GatherRoom   
        fields = ['subject', 'content', 'is_online', 'user_limit', 'date_time', 'creator', 'gather_room_category', 'gather_room_images']
    def __init__(self, instance=None, data=Empty, **kwargs):
        self.instance = instance
        if data is not Empty:
            self.initial_data = data
        if data['address'] != None and data['address'] != '': 
           raise ValueError('Address must not be specified for online event')
        self.partial = kwargs.pop('partial', False)
        self._context = kwargs.pop('context', {})
        kwargs.pop('many', None)
        super().__init__(**kwargs)
    def validate(self, data):
        if data['user_limit'] < 2 or data['user_limit'] > 25: 
           raise ValueError('User limit must be between 2 and 25')
        return data

class GatherRoomOfflineCreateSerializer(WritableNestedModelSerializer):
    gather_room_category = GatherRoomCategoryRetrieveIdByNameSerializer()
    gather_room_images = GatherRoomImageSerializer(many=True, required=False)
    class Meta: 
        model = GatherRoom   
        fields = ['subject', 'content', 'address', 'is_online', 'user_limit', 'date_time', 'creator', 'gather_room_category', 'gather_room_images']
    def __init__(self, instance=None, data=Empty, **kwargs):
        self.instance = instance
        if data is not Empty:
            self.initial_data = data
        if data['address'] == None or data['address'] == '': 
           raise ValueError('Address must be specified for offline event')
        self.partial = kwargs.pop('partial', False)
        self._context = kwargs.pop('context', {})
        kwargs.pop('many', None)
        super().__init__(**kwargs)
    def validate(self, data):
        if data['user_limit'] < 2: 
           raise ValueError('User limit must be more than or equal to 2')
        return data

class GatherRoomRetrieveSerializer(serializers.ModelSerializer):
    creator = CreatorSerializer(read_only=True)
    participants = ParticipantSerializer(many=True, read_only=True)
    gather_room_category = GatherRoomCategoryRetrieveSerializer()
    gather_room_images = GatherRoomImageSerializer(many=True, read_only=True) 
    class Meta: 
        model = GatherRoom   
        fields = ['id', 'subject', 'content', 'address', 'is_online', 'user_limit', 'date_time', 'creator', 'participants', 'gather_room_category', 'gather_room_images']

class GatherRoomOfflineUpdateSerializer(WritableNestedModelSerializer):
    gather_room_category = GatherRoomCategoryRetrieveIdByNameSerializer()
    gather_room_images = GatherRoomImageSerializer(many=True, required=False)
    class Meta: 
        model = GatherRoom   
        fields = ['subject', 'content', 'address', 'user_limit', 'date_time', 'gather_room_category', 'gather_room_images']
    def validate(self, data):
        if data['address'] == None or data['address'] == '': 
           raise ValueError('Address must be specified for offline event')
        if data['user_limit'] < 2: 
           raise ValueError('User limit must be more than or equal to 2')
        return data

class GatherRoomOnlineUpdateSerializer(WritableNestedModelSerializer):
    gather_room_category = GatherRoomCategoryRetrieveIdByNameSerializer()
    gather_room_images = GatherRoomImageSerializer(many=True, required=False)
    class Meta: 
        model = GatherRoom   
        fields = ['subject', 'content', 'is_online', 'user_limit', 'date_time', 'gather_room_category', 'gather_room_images']
    def validate(self, data):
        gather_room_instance = self.instance
        gather_room_instance.address = None 
        if data['user_limit'] < 2 or data['user_limit'] > 25: 
           raise ValueError('User limit must be between 2 and 25')
        return data

class GatherRoomReservationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGatherRoomReservation
        fields = ['user', 'gather_room']
    def validate(self, data):
        reservation_history = UserGatherRoomReservation.objects.filter(user=data['user'], gather_room=data['gather_room'])
        if reservation_history: 
           raise ValueError("User already made the reservation for this gather_room")
        return data

class GatherRoomReservationReadSerializer(serializers.ModelSerializer):
    gather_room = GatherRoomReadSerializer()
    class Meta:
        model = UserGatherRoomReservation
        fields = ['id', 'gather_room']

class GatherRoomReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GatherRoomReview 
        fields = ['content', 'rating', 'user', 'gather_room']
    def validate(self, data):
        reservation_history = UserGatherRoomReservation.objects.filter(user=data['user'], gather_room=data['gather_room']) 
        if not reservation_history: 
           raise exceptions.ValidationError("Participants are only allowed to write a review")
        review_history = GatherRoomReview.objects.filter(user=data['user'], gather_room=data['gather_room']) 
        if review_history: 
           raise exceptions.ValidationError("User already posted a review") 
        if data['rating'] < 0 or data['rating'] > 5: 
           raise ValueError("Rating must be between 0 and 5")
        return data 