from rest_framework import serializers
from users.models import User, Country 
from nofilter.models import Post, Comment, Recomment
from drf_writable_nested.serializers import WritableNestedModelSerializer
from dj_rest_auth.registration.serializers import RegisterSerializer

# class NofilterHighschoolCreateSerializer(serializers.ModelSerializer):
#     # 똑같은 고등학교 존재시 기존 고등학교 리턴, 유저가 새로운 고등학교시 입력 생성
#     def run_validators(self, value):
#         for validator in self.validators:
#             if isinstance(validator, UniqueTogetherValidator):
#                 self.validators.remove(validator)
#         super(NofilterHighschoolCreateSerializer, self).run_validators(value)
#     def create(self, validated_data):
#         instance, _ = Nofilter_highschool.objects.get_or_create(**validated_data)
#         return instance
#     class Meta:
#         model = Nofilter_highschool
#         fields = ('__all__')

# class NofilterHighschoolRatingSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Nofilter_highschool_rating
#         fields = ('__all__')

# class NofilterHighschoolRatingCreateSerializer(serializers.ModelSerializer):
#     def validate(self, value):
#         instance, _ = Nofilter_highschool_rating.objects.get_or_create(nofilter_highschool_id=value['nofilter_highschool_id'], item=value['item'])
#         return value
#     def create(self, validated_data):
#         instance = Nofilter_highschool_rating.objects.get(nofilter_highschool_id=validated_data['nofilter_highschool_id'].id, item=validated_data['item'])
#         instance.user_count += 1
#         instance.total_score += validated_data['total_score']
#         instance.average_score = instance.total_score / instance.user_count
#         instance.save()
#         return instance
#     class Meta:
#         model = Nofilter_highschool_rating
#         fields = ('__all__')

# # user 가입 후 user info 입력 받을 때
# class NofilterUserUpdateSerializer(WritableNestedModelSerializer):
#     nofilter_highschool = NofilterHighschoolCreateSerializer()
#     class Meta:
#         model = Nofilter_user_info
#         fields = ['nofilter_highschool', 'status', 'birthday']

# class NofilterHighschoolListSerializer(serializers.ModelSerializer):
#     nofilter_highschool_id = serializers.IntegerField(source="id")
#     class Meta:
#         model = Nofilter_highschool
#         fields = ["nofilter_highschool_id", "name", "location"]

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

# class NofilterUserReadSerializer(WritableNestedModelSerializer):
#     nofilter_highschool = NofilterHighschoolReadSerializer()
#     class Meta:
#         model = Nofilter_user_info
#         fields = ('user', 'nofilter_highschool', 'status',
#                   'birthday')
#
# class UserRegisterSerializer(WritableNestedModelSerializer):
#     nofilter_user_info = NofilterUserUpdateSerializer()
#     class Meta:
#         model = User
#         fields = ['name', 'email', 'nofilter_user_info',
#                   'password', 'is_male', ]


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

class UserUpdateSerializer(WritableNestedModelSerializer): 
    country = CountryRetrieveSerializer()
    class Meta: 
        model = User   
        fields = ('nickname', 'age', 'is_male', 'location', 'country')
    def validate(self, data):
        if data['age'] < 19:
           raise ValueError('A ForeaTown user must be 19 years old or above')
        return data

class UserReadSerializer(serializers.ModelSerializer):
    gender = serializers.SerializerMethodField()
    country = CountryReadSerializer() 
    class Meta:
        model = User
        fields = ['nickname', 'age', 'gender', 'location', 'profile_img_url', 'country']
    def get_gender(self, obj): 
        gender = 'male' if not obj.is_male else 'female'
        return gender 

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