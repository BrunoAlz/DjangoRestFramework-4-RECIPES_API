from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe
from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """ModelViewSet para receitas."""
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """ Recupera os dados baseado no usuário autenticado """
        return self.queryset.filter(
            user=self.request.user
            ).order_by('-id')

    def get_serializer_class(self):
        """ Retorna o serializador básico, sem os detalhes se
        a ação na requisição for list, do contrário retorna o
        serializador com os detalhes
        """
        if self.action == 'list':
            return serializers.RecipeSerializer

        return self.serializer_class
        """ Documentação da func => get_serializer_class
            https://www.django-rest-framework.org/api-guide/
            generic-views/#get_serializer_classself
        """

    def perform_create(self, serializer):
        """ Recepe os dados da Requisição e Cria a Receita."""
        serializer.save(user=self.request.user)
