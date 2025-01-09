from rest_framework import generics
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from allauth.account.utils import send_email_confirmation
from allauth.account.models import get_adapter

from .serializers import ProfessionalProfileSerializer,CustomerProfileSerializer,AdminProfileSerializer
class RegisterView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    
    def create(self, request, *args, **kwargs):
        user = request.data.get('user')
        
        if user['user_type'] == 'professional':
            serializer_class = ProfessionalProfileSerializer
        elif user['user_type'] == 'customer':
            serializer_class = CustomerProfileSerializer
        elif user['user_type'] == 'admin':
            serializer_class = AdminProfileSerializer
        else:
            return Response({'error': 'Invalid user type'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = serializer_class(data=request.data)
        if serializer.is_valid():
            user_instance = serializer.save()
            # Send email verification
            send_email_confirmation(request, user_instance.user)
            print('serialized data',serializer.data)
            return Response({
                'message': 'Registration successful. Please check your email to verify your account.',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)