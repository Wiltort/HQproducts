from django.db.models import Count
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from users.models import Subscription
from courses.models import Group


@receiver(post_save, sender=Subscription)
def post_save_subscription(sender, instance: Subscription, created, **kwargs):
    """
    Распределение нового студента в группу курса.

    """
    if created:
        course = instance.course
        user = instance.user
        if not Group.objects.filter(course=course).exists():
            for i in range(9):
                Group.objects.create(title=f"Group_{i + 1}", course=course)
            group = Group.objects.create(title="Group_10", course=course)
        else:
            groups = (
                Group.objects.filter(course=course)
                .annotate(
                    number_of_students=Count("students")
                )
                .order_by("number_of_students")[10]
            )
            n = groups.objects.count()
            if n < 10:
                for i in range(n, 9):
                    Group.objects.create(title=f"Group_{i + 1}", course=course)
                group = Group.objects.create(title="Group_10", course=course)
            else:
                group = groups[0]
        group.students.add(user)
