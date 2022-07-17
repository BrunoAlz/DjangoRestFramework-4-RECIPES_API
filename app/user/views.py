from rest_framework import generics
from user.serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    """Implementa a View genérica para criação dos Usuários"""
    serializer_class = UserSerializer
