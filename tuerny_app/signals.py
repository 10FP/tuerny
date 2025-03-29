from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .utils import send_verification_email, HtmlEmailThread
from .models import Comment, UserSettings, Notification, Question
from allauth.socialaccount.models import SocialAccount
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from django.utils.timezone import now


User = get_user_model()

@receiver(post_save, sender=User)
def send_verification_email_signal(sender, instance, created, **kwargs):
    if not created:
        return

    # Sosyal hesapla mı geldi?
    if SocialAccount.objects.filter(user=instance).exists():
        instance.is_email_verified = True
        instance.save(update_fields=['is_email_verified'])
    else:
        # Normal kayıt → kullanıcıya doğrulama bildirimi
        Notification.objects.create(
            user=instance,
            content="Lütfen e-posta adresinizi doğrulayın.",
            url="",  # Varsa profil doğrulama sayfasının linki
            notification_type="email_verification",
            created_at=now()
        )

        # Eğer e-posta da göndereceksen:
        send_verification_email(instance)




@receiver(pre_save, sender=Question)
def cache_old_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = Question.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except Question.DoesNotExist:
            instance._old_status = None

# ✅ Onay geçişi varsa bildirimi gönder
@receiver(post_save, sender=Question)
def send_question_approval_notification(sender, instance, created, **kwargs):
    if created:
        return  # yeni oluşturulduysa değil

    if hasattr(instance, "_old_status") and instance._old_status != "approved" and instance.status == "approved":
        user = instance.user

        if hasattr(user, "settings"):

            # 🔔 Bildirim tercihi varsa
            if user.settings.notify_question_approval:
                Notification.objects.create(
                    user=user,
                    content=f"'{instance.title}' başlıklı sorunuz onaylandı.",
                    url=reverse("tuerny_app:ask", kwargs={"question_id": instance.id}),
                    notification_type="question_approval"
                )

            # 📧 E-posta tercihi varsa
            if user.settings.email_question_approval:
                context = {
                    "user": user,
                    "question": instance,
                    "question_url": f"{settings.FRONTEND_URL}/ask/{instance.id}"
                }

                HtmlEmailThread(
                    subject="Sorunuz Onaylandı!",
                    template_name="email/question_approval.html",
                    context=context,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=user.email
                ).start()