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
    http_method_names = ["get", "head", "options", "post"]
    permission_classes = (permissions.IsAdminUser,)

    @action(
        detail=True, methods=("post",),
        permission_classes=(permissions.IsAdminUser,)
    )
    def bonus(self, request, pk=None):
        """Зачисление бонуса пользователю"""
        user = get_object_or_404(User, id=pk)
        if "value" not in request.data.keys():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"details": "field 'value' required"},
            )
        try:
            value = int(request.data["value"])
        except ValueError:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"details": "field 'value' must be integer"},
            )
        if value <= 0:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"details":
                      "non positive numbers is not allowed for 'value'"},
            )
        balanse = get_object_or_404(Balance, user=user)
        balanse.value += value
        balanse.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
