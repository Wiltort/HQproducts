from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from api.v1.permissions import IsStudentOrIsAdmin, ReadOnlyOrIsAdmin
from api.v1.serializers.course_serializer import (
    CourseSerializer,
    CreateCourseSerializer,
    CreateGroupSerializer,
    CreateLessonSerializer,
    GroupSerializer,
    LessonSerializer,
)
from api.v1.serializers.user_serializer import SubscriptionSerializer
from courses.models import Course
from users.models import Subscription, Balance


class LessonViewSet(viewsets.ModelViewSet):
    """Уроки."""

    permission_classes = (IsStudentOrIsAdmin,)

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return LessonSerializer
        return CreateLessonSerializer

    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs.get("course_id"))
        serializer.save(course=course)

    def get_queryset(self):
        course = get_object_or_404(Course, id=self.kwargs.get("course_id"))
        return course.lessons.all()


class GroupViewSet(viewsets.ModelViewSet):
    """Группы."""

    permission_classes = (permissions.IsAdminUser,)

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return GroupSerializer
        return CreateGroupSerializer

    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs.get("course_id"))
        serializer.save(course=course)

    def get_queryset(self):
        course = get_object_or_404(Course, id=self.kwargs.get("course_id"))
        return course.groups.all()


class CourseViewSet(viewsets.ModelViewSet):
    """Курсы"""

    queryset = Course.objects.all()
    permission_classes = (ReadOnlyOrIsAdmin,)

    def get_queryset(self):
        queryset = super(CourseViewSet, self).get_queryset()
        user = self.request.user
        if not user or not user.is_authenticated:
            return queryset
        queryset = queryset.exclude(subscribers__user=user)
        return queryset

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return CourseSerializer
        return CreateCourseSerializer

    @action(
        methods=["post"],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def pay(self, request, pk):
        """Покупка доступа к курсу (подписка на курс)."""
        user = request.user
        try:
            balance = Balance.objects.get(user=user)
        except ObjectDoesNotExist:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"details": "Balance not found"},
            )
        course = get_object_or_404(Course, id=pk)
        if balance.value >= course.price:
            if Subscription.objects.filter(user=user, course=course).exists():
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={"details": "Subscription exists"},
                )
            new_subscription = Subscription.objects.create(user=user,
                                                           course=course)
            balance.value -= course.price
            balance.save()
            serializer = SubscriptionSerializer(new_subscription)
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"details": "The balance is not sufficient"},
            )
