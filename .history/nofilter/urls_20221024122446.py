from django.urls import path, include
from .views import PostListView, PostCreateView, PostDetailView, ReviewPostCreateView, SchoolDetailView, PostCommentView, PostRecommentView, PostLikeView

urlpatterns = [
    path('', PostListView.as_view()),
    path('create', PostCreateView.as_view()),
    path('review/create', ReviewPostCreateView.as_view()),
    path('detail/<int:id>', PostDetailView.as_view()),
    path('detail/<int:id>/like', PostLikeView.as_view()),
    path('school/<int:id>', SchoolDetailView.as_view()),
    path('<int:id>/comment', PostCommentView.as_view()),
    path('<int:id>/recomment', PostRecommentView.as_view()),
]
