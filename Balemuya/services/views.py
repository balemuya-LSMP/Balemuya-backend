from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import ServicePost, ServicePostApplication, ServiceBooking,Review,Complain
from common.models import Category
from common.serializers import CategorySerializer
from .serializers import ServicePostSerializer,ServicePostApplicationSerializer,ServiceBookingSerializer,ComplainSerializer,ServiceBookingSerializer
from users.models import Professional, Customer

from django.http import JsonResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync



class CategoryListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            categories = Category.objects.all()
        except Category.DoesNotExist:
            return Response({"detail": "Categories not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
class ServicePostAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        service_posts = []
        if pk:
            try:
                service_post = ServicePost.objects.get(id=pk)
                serializer = ServicePostSerializer(service_post)
                return Response(serializer.data)
            except ServicePost.DoesNotExist:
                return Response({"detail": "ServicePost not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            if request.user.user_type =='customer':
                service_posts = ServicePost.objects.filter(customer=request.user.customer).order_by('-created_at')
            elif request.user.user_type =='professional':
                service_posts = ServicePost.objects.filter(category__in=request.user.professional.categories.all()).order_by('-created_at')
            elif request.user.user_type =='admin':
                service_posts = ServicePost.objects.all().order_by('-created_at')
                
            if not service_posts:
                return Response({"detail": "No service posts found."}, status=status.HTTP_404_NOT_FOUND)
            serializer = ServicePostSerializer(service_posts, many=True)
            return Response(serializer.data)

    def post(self, request):
        if request.user.user_type != "customer":
            return Response({"detail": "Only customers can create service posts."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ServicePostSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            service_post = serializer.save(customer=request.user.customer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        try:
            service_post = ServicePost.objects.get(id=pk, customer=request.user.customer)
        except ServicePost.DoesNotExist:
            return Response({"detail": "ServicePost not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ServicePostSerializer(service_post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        try:
            service_post = ServicePost.objects.get(id=pk)
        except ServicePost.DoesNotExist:
            return Response({"detail": "ServicePost not found."}, status=status.HTTP_404_NOT_FOUND)

        service_post.delete()
        return Response({"message":"post deleted successfully!"},status=status.HTTP_204_NO_CONTENT)

class ServicePostApplicationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request,service_id=None ,pk=None):
        if pk:
            try:
                application = ServicePostApplication.objects.get(id=pk)
                serializer = ServicePostApplicationSerializer(application)
                return Response(serializer.data)
            except ServicePostApplication.DoesNotExist:
                return Response({"detail": "Application not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            applications = ServicePostApplication.objects.filter(service=service_id)
            if request.user.user_type == "professional":
                applications = applications.filter(professional=request.user.professional)
            elif request.user.user_type == "customer":
                applications = applications.order_by('-created_at')
            if not applications:
                return Response({"detail": "No applications found."}, status=status.HTTP_404_NOT_FOUND)
            serializer = ServicePostApplicationSerializer(applications, many=True)
            return Response({"message":"success","data":serializer.data},status=status.HTTP_200_OK) 

    def post(self, request,service_id=None):
        if request.user.user_type != "professional":
            return Response({"detail": "Only professionals can apply for service posts."}, status=status.HTTP_403_FORBIDDEN)
        try:
           service_id = request.data.get('service_id')
           print('service id is',service_id)
           service_post = ServicePost.objects.get(id=service_id)
        except ServicePost.DoesNotExist as e:
            print('error is',str(e))
            return Response({"detail": "ServicePost not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ServicePostApplicationSerializer(data=request.data, context={'request': request,'service':service_post})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        try:
            application = ServicePostApplication.objects.get(id=pk)
        except ServicePostApplication.DoesNotExist:
            return Response({"detail": "Application not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ServicePostApplicationSerializer(application, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        try:
            application = ServicePostApplication.objects.get(id=pk)
        except ServicePostApplication.DoesNotExist:
            return Response({"detail": "Application not found."}, status=status.HTTP_404_NOT_FOUND)
        
        application.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    

class ServiceBookingAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk=None):
        if pk:
            try:
                booking = ServiceBooking.objects.get(id=pk)
                serializer = ServiceBookingSerializer(booking)
                return Response(serializer.data)
            except ServiceBooking.DoesNotExist:
                return Response({"detail": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            bookings = ServiceBooking.objects.all()
            serializer = ServiceBookingSerializer(bookings, many=True)
            return Response(serializer.data)

    def post(self, request):
        application_id = request.data.get('service_post_application')
        try:
            application = ServicePostApplication.objects.get(id=application_id)
        except ServicePostApplication.DoesNotExist:
            return Response({"detail": "Application not found."}, status=status.HTTP_404_NOT_FOUND)
        
        if application.status != 'accepted':
            return Response({"detail": "Only accepted applications can be booked."}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ServiceBookingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(service_post_application=application, professional=application.professional)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        try:
            booking = ServiceBooking.objects.get(id=pk)
        except ServiceBooking.DoesNotExist:
            return Response({"detail": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ServiceBookingSerializer(booking, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        try:
            booking = ServiceBooking.objects.get(id=pk)
        except ServiceBooking.DoesNotExist:
            return Response({"detail": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)
        
        booking.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class ReviewBookingAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        user = request.user
        booking_id = kwargs.get('booking_id')
        try:
            booking = ServiceBooking.objects.get(id=booking_id)
            
        except ServiceBooking.DoesNotExist:
            return Response({"error":"no booking found"},status=status.HTTP_404_NOT_FOUND)
        review,created = Review.objects.get_or_create(booking=booking,user=user)
        if not created:
            return Response({"error":"Review already exists"},status=status.HTTP_400_BAD_REQUEST)
        serializer = ReviewBookingSerializer(data=request.data,booking=booking,user=request.user)
        if serializer.is_valid():
            serializer.save()
            if request.user.user_type == "customer":
                booking.application.professional.rating = (booking.application.professional.rating + serializer.validated_data['rating'])/2
                booking.application.professional.save()
            if  request.user.user_type == "professional":
                booking.application.service.customer.rating = (booking.application.service.customer.rating + serializer.validated_data['rating'])/2
                booking.application.service.customer.save()
            return Response({'message':'Review created'},serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, *args, **kwargs):
        user = request.user
        booking_id = kwargs.get('booking_id')
        try:
            booking = ServiceBooking.objects.get(id=booking_id)
        except ServiceBooking.DoesNotExist:
            return Response({"error":"no booking found"},status=status.HTTP_404_NOT_FOUND)
        review = Review.objects.get(booking=booking,user=user)
        review.comment = request.data.get('comment')
        serializer = ReviewBookingSerializer(review)
        if serializer.is_valid():
            return Response({"message":"Review updated"},serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request, *args, **kwargs):
        user = request.user
        booking_id = kwargs.get('booking_id')
        try:
            booking = ServiceBooking.objects.get(id=booking_id)
        except ServiceBooking.DoesNotExist:
            return Response({"error":"no booking found"},status=status.HTTP_404_NOT_FOUND)
        try:
            review = Review.objects.get(booking=booking,user=user)
        except Review.DoesNotExist:
            return Response({"error":"no review found"},status=status.HTTP_404_NOT_FOUND)
        review.delete()
        return Response({"message":"Review deleted successfully"},status=status.HTTP_204_NO_CONTENT)
    
class ComplainBookingAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        user = request.user
        booking_id = kwargs.get('booking_id')
        try:
            booking = ServiceBooking.objects.get(id=booking_id)
            
        except ServiceBooking.DoesNotExist:
            return Response({"error":"no booking found"},status=status.HTTP_404_NOT_FOUND)
        complain,created = Complain.objects.get_or_create(booking=booking,user=user)
        if not created:
            return Response({"error":"Complain already exists"},status=status.HTTP_400_BAD_REQUEST)
        serializer = ComplainBookingSerializer(data=request.data,booking=booking,user=request.user)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, *args, **kwargs):
        user = request.user
        booking_id = kwargs.get('booking_id')
        try:
            booking = ServiceBooking.objects.get(id=booking_id)
        except ServiceBooking.DoesNotExist:
            return Response({"error":"no booking found"},status=status.HTTP_404_NOT_FOUND)
        complain = Complain.objects.get(booking=booking,user=user)
        serializer = ComplainBookingSerializer(complain,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, *args, **kwargs):
        user = request.user
        booking_id = kwargs.get('booking_id')
        try:
            booking = ServiceBooking.objects.get(id=booking_id)
        except ServiceBooking.DoesNotExist:
            return Response({"error":"no booking found"},status=status.HTTP_404_NOT_FOUND)
        complain = Complain.objects.get(booking=booking,user=user)
        complain.delete()
        return Response({"message":"Complain deleted successfully"},status=status.HTTP_204_NO_CONTENT)