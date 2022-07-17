from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
)


class CreateUserView(generics.CreateAPIView):
    """Implementa a View genérica para criação dos Usuários"""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Implementa APIView para gerar o Token do usuário."""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Implementa APIView para Details e Update do user."""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Pega e retorna o usuário autenticado, quando a
        a requisição for GET"""
        return self.request.user
