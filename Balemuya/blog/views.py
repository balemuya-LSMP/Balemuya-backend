
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import BlogPost, Comment, Like, Media
from .serializers import BlogPostSerializer, CommentSerializer, LikeSerializer

class BlogPostListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        posts = BlogPost.objects.all()
        serializer = BlogPostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.user_type =='professional':
            return Response({'detail':'only professionals posts blog'},status=status.HTTP_401_UNAUTHORIZED)
        serializer = BlogPostSerializer(data=request.data)
        if serializer.is_valid():
            blog_post = serializer.save(author=request.user)
            media_files = request.FILES.getlist('media_files')
            print('media files',media_files)
            for media_file in media_files:
                media_type = 'image' if media_file.content_type.startswith('image/') else 'video'
                Media.objects.create(
                    post=blog_post,
                    media_file=media_file,
                    media_type=media_type
                )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BlogPostDetailAPIView(APIView):
    def get_object(self, post_id):
        try:
            return BlogPost.objects.get(id=post_id)
        except BlogPost.DoesNotExist:
            return None

    def get(self, request, post_id):
        post = self.get_object(post_id)
        if post is not None:
            serializer = BlogPostSerializer(post)
            return Response(serializer.data)
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, post_id):
        post = self.get_object(post_id)
        if post is not None:
            serializer = BlogPostSerializer(post, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, post_id):
        post = self.get_object(post_id)
        if post is not None:
            post.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

class CommentListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, post_id):
        comments = Comment.objects.filter(post=post_id)
        serializer = CommentSerializer(comments, many=True)
        number_of_comments= comments.count()
        return Response({'comments_count':number_of_comments,'data':serializer.data})

    def post(self, request, post_id):
        payload_data = request.data.copy()
        payload_data['user'] = request.user.id
        payload_data['post'] = post_id
        serializer = CommentSerializer(data=payload_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, post_id):
        comment_id = request.data.get("id")
        try:
            comment = Comment.objects.get(id=comment_id, post_id=post_id, user=request.user)
        except Comment.DoesNotExist:
            return Response({"detail": "Comment not found or not authorized."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_id):
        comment_id = request.data.get("id")
        try:
            comment = Comment.objects.get(id=comment_id, post_id=post_id, user=request.user)
        except Comment.DoesNotExist:
            return Response({"detail": "Comment not found or not authorized."}, status=status.HTTP_404_NOT_FOUND)

        comment.delete()
        return Response({"detail": "Comment deleted."}, status=status.HTTP_204_NO_CONTENT)

class LikeListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, post_id):
        likes = Like.objects.filter(post_id=post_id)
        number_of_likes = likes.count()
        serializer = LikeSerializer(likes, many=True)
        return Response({'likes_count':number_of_likes,'data':serializer.data},status=status.HTTP_200_OK)

    def post(self, request, post_id):
        user = request.user
        existing_like = Like.objects.filter(post_id=post_id, user=user).first()

        if existing_like:
            existing_like.delete()
            return Response({"detail": "Unliked successfully."}, status=status.HTTP_204_NO_CONTENT)
        else:
            payload_data = {
                "user": user.id,
                "post": post_id
            }
            serializer = LikeSerializer(data=payload_data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
