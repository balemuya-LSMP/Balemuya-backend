from customAdmin.packages import *

from .serializers import ProfessionalListSerializer,CustomerListSerializer

class UserListView(APIView):
    permission_classes = [IsAdmin,IsAuthenticated]

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class UserCreateView(APIView):
    permission_classes = [IsAdmin,IsAuthenticated]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            
            user = serializer.instance
            user.is_active= True
            user.is_phone_verified = True
            user.is_email_verified = True
            user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailView(APIView):
    permission_classes = [IsAdmin,IsAuthenticated]
    
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        user.delete()
        return Response({'detail': 'User deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)

class UserBlockView(APIView):
    permission_classes = [IsAdmin,IsAuthenticated]

    def patch(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        is_blocked = request.data.get('is_blocked', None)
        if is_blocked is None:
            return Response({'detail': 'is_blocked field is required'}, status=status.HTTP_400_BAD_REQUEST)

        user.is_blocked = is_blocked
        user.save()
        return Response({'detail': f'User {"blocked" if is_blocked else "unblocked"} successfully.'}, status=status.HTTP_200_OK)



class ProfessionalListView(generics.ListAPIView):
    permission_classes = [IsAdmin,IsAuthenticated]
    serializer_class = ProfessionalListSerializer

    def get_queryset(self):
        if self.request.user.user_type != 'admin':
            raise PermissionDenied("You are not authorized to access this.")
        
        queryset = Professional.objects.all()
        status_filter = self.request.query_params.get('status', None)

        if status_filter:
            if status_filter == 'active':
                queryset = queryset.filter(user__is_active=True)
            elif status_filter == 'verified':
                queryset = queryset.filter(is_verified=True)
            elif status_filter == 'available':
                queryset = queryset.filter(is_available=True)
            elif status_filter == 'blocked':
                queryset = queryset.filter(user__is_blocked=True)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        status_filter = self.request.query_params.get('status', None)

        if not queryset.exists():
            if status_filter is None:
                status_filter = ''
            return Response({"message": f"No {status_filter} professionals found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)




class CustomerListView(generics.ListAPIView):
    permission_classes = [IsAdmin,IsAuthenticated]
    serializer_class = CustomerListSerializer

    def get_queryset(self):
        if self.request.user.user_type != 'admin':
            raise PermissionDenied("You are not authorized to access this.")
        
        queryset = Customer.objects.all()
        status_filter = self.request.query_params.get('status', None)

        if status_filter:
            if status_filter == 'active':
                queryset = queryset.filter(user__is_active=True)
            elif status_filter == 'blocked':
                queryset = queryset.filter(user__is_blocked=True)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        status_filter = self.request.query_params.get('status', None)

        if not queryset.exists():
            if status_filter ==None:
                status_filter = ''
            return Response({"message": f"No {status_filter} customers found."}, status=404)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class AdminListView(generics.ListAPIView):
    permission_classes = [IsAdmin,IsAuthenticated]
    serializer_class = AdminSerializer

    def get_queryset(self):
        if self.request.user.user_type != 'admin':
            raise PermissionDenied({"message":
                "You are not authorized to access this."})
        queryset = Admin.objects.all()
        status_filter = self.request.query_params.get('status', None)

        if status_filter:
            if status_filter == 'active':
                queryset = queryset.filter(user__is_active=True)
            elif status_filter == 'blocked':
                queryset = queryset.filter(user__is_blocked=True)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        status_filter = self.request.query_params.get('status', None)

        if not queryset.exists():
            if status_filter ==None:
                status_filter = ''
            return Response({"message": f"No {status_filter} Admin found."}, status=404)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    
    
class AdminVerifyProfessionalView(APIView):
    permission_classes = [IsAdmin,IsAuthenticated]

    def put(self, request, ver_req_id):
        if not request.user.user_type == 'admin':
            return Response({"error": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)

        try:
            verification_request = VerificationRequest.objects.get(id=ver_req_id)
        except VerificationRequest.DoesNotExist:
            return Response({"error": "Verification request not found."}, status=status.HTTP_404_NOT_FOUND)

        if verification_request.status != "pending":
            return Response({"error": "This request has already been processed."}, status=status.HTTP_400_BAD_REQUEST)

        action = request.data.get("action")
        admin_comment = request.data.get("admin_comment", "")

        if action not in ["approved", "rejected"]:
            return Response({"error": "Invalid action. Must be 'approved' or 'rejected'."}, status=status.HTTP_400_BAD_REQUEST)

        # Update the verification request
        verification_request.status = action
        verification_request.admin_comment = admin_comment
        verification_request.verified_by = request.user.admin 
        verification_request.save()
        
        if verification_request.status == "approved":
            professional = verification_request.professional
            professional.is_verified = True
            professional.save()
            
            subject = "Verification Approved"
            message = "Congratulations! Your verification request has been approved by the admin."
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [professional.user.email]
            send_mail(subject, message, email_from, recipient_list)

        elif verification_request.status == "rejected":
            subject = "Verification Rejected"
            message = f"Your verification request has been rejected by the admin. Reason: {admin_comment}"
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [verification_request.professional.user.email]
            send_mail(subject, message, email_from, recipient_list)
            # send_push_notification(verification_request.professional.user, f"Your verification request has been rejected by the admin. Reason: {admin_comment}")
            
        serializer = VerificationRequestSerializer(verification_request)
        return Response({"message": f"Request successfully {action}.", "data": serializer.data}, status=status.HTTP_200_OK)
    
class ProfessionalVerificationRequestListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.user_type == 'admin':
            return Response({"error": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        try:
            verification_requests = VerificationRequest.objects.filter(status='pending')
        except VerificationRequest.DoesNotExist:
            return Response({"error": "Verification request not found."}, status=status.HTTP_404_NOT_FOUND)
        
        if verification_requests.count() == 0:
            return Response({"error": "No verification requests found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = VerificationRequestSerializer(verification_requests, many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)
    
    