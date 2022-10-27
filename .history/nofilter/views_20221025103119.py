from django.conf import settings
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import PostSerializer, PostCreateSerializer, PostCreateSerializer, PostDetailViewSerializer, ReviewPostCreateSerializer, PostRatingSerializer, PostRatingPostSerializer, CommentSerializer, CommentCreateSerializer, RecommentSerializer
from users.serializers import UserReadSerializer, NofilterHighschoolReadSerializer
from .models import Post, Category, PostRating, Comment, Recomment, UserPostLikes
from users.models import User, Nofilter_highschool, Nofilter_user_info
from users.views import user_validator
from .schemas import POST_LIST_CATEGORY
from rest_framework.exceptions import APIException

import json, boto3

# AWS ACCESS FOR BOTO3
AWS_ACCESS_KEY_ID = getattr(settings, 'AWS_ACCESS_KEY_ID')
AWS_ACCESS_KEY_SECRET = getattr(settings, 'AWS_ACCESS_KEY_SECRET')


# DB에 저장된 모든 post list를 불러오는 class post
# query string으로 category filtering
class PostListView(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    @extend_schema(
        tags=["Post List"],
        summary="Post list",
        responses=PostSerializer,
        parameters=[
            OpenApiParameter(
                name="category",
                description="categoty id 입력",
                required=False,
                type=int,
                enum=[1, 2],
            ),
        ],
        examples=POST_LIST_CATEGORY
    )
    @user_validator
    def get(self, request):
        try:
            user = User.objects.get(id=request.user.id)
            category = request.GET.get("category")

            if category != None:
                queryset = self.get_queryset()
                is_category = Category.objects.get(id=category)
                category_filter = queryset.filter(category=category)
                category_filter_posts = PostSerializer(
                    category_filter, many=True)
                user_serializer = UserReadSerializer(user)
                data = {
                    'login_user': user_serializer.data,
                    'post_data': category_filter_posts.data
                }
                return Response(data)

            elif category == None:
                queryset = Post.objects.all()
                serializer_all_posts = PostSerializer(queryset, many=True)
                user_serializer = UserReadSerializer(user)
                data = {
                    'login_user': user_serializer.data,
                    'post_data': serializer_all_posts.data
                }
                return Response(data)

        except Exception as e:
            raise APIException(detail=e)


# 리뷰게시판에 글 작성시 사용하는 Class
# 사진파일이 있으면 S3에 저장후 URL을 DB에 저장
class ReviewPostCreateView(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = ReviewPostCreateSerializer

    @extend_schema(
        tags=["Review Post Create"],
        summary="리뷰게시판에 글 작성",
        responses=ReviewPostCreateSerializer,
        # examples=[
        #     OpenApiExample(
        #         "test",
        #         summary="리뷰게시판 글 작성, multipart/form-data",
        #         request_only=True,
        #         media_type='multipart/form-data',
        #         value={
        #             "category": "int",
        #             "creator": "int",
        #             "subject": "string",
        #             "content": "string",
        #             "review": "object",
        #             "highschool": "int",
        #             "postfile": "file",
        #         },
        #     )
        # ]
        parameters=[
            OpenApiParameter(
                "test",
                description="리뷰게시판 글 작성, multipart/form-data",
                examples=[

                    OpenApiExample(
                        "test",
                        request_only=True,
                        summary="short optional summary",
                        description="longer description",
                        media_type='multipart/form-data',
                        value={"category": "int",
                               "creator": "int",
                               "subject": "string",
                               "content": "string",
                               "review": "object",
                               "highschool": "int",
                               "postfile": "file",
                               }
                    )
                ],
            )
        ],
        # examples=POST_LIST_CATEGORY
    )
    @user_validator
    def post(self, request):
        try:
            user_highschool = Nofilter_user_info.objects.get(
                user=request.user).nofilter_highschool
            category = request.POST.get('category')
            creator = request.POST.get('creator')
            subject = request.POST.get('subject')
            content = request.POST.get('content')
            review = json.loads(request.POST.get('review'))
            highschool = request.POST.get('highschool')

            if user_highschool.id != int(highschool):
                # return JsonResponse({'message': '로그인 회원의 고등학교와 글의 고등학교가 일치하지 않습니다.'}, status=400)
                raise APIException(detail='로그인 회원의 고등학교와 글의 고등학교가 일치하지 않습니다.')
            # user_info = Nofilter_user_info.objects.get(user_id=creator)
            # highschool = user_info.nofilter_highschool_id

            if request.FILES.get('postfile'):
                postfile = request.FILES.getlist('postfile')
                data = {
                    'category': int(category),
                    'creator': int(creator),
                    'subject': subject,
                    'content': content,
                    'review': review,
                    'highschool': int(highschool)
                }
            else:
                data = {
                    'category': int(category),
                    'creator': int(creator),
                    'subject': subject,
                    'content': content,
                    'review': review,
                    'highschool': int(highschool)
                }
            serializer = self.get_serializer(data=data)

            if serializer.is_valid(data):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(e)
            raise APIException(detail=e)

# 자유게시판에 글 작성시 사용하는 Class
# 사진파일이 있으면 S3에 저장후 URL을 DB에 저장
class PostCreateView(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostCreateSerializer

    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_ACCESS_KEY_SECRET
    )

    def post(self, request):
        try:
            category = request.POST.get('category')
            creator = request.POST.get('creator')
            subject = request.POST.get('subject')
            content = request.POST.get('content')

            if request.FILES.get('postfile'):
                postfile = request.FILES.getlist('postfile')
                data = {
                    'category': int(category),
                    'creator': int(creator),
                    'subject': subject,
                    'content': content,
                }

            else:
                data = {
                    'category': int(category),
                    'creator': int(creator),
                    'subject': subject,
                    'content': content,
                }
            serializer = self.get_serializer(data=data)

            if serializer.is_valid():
                serializer.save()

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(e)
            raise APIException(detail=e)

# post detail page
# post의 내용(제목, 내용, 사진, 유저정보, 댓글, 대댓글, 좋아요, 뷰)을 보여줌
class PostDetailView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostDetailViewSerializer

    @ user_validator
    def get(self, request, id):
        try:
            login_user = request.user
            queryset = self.get_queryset()
            detail_filter = queryset.filter(id=id)
            if not detail_filter:
                raise APIException(detail="존재하지 않는 post입니다.")
            detail_post = PostDetailViewSerializer(detail_filter, many=True)
            postLike = UserPostLikes.objects.get(user=request.user, post_id=id)

            if not detail_filter:
                return Response({'message': 'POST DOES NOT EXIST'}, status=400)

            data = {
                'detail_post': detail_post.data,
                'post_like': postLike.likes
            }

            return Response(data)

        except Exception as e:
            print(e)
            raise APIException(detail=e)

# 학교 detail page
# 해당 학교의 정보와 글 들을 보여줌
class SchoolDetailView(generics.RetrieveAPIView):
    queryset = Nofilter_highschool.objects.all()
    serializer_class = NofilterHighschoolReadSerializer

    def get(self, request, id):
        try:
            queryset = self.get_queryset()
            school = queryset.get(id=id)
            school_rating_serializer = self.get_serializer(school)

            school_posts = PostRating.objects.filter(highschool=id)
            school_post_serializer = PostRatingSerializer(
                school_posts, many=True)
            posts_result = PostRatingPostSerializer(school_posts, many=True)

            result_data = {
                "highschool": school_rating_serializer.data,
                "highschool_posts": posts_result.data
            }

            return Response(result_data)

        except Nofilter_highschool.DoesNotExist:
            raise APIException(detail="존재하지 않는 학교 id입니다")

        except Exception as e:
            print(e)
            raise APIException(detail=e)


# 댓글을 가져오거나 생성할때 사용하는 class
# content가 없으면 에러 발생
class PostCommentView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get(self, request, id):
        try:
            post = Post.objects.get(id=id)
            comments = self.get_queryset().filter(post=post)
            comments_serializer = CommentSerializer(comments, many=True)

            return Response(comments_serializer.data)

        except Exception as e:
            print(e)
            raise APIException(detail=e)

    @ user_validator
    def post(self, request, id):
        try:
            user = User.objects.get(id=request.user.id)
            post = Post.objects.get(id=id)
            content = request.data["content"]

            data = {
                "user": user.id,
                "post": post.id,
                "content": content,
            }
            serializer = CommentCreateSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Post.DoesNotExist:
            raise APIException(detail="없는 post입니다. post를 확인해주세요.")

        except User.DoesNotExist:
            raise APIException(detail="user error.")

        except Exception as e:
            print(e)
            raise APIException(detail=e)

# 대댓글을 가져오거나 생성할때 사용하는 class
# content가 없으면 에러 발생
# 해당 대댓글의 상위 댓글이 없어도 에러발생


class PostRecommentView(generics.ListCreateAPIView):
    queryset = Recomment.objects.all()
    serializer_class = RecommentSerializer

    @ user_validator
    def post(self, request, id):
        try:
            user = User.objects.get(id=request.user.id)
            post = Post.objects.get(id=id)
            comment = request.GET.get('comment')
            content = request.data["content"]
            data = {
                "user": user.id,
                "post": post.id,
                "comment": comment,
                "content": content,
            }
            serializer = RecommentSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Post.DoesNotExist:
            raise APIException(detail="없는 post입니다. post를 확인해주세요.")

        except User.DoesNotExist:
            raise APIException(detail="user error.")

        except Recomment.DoesNotExist:
            raise APIException(detail="없는 comment입니다. comment를 확인해주세요.")

        except Exception as e:
            print(e)
            raise APIException(detail=e)


# 좋아요 기능 class
# 좋아요를 누르면 해당 user와 post의 정보가 담긴 중간테이블이 DB에 생성됨
# 좋아요를 취소하면 해당 user와 post의 정보가 담긴 중간테이블이 DB에서 삭제됨
class PostLikeView(generics.ListCreateAPIView):

    @user_validator
    def post(self, request, id):
        try:
            user = User.objects.get(id=request.user.id)
            post = Post.objects.get(id=id)

            postLike, is_created = UserPostLikes.objects.get_or_create(
                user=user, post=post)

            if postLike.likes:
                postLike.delete()
            else:
                postLike.likes = True
                postLike.save()

            return Response(postLike.likes)

        except Post.DoesNotExist:
            raise APIException(detail="없는 post입니다. post를 확인해주세요.")

        except User.DoesNotExist:
            raise APIException(detail="user error.")

        except Exception as e:
            print(e)
            raise APIException(detail=e)
