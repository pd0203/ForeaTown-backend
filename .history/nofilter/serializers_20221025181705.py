from rest_framework import serializers
from drf_writable_nested.serializers import WritableNestedModelSerializer
from .models import Category, Post, PostFile, Comment, Recomment
from users.models import User
from users.serializers import UserPostSerializer, NofilterHighschoolRatingCreateSerializer
import json, boto3, uuid
from django.conf import settings

# AWS ACCESS FOR BOTO3
AWS_ACCESS_KEY_ID = getattr(settings, 'AWS_ACCESS_KEY_ID')
AWS_ACCESS_KEY_SECRET = getattr(settings, 'AWS_ACCESS_KEY_SECRET')

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('__all__')

class PostListSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    class Meta:
        model = Post
        fields = ("category", "creator", "subject", "content",
                  "view", "created_at")

class PostFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostFile
        fields = ("__all__")

class PostFileUploadSerializer(serializers.ModelSerializer):
    postfile = serializers.FileField()
    class Meta:
        model = PostFile
        fields = ["postfile"]

# class PostSerializer(serializers.ModelSerializer):
#     category = serializers.StringRelatedField()
#     postfile = serializers.SerializerMethodField()
#     creator = UserPostSerializer()
#     reviewrating = serializers.SerializerMethodField()
#     postlikes = serializers.SerializerMethodField()
#     commentcount = serializers.SerializerMethodField()
#     def get_commentcount(self, obj):
#         comments = obj.comment_set.all()
#         comments_count = comments.count()
#         recomments_count = 0
#         for comment in comments:
#             recomment = comment.recomment_set.all()
#             recomment_count = recomment.count()
#             recomments_count += recomment_count
#         total_count = comments_count + recomments_count
#         return total_count
#     def get_postlikes(self, obj):
#         likes = obj.userpostlikes_set.all().filter(likes=True).all()
#         likes_count = likes.count()
#         return likes_count
#     def get_postfile(self, obj):
#         file = obj.postfile_set.all()
#         return PostFileSerializer(instance=file, many=True).data
#     def get_reviewrating(self, obj):
#         rating = obj.postrating_set.all()
#         return PostRatingSerializer(instance=rating, many=True).data
#     class Meta:
#         model = Post
#         fields = ("id", "category", "creator", "subject", "content", "postlikes",
#                   "view", "created_at", "postfile", "reviewrating", "commentcount")


class PostCreateSerializer(WritableNestedModelSerializer):
    postfile = PostFileUploadSerializer(required=False)
    class Meta:
        model = Post
        fields = ("id", "category", "creator", "subject", "content",
                  "created_at", "postfile")
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_ACCESS_KEY_SECRET
    )
    def create(self, validated_data):
        instance = Post.objects.create(**validated_data)
        image_set = self.context['request'].FILES
        for image_data in image_set.getlist('postfile'):
            filename = 'free' + str(uuid.uuid1()).replace('-', '')
            self.s3_client.upload_fileobj(
                image_data,
                "copacabana-bucket",
                filename,
                ExtraArgs={
                    "ContentType": image_data.content_type
                })
            PostFile.objects.create(
                post=instance, file_url=f"https://copacabana-bucket.s3.ap-northeast-2.amazonaws.com/{filename}")
        return instance

# class PostRatingSerializer(serializers.ModelSerializer):
#     nofilter_highschool = serializers.IntegerField(source="highschool_id")
#     class Meta:
#         model = PostRating
#         fields = ["nofilter_highschool", "post", "item", "rating"]

