from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import Balance
from django.contrib.auth import get_user_model


User = get_user_model()


@receiver(post_save, sender=User)
def create_balance(sender, instance, created, **kwargs):
    """
    Создает новому пользователю баланс равный 1000 бонусов.
    """
    print("new")
    if created:
        instance.balance = Balance.objects.create(value=1000, user=instance)
        instance.save()
