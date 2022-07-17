"""
Tests for models.
"""
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Teste para verificar a criação de Usuário com email"""
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Teste para verificar a normalização do Email"""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TESTE3@EXAMPLE.COM', 'TESTE3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Teste para verificar a criação do usuário sem email"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """Teste para verificar a criação do superuser."""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_creat_recipe(self):
        """ Verifica se a criação da Receita funciona corretamente """

        # 1 - Criaremos o Usuário que ira criar as receitas
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123'
        )

        # 2 - Criaremos a receita e passaremos o usuário acima.
        recipe = models.Recipe.objects.create(
            user=user,
            title='Test recipe name',
            time_minutes=5,
            price=Decimal('5.50'),
            description='Criando um Teste de uma receita',
        )

        self.assertEqual(str(recipe), recipe.title)
