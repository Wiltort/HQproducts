from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from rest_framework import serializers

from users.models import Subscription

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователей."""

    class Meta:
        model = User
        fields = '__all__'


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор подписки."""
    user = serializers.ReadOnlyField(source='user.id')
    course = serializers.ReadOnlyField(source='course.id')
    remaining_balance = serializers.ReadOnlyField(source='user.balance.value')

    class Meta:
        model = Subscription
        fields = (
            'id', 'user', 'course', 'remaining_balance'
        )
