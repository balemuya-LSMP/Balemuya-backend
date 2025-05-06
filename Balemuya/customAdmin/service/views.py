# from customAdmin.packages import *

from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from services.models import ServicePostReport,ServiceBooking,ServicePost,ServicePostApplication,ServiceRequest
from services.serializers import ServicePostSerializer,ServicePostReportSerializer,ServicePostApplicationSerializer,ServiceRequestSerializer,\
    ServiceBookingSerializer,ServicePostReportSerializer

from customAdmin.permissions import IsAdmin



class AdminServicePostListView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        """
        Admin-only endpoint to list all service posts.
        Optional filtering by status (?status=pending)
        """
        status_filter = request.query_params.get('status')
        posts = ServicePost.objects.all().order_by('-created_at')

        if status_filter:
            posts = posts.filter(status=status_filter)

        serializer = ServicePostReportSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminServicePostReportListView(APIView):
    permission_classes = [IsAdmin,IsAuthenticated]

    def get(self, request):
        reports = ServicePostReport.objects.select_related('service_post', 'reporter').all()
        serializer = ServicePostReportSerializer(reports, many=True)
        return Response(serializer.data)

class AdminServicePostDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_object(self, service_post_id):
        try:
            return ServicePost.objects.get(id=service_post_id)
        except ServicePost.DoesNotExist:
            raise NotFound("Service post not found.")

    def get(self, request, service_post_id):
        """
        Retrieve detailed info of a specific service post by ID.
        """
        post = self.get_object(service_post_id)
        serializer = ServicePostReportSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class AdminToggleServicePostStatusView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_object(self, service_post_id):
        try:
            return ServicePost.objects.get(id=service_post_id)
        except ServicePost.DoesNotExist:
            raise NotFound("Service post not found.")

    def post(self, request, service_post_id):
        """
        Toggle the active status of a service post.
        """
        post = self.get_object(service_post_id)
        post.is_active = not post.is_active  # or use `post.status` if that's your field
        post.save()

        return Response({
            "message": f"Service post status set to {'active' if post.is_active else 'inactive'}.",
            "service_post_id": str(post.id),
            "is_active": post.is_active
        }, status=status.HTTP_200_OK)

    
class AdminDeleteReportedPostView(APIView):
    permission_classes = [IsAdmin,IsAuthenticated]

    def delete(self, request, service_post_id):
        try:
            post = ServicePost.objects.select_related('customer__user').get(id=service_post_id)
        except ServicePost.DoesNotExist:
            return Response({'detail': 'Service post not found'}, status=status.HTTP_404_NOT_FOUND)

        customer = post.customer
        user = customer.user

        # Delete the post
        post.delete()
        
        return Response({
            'detail': f'Post deleted. User has {customer.report_count} reports.'
        }, status=status.HTTP_200_OK)



class AdminServicePostReportDetailView(ListAPIView):
    serializer_class = ServicePostReportSerializer
    permission_classes = [IsAdmin, IsAuthenticated]

    def get_queryset(self):
        return Report.objects.filter(service_post_id=self.kwargs['service_post_id'])
    
class AdminServicePostSearchView(ListAPIView):
    serializer_class = ServicePostSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        return ServicePost.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query)
        )
