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
        user_type = request.data.get('user_type')
        
        if user_type == 'professional':
            serializer_class = ProfessionalProfileSerializer
        elif user_type == 'customer':
            serializer_class = CustomerProfileSerializer
        elif user_type == 'admin':
            serializer_class = AdminProfileSerializer
        else:
            return Response({'error': 'Invalid user type'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            #send email verification
            send_email_confirmation(request, user)
            
            return Response({'message': 'Registration successful. please check your email to verify your account',
                             'data':serializer.data}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
