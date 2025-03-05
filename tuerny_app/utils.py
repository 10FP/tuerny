from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse

signer = TimestampSigner()

def generate_email_verification_token(email):
    return signer.sign(email)

def verify_email_token(token, max_age=3600):  # 1 saat (3600 saniye) geçerli
    try:
        email = signer.unsign(token, max_age=max_age)
        return email
    except (BadSignature, SignatureExpired):
        return None
    
def send_verification_email(user):
    token = generate_email_verification_token(user.email)
    verification_link = f"{settings.FRONTEND_URL}/verify-email/{token}"

    subject = "E-posta Adresinizi Doğrulayın"
    message = f"Merhaba {user.username},\n\nLütfen aşağıdaki bağlantıya tıklayarak e-posta adresinizi doğrulayın:\n\n{verification_link}\n\nTeşekkürler!"
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])