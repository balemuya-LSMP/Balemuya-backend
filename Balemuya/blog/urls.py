from django.urls import path
from .views import BlogPostListCreateAPIView, BlogPostDetailAPIView, CommentListCreateAPIView, LikeListCreateAPIView

urlpatterns = [
    path('posts/', BlogPostListCreateAPIView.as_view(), name='blog-post-list-create'), 
    path('posts/<uuid:post_id>/', BlogPostDetailAPIView.as_view(), name='blog-post-detail'),  
    path('posts/<uuid:post_id>/comments/', CommentListCreateAPIView.as_view(), name='comment-list-create-update-delete'),
    path('posts/<uuid:post_id>/likes/', LikeListCreateAPIView.as_view(), name='like-list-create'),  
]