from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)


RECIPES_URL = reverse('recipe:recipe-list')


# Função Helper para Acessar a URL de Detalhes
def detail_url(recipe_id):
    """Recebe o ID de uma receita e retorna a URL de Detalhes."""
    return reverse('recipe:recipe-detail', args=[recipe_id])


# Função helper para Criar Receitas
def create_recipe(user, **params):
    """Cria e retorna uma receita para testes"""

    # 1 - Criando o valores padrões para teste
    defaults = {
        'title': 'Titulo da Receita teste ',
        'time_minutes': 22,
        'price': Decimal('5.25'),
        'description': 'Descrição da receita de testes',
        'link': 'http://teste.com/receita.pdf',
    }
    """2 - Atualiza o Dicionário defaults com os dados recebidos
    nos params, se não vier dados usará os valores padrões"""
    defaults.update(params)

    # 3 - Cria a receita usando um usuário, e o dicionário defaults
    recipe = Recipe.objects.create(
        user=user,
        **defaults
    )
    return recipe


class PublicRecipeAPITests(TestCase):
    """Verifica as requisições de usuários não autenticados."""

    def setUp(self):
        # 1 - Cria um APIClient que simula as requisições
        self.client = APIClient()

    def test_auth_required(self):
        # 2 - Verifica se a autenticação é obrigatória para a requisição.
        res = self.client.get(RECIPES_URL)
        # 3 - Verifica o Status da Requisição
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Verifica as Requisições dos usuários Atutenticados."""

    def setUp(self):
        # 1 - Cria um APIClient que simula as requisições
        self.client = APIClient()
        # 2 - Cria um Usuário django, para ser usado nos testes
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123',
        )
        # 3 - Força a autenticação do Usuário
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Verifica se está recebendo uma lista de Receitas."""

        # 1 - Cria duas Receitas, com os dados padrões
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        # 2 - manda um GET na Url de Receitas
        res = self.client.get(RECIPES_URL)
        # 3 - Recupera todas as Receitas do BD
        recipes = Recipe.objects.all().order_by('-id')
        # 4 - Serializa os dados recuperados do BD
        serializer = RecipeSerializer(recipes, many=True)
        # 5 - Testa o Status da requisição
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # 6 - Verifica se os dados da Requisição são iguais do BD
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """Verifica se a listagem devolvida está restrita apenas
        ao usuário que realizou a solicitação dos dados
        ."""

        # 1 - Cria um Usuário django, para ser usado nos testes
        other_user = get_user_model().objects.create_user(
            'other@example.com',
            'password123',
        )
        """
        2 - Cria duas receitas:
            Uma por um usuário novo "other_user"
            Outra pelo usuário autenticado
        """
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        # 3 - manda um GET na Url de Receitas
        res = self.client.get(RECIPES_URL)
        """
        4 - Recupera as receitas do BD, filtrando o usuário, para que
        retorne apenas as receitas inseridas pelo usuário da requisição
        """
        recipes = Recipe.objects.filter(user=self.user)
        # 5 - Serializa os dados recuperados do BD
        serializer = RecipeSerializer(recipes, many=True)
        # 6 - Testa o Status da requisição
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # 7 - Verifica se os dados da Requisição são iguais do BD
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """Verifica se Está recuperando os detalhes de uma receita."""

        # 1 - Cria uma receita
        recipe = create_recipe(user=self.user)
        # 2 - Passa o ID da receita criada para a função helper
        url = detail_url(recipe.id)
        # 3 - Faz a requisição na URL de Details
        res = self.client.get(url)
        # 4 - Serializa os dados da Receita Criada
        serializer = RecipeDetailSerializer(recipe)
        # 7 - Verifica se os dados da Requisição são iguais do BD
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Verificar a Criação de uma Receita direto via API."""

        # 1 - Cria o Payload com os dados
        payload = {
            'title': 'Sample recipe',
            'time_minutes': 30,
            'price': Decimal('5.99'),
        }
        # 2 - Manda um POST para a url com os dados
        res = self.client.post(RECIPES_URL, payload)
        # 3 - Verifica o Status da Requisição
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # 4 - Recupera no banco a Receita criada
        recipe = Recipe.objects.get(id=res.data['id'])
        # 5 - Percorre da receita no Payload
        for k, v in payload.items():
            # 6 - Verifica se os dados do Banco são iguais aos dados do Payload
            self.assertEqual(getattr(recipe, k), v)
        # 7 - Verifica se o usuário da Receita é igual ao usuário Autenticado
        self.assertEqual(recipe.user, self.user)
