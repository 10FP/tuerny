from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .utils import send_verification_email  # Fonksiyonu içeri aktar

User = get_user_model()

@receiver(post_save, sender=User)
def send_verification_email_signal(sender, instance, created, **kwargs):
    if created and not instance.is_email_verified:  # Yeni kullanıcı oluşturulduysa
        send_verification_email(instance)