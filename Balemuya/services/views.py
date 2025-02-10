from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import ServicePost, ServicePostApplication, ServiceBooking, Review, Complain
from common.models import Category
from common.serializers import CategorySerializer
from .serializers import ServicePostSerializer, ServicePostApplicationSerializer, ServiceBookingSerializer, ReviewSerializer, ComplainSerializer
from users.models import Professional, Customer
from django.utils import timezone

class CategoryListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            categories = Category.objects.all()
        except Category.DoesNotExist:
            return Response({"detail": "Categories not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ServicePostListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        status_param = request.query_params.get('status', 'active')
        
        if request.user.user_type == 'customer':
            service_posts = ServicePost.objects.filter(
                customer=request.user.customer, status=status_param
            ).order_by('-created_at')

        elif request.user.user_type == 'professional':
            service_posts = ServicePost.objects.filter(
                category__in=request.user.professional.categories.all(),
                status=status_param,
                work_due_date__lte=timezone.now(),
            ).order_by('-created_at')

        elif request.user.user_type == 'admin':
            service_posts = ServicePost.objects.all().order_by('-created_at')

        else:
            return Response({"detail": "Invalid user type."}, status=status.HTTP_403_FORBIDDEN)

        if not service_posts.exists():
            return Response({"detail": "No service posts found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ServicePostSerializer(service_posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        
        if request.user.user_type !='customer':
            return Response({'message':'you are not allowd to post!'},status=status.HTTP_400_BAD_REQUEST)
        
        posted_data = {
            'customer_id':request.user.customer.id,
            **request.data
        }
        serializer = ServicePostSerializer(data=posted_data,context={'request':request})
        if serializer.is_valid():
            serializer.save() 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ServicePostDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return ServicePost.objects.get(id=pk)
        except ServicePost.DoesNotExist:
            return None

    def get(self, request, pk):
        service_post = self.get_object(pk)
        if not service_post:
            return Response({"detail": "ServicePost not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ServicePostSerializer(service_post)
        return Response(serializer.data)

    def put(self, request, pk):
        service_post = self.get_object(pk)
        if not service_post:
            return Response({"detail": "ServicePost not found."}, status=status.HTTP_404_NOT_FOUND)

        if service_post.customer != request.user.customer:
            return Response({"detail": "You are not authorized to update this post."}, status=status.HTTP_403_FORBIDDEN)

        serializer = ServicePostSerializer(service_post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        service_post = self.get_object(pk)
        if not service_post:
            return Response({"detail": "ServicePost not found."}, status=status.HTTP_404_NOT_FOUND)

        service_post.delete()
        
        return Response({"message": "Post deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)


class CreateServicePostApplicationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, service_id=None):
        if request.user.user_type != "professional":
            return Response({"detail": "Only professionals can apply for service posts."}, status=status.HTTP_403_FORBIDDEN)

        try:
            service_id = request.data.get('service_id')
            service_post = ServicePost.objects.get(id=service_id)
            print('service id get from frontend',service_post)
        except ServicePost.DoesNotExist:
            return Response({"detail": "ServicePost not found."}, status=status.HTTP_404_NOT_FOUND)
        professional_id = request.user.professional.id
        print('professional id is ',professional_id)
        application_data = {
            'service_id':service_post,
            'professional_id':request.user.professional.id,
            **request.data
        }
        serializer = ServicePostApplicationSerializer(data=application_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListServicePostApplicationsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, service_id=None):
        status_param = request.query_params.get('status', 'pending')
        applications = ServicePostApplication.objects.filter(service=service_id, status=status_param)

        if request.user.user_type == "professional":
            applications = applications.filter(professional=request.user.professional, status=status_param).order_by('-created_at')
        elif request.user.user_type == "customer":
            applications = applications.order_by('-created_at')

        if not applications.exists():
            return Response({"detail": "No applications found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ServicePostApplicationSerializer(applications, many=True)
        data = list(serializer.data)
        return Response({"message": "success", "data": data}, status=status.HTTP_200_OK)


class DetailServicePostApplicationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        try:
            application = ServicePostApplication.objects.get(id=pk)
        except ServicePostApplication.DoesNotExist:
            return Response({"detail": "Application not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ServicePostApplicationSerializer(application)
        return Response(serializer.data)


class AcceptServicePostApplicationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk=None):
        try:
            accepted_application = ServicePostApplication.objects.get(id=pk)
        except ServicePostApplication.DoesNotExist:
            return Response({"detail": "Application not found."}, status=status.HTTP_404_NOT_FOUND)

        accepted_application.status = 'accepted'
        accepted_application.save()

        # Reject all other applications for the same service
        ServicePostApplication.objects.filter(service=accepted_application.service, status='pending').exclude(id=pk).update(status='rejected')

        # Create a booking for the accepted application
        booking = ServiceBooking.objects.create(
            application=accepted_application,
            scheduled_date=accepted_application.service.work_due_date,
            status='pending'
        )
        booking.save()

        # Update the service post status
        accepted_application.service.status = 'booked'
        accepted_application.service.save()

        return Response({"detail": "Application accepted, others rejected."}, status=status.HTTP_200_OK)


class ServiceBookingListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        status_param = request.query_params.get('status', None)
        try:
            if request.user.user_type == "professional":
                bookings = ServiceBooking.objects.filter(status=status_param, application__professional=request.user.professional).order_by('-created_at')
            elif request.user.user_type == "customer":
                bookings = ServiceBooking.objects.filter(status=status_param, application__service__customer=request.user.customer).order_by('-created_at')
        except ServiceBooking.DoesNotExist:
            return Response({"detail": "Bookings not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ServiceBookingSerializer(bookings, many=True)
        return Response({'message': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)


class ServiceBookingRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        try:
            booking = ServiceBooking.objects.get(id=pk)
            serializer = ServiceBookingSerializer(booking)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ServiceBooking.DoesNotExist:
            return Response({"detail": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)


class CompleteBookingAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk=None):
        try:
            booking = ServiceBooking.objects.get(id=pk)
        except ServiceBooking.DoesNotExist:
            return Response({"detail": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)
        if booking.status =='pending':
            booking.status ='completed'
            booking.save()
            
            booking.application.service.status='completed'
            booking.application.service.save()
            return Response({"detail": "Booking completed."}, status=status.HTTP_404_NOT_FOUND)
        else:
             return Response({'error':'there is no pending booking to be completed'}, status=status.HTTP_400_BAD_REQUEST)


class ServiceBookingDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk=None):
        try:
            booking = ServiceBooking.objects.get(id=pk,status='completed')
        except ServiceBooking.DoesNotExist:
            return Response({"detail": "Booking not completed can't be deleted."}, status=status.HTTP_404_NOT_FOUND)

        booking.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CancelServiceBookingAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id=None):
        try:
            booking = ServiceBooking.objects.get(id=booking_id,status='pending')
        except ServiceBooking.DoesNotExist:
            return Response({"detail": "no active booking found."}, status=status.HTTP_404_NOT_FOUND)

        booking.status = 'canceled'
        booking.save()
        
        booking.application.status = 'rejected'
        booking.application.save()
        
        booking.application.service.status = 'canceled'
        booking.application.service.save()
        
        return Response({"detail": "Booking cancelled successfully."}, status=status.HTTP_200_OK)



class ReviewBookingAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        booking_id = kwargs.get('booking_id')
        try:
            booking = ServiceBooking.objects.get(id=booking_id)
        except ServiceBooking.DoesNotExist:
            return Response({"error": "No booking found"}, status=status.HTTP_404_NOT_FOUND)

        review,created = Review.objects.get_or_create(booking=booking, user=user)
        if not created:
            return Response({"error": "Review already exists"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ReviewSerializer(instance=booking, data=request.data, user=request.user)
        if serializer.is_valid():
            serializer.save()
            if request.user.user_type == "customer":
                booking.application.professional.rating = (booking.application.professional.rating + serializer.validated_data['rating']) / 2
                booking.application.professional.save()
            if request.user.user_type == "professional":
                booking.application.service.customer.rating = (booking.application.service.customer.rating + serializer.validated_data['rating']) / 2
                booking.application.service.customer.save()

            return Response({"success": "Review added."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ComplainBookingAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        booking_id = kwargs.get('booking_id')
        try:
            booking = ServiceBooking.objects.get(id=booking_id)
        except ServiceBooking.DoesNotExist:
            return Response({"error": "No booking found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ComplainSerializer(data=request.data, context={'request': request, 'booking': booking})
        if serializer.is_valid():
            serializer.save()
            return Response({"success": "Complain added."}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
