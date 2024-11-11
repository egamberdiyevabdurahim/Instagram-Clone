from threading import Thread
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from app_user.views import send_confirmation


@receiver(post_save, sender=get_user_model())
def send_verification(sender, instance=None, created=False, **kwargs):
    if created:
        Thread(target=send_confirmation, args=(instance,)).start()
