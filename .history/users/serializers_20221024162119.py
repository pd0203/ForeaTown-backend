from rest_framework import serializers
from users.models import User, Nofilter_user_info, Nofilter_highschool_rating, Nofilter_highschool
from nofilter.models import Post, Comment, Recomment
from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework.validators import UniqueTogetherValidator


class NofilterHighschoolCreateSerializer(serializers.ModelSerializer):

    # 똑같은 고등학교 존재시 기존 고등학교 리턴, 유저가 새로운 고등학교시 입력 생성
    def run_validators(self, value):
        for validator in self.validators:
            if isinstance(validator, UniqueTogetherValidator):
                self.validators.remove(validator)
        super(NofilterHighschoolCreateSerializer, self).run_validators(value)

    def create(self, validated_data):
        instance, _ = Nofilter_highschool.objects.get_or_create(
            **validated_data)
        return instance

    class Meta:
        model = Nofilter_highschool
        fields = ('__all__')


class NofilterHighschoolRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nofilter_highschool_rating
        fields = ('__all__')


class NofilterHighschoolRatingCreateSerializer(serializers.ModelSerializer):

    def validate(self, value):
        # OrderedDict([('item', '수업'), ('user_count', 1), ('total_score', 3), ('nofilter_highschool_id', <Nofilter_highschool: 휘문고등학교>)])
        instance, _ = Nofilter_highschool_rating.objects.get_or_create(
            nofilter_highschool_id=value['nofilter_highschool_id'], item=value['item'])
        return value

    def create(self, validated_data):
        instance = Nofilter_highschool_rating.objects.get(
            nofilter_highschool_id=validated_data['nofilter_highschool_id'].id, item=validated_data['item'])
        instance.user_count += 1
        instance.total_score += validated_data['total_score']
        instance.average_score = instance.total_score / instance.user_count
        instance.save()
        return instance

    class Meta:
        model = Nofilter_highschool_rating
        fields = ('__all__')


# user 가입 후 user info 입력 받을 때
class NofilterUserUpdateSerializer(WritableNestedModelSerializer):
    nofilter_highschool = NofilterHighschoolCreateSerializer()

    class Meta:
        model = Nofilter_user_info
        fields = ['nofilter_highschool', 'status', 'birthday']


# class NofilterHighschoolCreateSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Nofilter_highschool
#         fields = ('__all__')


class NofilterHighschoolListSerializer(serializers.ModelSerializer):
    nofilter_highschool_id = serializers.IntegerField(source="id")

    class Meta:
        model = Nofilter_highschool
        fields = ["nofilter_highschool_id", "name", "location"]


class NofilterHighschoolReadSerializer(serializers.ModelSerializer):
    # Highschool_nofilter_users = NofilterUserReadSerializer(many=True)
    # highschool_rating = NofilterHighschoolRatingSerializer(many=True)

    highschool_rating = serializers.SerializerMethodField()

    def create(self, validated_data):
        instance, _ = Nofilter_highschool.objects.get_or_create(
            **validated_data)
        return instance

    def get_highschool_rating(self, obj):
        rating = obj.rating.all()
        return NofilterHighschoolRatingSerializer(instance=rating, many=True).data

    class Meta:
        model = Nofilter_highschool
        fields = ['name', 'location', 'highschool_rating']


class NofilterUserReadSerializer(WritableNestedModelSerializer):
    nofilter_highschool = NofilterHighschoolReadSerializer()

    class Meta:
        model = Nofilter_user_info
        fields = ('user', 'nofilter_highschool', 'status',
                  'birthday')


class UserRegisterSerializer(WritableNestedModelSerializer):
    nofilter_user_info = NofilterUserUpdateSerializer()

    class Meta:
        model = User
        fields = ['name', 'email', 'nofilter_user_info',
                  'password', 'is_male', ]


class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ('__all__')

class UserSignUpUpdateSerializer(WritableNestedModelSerializer): 
    class Meta: 
        model = User   
        fields = ('status', 'birthday')
    def validate(self, data): 
        if data['status'] != '멘토' and data['status'] != '멘티':
           raise ValueError('회원유형은 멘토 또는 멘티 중 하나로 선택해 주시기 바랍니다')
        return data

class UserReadSerializer(WritableNestedModelSerializer):
    user_post_likes = serializers.SerializerMethodField()

    # def update(self, obj, validated_data):
    #     # obj.email = validated_data.get('email', obj.email)
    #     # obj.username = validated_data.get('username', obj.username)
    #     # obj.password = validated_data.get('password', obj.password)
    #     # obj.profile_image_url = validated_data.get('profile_image_url', obj.profile_image_url)
    #     # obj.save()
    #     return obj

    def get_user_post_likes(self, obj):
        likes = obj.userpostlikes_set.all().filter(user=obj.id)
        posts = []

        for post in likes:
            data = Post.objects.get(id=post.id)
            serializer = PostSerializer(instance=data)
            posts.append(serializer.data)

        return posts

    class Meta:
        model = User
        fields = ['name', 'email', 'password', 'status', 'birthday', 'user_post_likes', 'is_active', 'created_at',
                  'updated_at', 'deleted_at']


class UserPostSerializer(serializers.ModelSerializer):
    nofilter_user_info = NofilterUserReadSerializer()

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'nofilter_user_info',
                  'is_active']


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
