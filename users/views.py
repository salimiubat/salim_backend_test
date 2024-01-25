# views.py
from rest_framework import generics, permissions
from rest_framework import viewsets,status
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import *
from .models import User
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password, make_password



class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer




class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    def get_permissions(self):
        if self.action == 'create':
            return []
        return [permissions.IsAuthenticated()] 
    
    def create(self, request, *args, **kwargs):
        role = request.data.get("role")
        serializer = CustomUserSerializer(data=request.data)

        if role != 'OWNER':
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message': 'Employee has been created '}, status=status.HTTP_201_CREATED)
        else:

            request.data['is_staff'] = True
            request.data['is_superuser'] = True

            serializer.is_valid(raise_exception=True)

            serializer.save()

        return Response({'message': 'Owner and Superuser created successfully'}, status=status.HTTP_201_CREATED)
    