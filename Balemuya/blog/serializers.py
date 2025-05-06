from rest_framework import serializers
from users.serializers import UserSerializer
from .models import BlogPost, Comment, Like,Media

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'content', 'created_at','updated_at']

class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Like
        fields = ['id', 'post', 'user', 'created_at','updated_at']

class MediaSerializer(serializers.ModelSerializer):
    media_file_url = serializers.SerializerMethodField()
    class Meta:
        model = Media
        fields = ['id', 'media_file','media_file_url', 'media_type','created_at','updated_at']
        
    
    def get_media_file_url(self, obj):
        if obj.media_file:
            return obj.media_file.url
        return None

class BlogPostSerializer(serializers.ModelSerializer):
    medias = MediaSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    likes = LikeSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)

    comments_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = [
            'id',
            'title',
            'content',
            'author',
            'created_at',
            'updated_at',
            'comments',
            'likes',
            'medias',
            'comments_count',
            'likes_count',
        ]

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_likes_count(self, obj):
        return obj.likes.count()