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
from django.db import transaction


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
        except ServicePost.DoesNotExist:
            return Response({"message": "ServicePost not found."}, status=status.HTTP_404_NOT_FOUND)
        if request.user.professional.is_available==False:
            return Response({"message": "Please subscribe for requests."}, status=status.HTTP_400_BAD_REQUEST)
        elif request.user.professional.num_of_request==0:
            return Response({"message": "You have no  coins to apply  Job."}, status=status.HTTP_400_BAD_REQUEST)
        
       
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
            request.user.professional.num_of_request -= 1
            request.user.professional.save()
            
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
            application = ServicePostApplication.objects.get(id=pk)
        except ServicePostApplication.DoesNotExist:
            return Response({"detail": "Application not found."}, status=status.HTTP_404_NOT_FOUND)
        
        if not application.service:
            return Response({"error": "service not  not found."}, status=status.HTTP_404_NOT_FOUND)

        if application.status == 'accepted':
            return Response({'error': "User already accepted"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                application.status = 'accepted'
                application.save()

                ServicePostApplication.objects.filter(service=application.service, status='pending').exclude(id=pk).update(status='rejected')

                booking = ServiceBooking.objects.create(
                    application=application,
                    scheduled_date=application.service.work_due_date,
                    status='pending'
                )
                
                application.service.status = 'booked'
                application.service.save()

                return Response({"detail": "Application accepted, others rejected."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "An error occurred while processing your request"}, status=500)

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

    def post(self, request, booking_id=None):
        try:
            booking = ServiceBooking.objects.get(id=booking_id)
        except ServiceBooking.DoesNotExist:
            return Response({"detail": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)

        if booking.status != 'pending':
            return Response({"detail": "Booking must be pending to be completed."}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        if user != booking.application.service.customer.user and user != booking.application.professional.user:
            return Response({"detail": "You do not have permission to complete this booking."}, status=status.HTTP_403_FORBIDDEN)

        booking.status = 'completed'
        booking.application.service.status = 'completed'
        booking.application.service.save()
        booking.save()
        
        serializer = ServiceBookingSerializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    

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
        
        try:
            with transaction.atomic():
                booking.status = 'canceled'
                booking.save()
                
                booking.application.status = 'rejected'
                booking.application.save()
                
                booking.application.service.status = 'canceled'
                booking.application.service.save()
                
                return Response({"detail": "Booking cancelled successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": "erorr in canceling ."}, status=500)



class ReviewAPIView(APIView):
    def post(self, request, *args, **kwargs):
        user = request.user
        booking = request.data.get('booking')
        service_request = request.data.get('service_request')

        if booking and service_request:
            return Response({"error": "Please provide either a ServiceBooking or a ServiceRequest, not both."}, status=status.HTTP_400_BAD_REQUEST)

        if booking:
            try:
                booking_instance = ServiceBooking.objects.get(id=booking)
            except ServiceBooking.DoesNotExist:
                return Response({"error": "No booking found"}, status=status.HTTP_404_NOT_FOUND)

            if Review.objects.filter(booking=booking_instance, user=user).exists():
                return Response({"error": "Review already exists for this booking"}, status=status.HTTP_400_BAD_REQUEST)

            review_data = {
                "booking": booking_instance.id,
                "user": user.id,
                **request.data,
            }

        elif service_request:
            try:
                request_instance = ServiceRequest.objects.get(id=service_request)
            except ServiceRequest.DoesNotExist:
                return Response({"error": "No service request found"}, status=status.HTTP_404_NOT_FOUND)

            if Review.objects.filter(service_request=request_instance, user=user).exists():
                return Response({"error": "Review already exists for this service request"}, status=status.HTTP_400_BAD_REQUEST)

            review_data = {
                "service_request": request_instance.id,
                "user": user.id,
                **request.data,
            }

        else:
            return Response({"error": "Please provide either a ServiceBooking or a ServiceRequest."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ReviewSerializer(data=review_data)
        if serializer.is_valid():
            serializer.save()

            if user.user_type == "customer":
                if booking:
                    booking_instance.application.professional.rating = (
                        (booking_instance.application.professional.rating + serializer.validated_data['rating']) / 2
                    )
                    booking_instance.application.professional.save()
                else:
                    request_instance.professional.rating = (
                        (request_instance.professional.rating + serializer.validated_data['rating']) / 2
                    )
                    request_instance.professional.save()
            elif user.user_type == "professional":
                if booking:
                    booking_instance.application.service.customer.rating = (
                        (booking_instance.application.service.customer.rating + serializer.validated_data['rating']) / 2
                    )
                    booking_instance.application.service.customer.save()
                else:
                    request_instance.customer.rating = (
                        (request_instance.customer.rating + serializer.validated_data['rating']) / 2
                    )
                    request_instance.customer.save()

            return Response({"success": "Review added."}, status=status.HTTP_200_OK)
        else:
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ComplainAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user        
        booking = request.data.get('booking') 
        service_request = request.data.get('service_request')

        if booking and service_request:
            return Response({"error": "Please provide either a ServiceBooking or a ServiceRequest, not both."}, status=status.HTTP_400_BAD_REQUEST)

        if booking:
            try:
                booking_instance = ServiceBooking.objects.get(id=booking)
            except ServiceBooking.DoesNotExist:
                return Response({"error": "No booking found"}, status=status.HTTP_404_NOT_FOUND)

            if booking_instance.application.service.customer.user != user and booking_instance.application.professional.user != user:
                return Response({'error': 'You cannot complain about this booking.'}, status=status.HTTP_400_BAD_REQUEST)

            if Complain.objects.filter(booking=booking_instance, user=user).exists():
                return Response({'error': 'You have already reported this booking.'}, status=status.HTTP_400_BAD_REQUEST)

            complain_data = {
                'booking': booking_instance.id,
                'user': user.id,
                **request.data,
            }

        elif service_request:
            try:
                request_instance = ServiceRequest.objects.get(id=service_request)
            except ServiceRequest.DoesNotExist:
                return Response({"error": "No service request found"}, status=status.HTTP_404_NOT_FOUND)

            if request_instance.customer.user != user:
                return Response({'error': 'You cannot complain about this service request.'}, status=status.HTTP_400_BAD_REQUEST)

            if Complain.objects.filter(service_request=request_instance, user=user).exists():
                return Response({'error': 'You have already reported this service request.'}, status=status.HTTP_400_BAD_REQUEST)

            complain_data = {
                'service_request': request_instance.id,
                'user': user.id,
                **request.data,
            }

        else:
            return Response({"error": "Please provide either a ServiceBooking or a ServiceRequest."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ComplainSerializer(data=complain_data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": "Complaint added."}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)