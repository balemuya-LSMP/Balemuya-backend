from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import Notification
from .serializers import NotificationSerializer

# Create your views here.
           
class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
            data = NotificationSerializer(notifications, many=True).data
        except Notification.DoesNotExist:
            return Response({"error": "No notifications found."}, status=404)
        notification_count = len(notifications)
        return Response({'notifications': data, 'notification_count': notification_count},status = status.HTTP_200_OK)
    

class MarkNotificationAsReadView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, recipient=request.user)
        except Notification.DoesNotExist:
            return Response({"error": "Notification not found."}, status=404)
        
        notification.is_read = True
        notification.save()
        return Response({"message": "Notification marked as read."})

class MarkAllNotificationAsReadView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        notifications = Notification.objects.filter(recipient=request.user, is_read=False)
        notifications.update(is_read=True)
        return Response({"message": "All notifications marked as read."},status=status.HTTP_200_OK)