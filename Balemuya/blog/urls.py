from django.urls import path
from .views import BlogPostListCreateAPIView, BlogPostDetailAPIView, CommentListCreateAPIView, LikeListCreateAPIView

urlpatterns = [
    path('posts/', BlogPostListCreateAPIView.as_view(), name='blog_post_list_create'), 
    path('posts/<int:pk>/', BlogPostDetailAPIView.as_view(), name='blog_post_detail'),  
    path('comments/', CommentListCreateAPIView.as_view(), name='comment_list_create'),
    path('likes/', LikeListCreateAPIView.as_view(), name='like_list_create'),  
]