from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .utils import send_verification_email  # Fonksiyonu içeri aktar
from .models import Comment, UserSettings
from django.core.mail import send_mail
User = get_user_model()

@receiver(post_save, sender=User)
def send_verification_email_signal(sender, instance, created, **kwargs):
    if created and not instance.is_email_verified:  # Yeni kullanıcı oluşturulduysa
        send_verification_email(instance)


@receiver(post_save, sender=Comment)
def notify_question_comment(sender, instance, created, **kwargs):
    """
    Bir soru için yeni yorum yapıldığında, sorunun sahibine bildirim ve e-posta gönder.
    """
    if created and instance.question:  # Eğer yorum bir soru ile ilişkiliyse
        question = instance.question
        user = question.user  # Soruyu soran kullanıcı

        try:
            settings = user.settings  # Kullanıcının bildirim ayarlarını al
        except UserSettings.DoesNotExist:
            return  # Kullanıcının ayarları yoksa işlemi durdur

        # **1️⃣ Bildirim Gönder**
        # if settings.notify_question_answers:  # Yorumlar için bildirim alma ayarı açıksa
        #     Notification.objects.create(
        #         user=user,
        #         content_type=ContentType.objects.get_for_model(Comment),
        #         object_id=instance.id,
        #         message=f"{instance.user.username} soruna yorum yaptı.",
        #     )

        # **2️⃣ E-posta Gönder**
        if settings.email_question_answers and user.email:  # Yorumlar için e-posta alma ayarı açıksa
            subject = "Soruna Yeni Bir Yorum Yapıldı"
            
            
            send_mail(
                subject,
                "Soruna Yeni Bir Yorum Yapıldı",
                "furkanp2002@gmail.com",
                [user.email],
                fail_silently=False,
            )