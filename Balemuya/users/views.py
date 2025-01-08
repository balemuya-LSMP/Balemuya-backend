from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .serializers import ProfessionalProfileSerializer

class ProfessionalRegisterView(generics.CreateAPIView):
    pass
    # serializer_class = ProfessionalSerializer

    # def post(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     user = self.perform_create(serializer)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)

    # def perform_create(self, serializer):
    #     return serializer.save()