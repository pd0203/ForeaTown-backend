from rest_framework import serializers
from users.models import User, Country 
from drf_writable_nested.serializers import WritableNestedModelSerializer
from dj_rest_auth.registration.serializers import RegisterSerializer

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

class CustomRegisterSerializer(RegisterSerializer):
    username = None
    name = serializers.CharField()
    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data['name'] = self.validated_data.get('name', '')
        return data

class UserPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'is_active']