# class ReviewPostCreateSerializer(WritableNestedModelSerializer):
#     postfile = PostFileUploadSerializer(required=False)
#     s3_client = boto3.client(
#         's3',
#         aws_access_key_id=AWS_ACCESS_KEY_ID,
#         aws_secret_access_key=AWS_ACCESS_KEY_SECRET
#     )
#     def create(self, validated_data):
#         instance = Post.objects.create(**validated_data)
#         image_set = self.context['request'].FILES
#         review_data = json.loads(self.context['request'].data['review'])
#         highschool_id = self.context['request'].data['highschool']
#         for image_data in image_set.getlist('postfile'):
#             filename = 'review' + str(uuid.uuid1()).replace('-', '')
#             self.s3_client.upload_fileobj(
#                 image_data,
#                 "copacabana-bucket",
#                 filename,
#                 ExtraArgs={
#                     "ContentType": image_data.content_type
#                 })
#             PostFile.objects.create(
#                 post=instance, file_url=f"https://copacabana-bucket.s3.ap-northeast-2.amazonaws.com/{filename}")
#         for key in review_data:
#             PostRating.objects.create(
#                 post=instance, item=key, rating=int(review_data[key]), highschool_id=int(highschool_id))
#         for key in review_data:
#             data = {
#                 'nofilter_highschool_id': Nofilter_highschool.objects.get(id=highschool_id).id,
#                 'item': key,
#                 'total_score': int(review_data[key]),
#             }
#             highschool_rating_serializer = NofilterHighschoolRatingCreateSerializer(
#                 data=data)
#             if highschool_rating_serializer.is_valid(data):
#                 highschool_rating_serializer.save()
#         return instance
#     class Meta:
#         model = Post
#         fields = ("id", "category", "creator", "subject", "content",
#                   "created_at", "postfile")

class RecommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recomment
        fields = ('__all__')

class CommentCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ['user', 'post', 'content']

class CommentSerializer(serializers.ModelSerializer):
    recomment = serializers.SerializerMethodField()
    def get_recomment(self, obj):
        recomment = obj.recomment_set.all()
        return RecommentSerializer(instance=recomment, many=True).data
    class Meta:
        model = Comment
        fields = ('id', 'user', 'content', 'created_at', 'recomment')

# class PostDetailViewSerializer(serializers.ModelSerializer):
#     category = serializers.StringRelatedField()
#     postfile = serializers.SerializerMethodField()
#     creator = UserPostSerializer()
#     comment = serializers.SerializerMethodField()
#     comment_count = serializers.SerializerMethodField()
#     reviewrating = serializers.SerializerMethodField()
#     postlikes = serializers.SerializerMethodField()
#     def get_postlikes(self, obj):
#         # likes = obj.userpostlikes_all().filter(likes=True).all()
#         likes = obj.userpostlikes_set.all().filter(likes=True).all()
#         likes_count = likes.count()
#         return likes_count
#     def get_comment_count(self, obj):
#         comments = obj.comment_set.all()
#         recomment_count = 0
#         for comment in comments:
#             recomments = comment.recomment_set.all()
#             recomment_count += recomments.count()
#         # recomment = comment.recomment_set.all()
#         all_comments_count = comments.count() + recomment_count
#         return all_comments_count
#     def get_comment(self, obj):
#         comment = obj.comment_set.all()
#         return CommentSerializer(instance=comment, many=True).data
#     def get_postfile(self, obj):
#         file = obj.postfile_set.all()
#         return PostFileSerializer(instance=file, many=True).data
#     def get_reviewrating(self, obj):
#         rating = obj.postrating_set.all()
#         return PostRatingSerializer(instance=rating, many=True).data
#     class Meta:
#         model = Post
#         fields = ("category", "creator", "subject", "content", "reviewrating", 'postlikes',
#                   "view", "created_at", "postfile", 'comment', 'comment_count')

# class PostRatingPostSerializer(serializers.ModelSerializer):
#     posts = serializers.SerializerMethodField()
#     def get_posts(self, obj):
#         post = Post.objects.filter(id=obj.post_id)
#         return PostDetailViewSerializer(instance=post, many=True).data
#     class Meta:
#         model = PostRating
#         fields = ['posts']

class PostSerializerCreate(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    postfile = serializers.SerializerMethodField()
    def get_postfile(self, obj):
        file = obj.postfile_set.all()
        return PostFileSerializer(instance=file, many=True).data
    class Meta:
        model = Post
        fields = ("category", "creator", "subject", "content",
                  "view", "created_at", "postfile")