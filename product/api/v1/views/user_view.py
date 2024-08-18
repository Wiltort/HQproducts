from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import Balance

from api.v1.serializers.user_serializer import CustomUserSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    http_method_names = ["get", "head", "options"]
    permission_classes = (permissions.IsAdminUser,)

    @action(
        detail=True,
        methods=('post'),
        permission_classes=permissions.IsAdminUser
        )
    def bonus(self, request, pk=None):
        user = get_object_or_404(User, id=pk)
        value = request.data['value']
        balanse = get_object_or_404(Balance, user=user)
        balanse.value += value
        balanse.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
