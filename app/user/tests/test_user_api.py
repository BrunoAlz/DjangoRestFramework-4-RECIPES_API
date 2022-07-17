"""
TESTES PARA A API DE USUÁRIOS
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


# Constante com o endpoint que será testado
CREATE_USER_URL = reverse('user:create')

def create_user(**params):
    """Cria e retorna um novo usuário"""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Testa a criação de usuário por um usuário Anônimo"""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Testa se a criação do usuário foi válida"""
        # Cria o payload com os dados que seão enviados para a URL
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test name'
        }
        # Manda um Post com os dados, para a URL
        res = self.client.post(CREATE_USER_URL, payload)

        # Verifica se o endpoint retorna o código correto
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # Consulta se o email passado na requisição post está salvo no BD
        user = get_user_model().objects.get(email=payload['email'])
        # se o user for criado, testaremos se a senha está correta
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        """Verifica se já existe um usuário com o email na base de dados"""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }
        create_user(**payload)
        # Está fazendo o Unpack na função que criada
        # anteriormente -> email=email, pass=pass, user=user...
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Verifica se algum erro é retornado no caso de a senha ser muito curta"""
        payload = {
            'email': 'test@example.com',
            'password': 'pw',
            'name': 'Test name',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # Verifica se o usuário com a senha curta foi criado, o resultado deve ser False
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        # Testa se o resultado é Falso
        self.assertFalse(user_exists)
