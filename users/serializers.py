from rest_framework import serializers
from users.models import User, Country 
from nofilter.models import Post, Comment, Recomment
from drf_writable_nested.serializers import WritableNestedModelSerializer
from dj_rest_auth.registration.serializers import RegisterSerializer

# class NofilterHighschoolReadSerializer(serializers.ModelSerializer):
#     highschool_rating = serializers.SerializerMethodField()
#     def create(self, validated_data):
#         instance, _ = Nofilter_highschool.objects.get_or_create(
#             **validated_data)
#         return instance
#     def get_highschool_rating(self, obj):
#         rating = obj.rating.all()
#         return NofilterHighschoolRatingSerializer(instance=rating, many=True).data
#     class Meta:
#         model = Nofilter_highschool
#         fields = ['name', 'location', 'highschool_rating']

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('__all__')

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
        fields = ('name',)

class UserReadSerializer(serializers.ModelSerializer):
    gender = serializers.SerializerMethodField()
    country = CountryReadSerializer() 
    class Meta:
        model = User
        fields = ['id', 'nickname', 'age', 'gender', 'location', 'profile_img_url', 'country']
    def get_gender(self, obj): 
        gender = 'male' if obj.is_male else 'female'
        return gender 

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
        fields = ('nickname', 'age', 'is_male', 'location', 'country')
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

class UserRecommentGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recomment
        fields = ('__all__')

class UserCommentGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('__all__')

class UserPostGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('__all__')

class UserAllPostSerializer(serializers.ModelSerializer):
    all_post = serializers.SerializerMethodField()
    all_comment = serializers.SerializerMethodField()
    all_recomment = serializers.SerializerMethodField()
    def get_all_recomment(self, obj):
        recomments_data = []
        recomments = obj.recomment_set.all()
        for recomment in recomments:
            recomments_data.append(UserRecommentGetSerializer(recomment).data)
        return recomments_data
    def get_all_comment(self, obj):
        comments_data = []
        comments = obj.comment_set.all()
        for comment in comments:
            comments_data.append(UserCommentGetSerializer(comment).data)
        return comments_data
    def get_all_post(self, obj):
        posts_data = []
        posts = obj.post_set.all()
        for post in posts:
            posts_data.append(UserPostGetSerializer(post).data)
        return posts_data
    class Meta:
        model = User
        fields = ['all_post', 'all_comment', 'all_recomment']