from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import CharField
from rest_framework.exceptions import ValidationError
from users.models import User, Country 
from drf_writable_nested.serializers import WritableNestedModelSerializer
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password

class CountryRetrieveSerializer(serializers.RelatedField):
    def to_representation(self, value):
        return value.name
    def to_internal_value(self, data):
        try :
          return Country.objects.get(name=data['name'])
        except Country.DoesNotExist:
          raise ValueError('Matching country does not exist') 
    def get_queryset(self, *args):
        pass

class CountryReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['name',]

class UserReadSerializer(serializers.ModelSerializer):
    gender = serializers.SerializerMethodField()
    # country = CountryReadSerializer() 
    country = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'nickname', 'age', 'gender', 'location', 'profile_img_url', 'country']
    def get_gender(self, obj): 
        gender = 'male' if obj.is_male else 'female'
        return gender 
    def get_country(self, obj):
        country = obj.country.name
        return country 

class CreatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'profile_img_url']

class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'profile_img_url']

class UserUpdateSerializer(WritableNestedModelSerializer): 
    country = CountryRetrieveSerializer()
    class Meta: 
        model = User   
        fields = ['nickname', 'age', 'is_male', 'location', 'country', 'profile_img_url']
    def validate(self, data):
        if data['age'] < 19:
           raise ValueError('A ForeaTown user must be 19 years old or above')
        return data

class UserSignUpSerializer(ModelSerializer):
    password2 = CharField(write_only=True)
    class Meta:
        model = User 
        fields = ['id', 'email', 'password', 'password2', 'name']
    def create(self, validated_data):
        password = validated_data['password']
        password2 = validated_data['password2']
        if password != password2:
            raise ValidationError('PASSWORD1 AND PASSWORD2 DO NOT MATCH')
        validated_data.pop('password2')
        encoded_password = make_password(password)
        validated_data['password'] = encoded_password
        instance = User.objects.create(**validated_data)
        return instance
    def validate_password(self, password):
        try:
           validate_password(password)
           return password
        except ValidationError as v:
            raise ValidationError(v.args)

class UserPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'is_active']