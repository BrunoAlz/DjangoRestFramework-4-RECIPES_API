from django.contrib.auth import (
    get_user_model,
    authenticate,
)
from django.utils.translation import gettext as _

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializador de dados para os Usuários."""

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """Cria e retorna o novo usuário com a senha encriptada"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Faz o updade e retorna o usuário"""

        """
        1 - Pega a senha do usuário que está vindo na requisição
        dentro do serializador, e exclui essa senha, assim a senha
        não será obrigatória no update, ou seja o usuário pode mudar
        só o nome.
        """
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        # 2 - Se o mandar a senha na requisição, faz o updade.
        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validate and authenticate the user."""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials.')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
