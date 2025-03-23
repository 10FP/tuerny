from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import threading
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

class HtmlEmailThread(threading.Thread):
    def __init__(self, subject, template_name, context, from_email, to, *args, **kwargs):
        self.subject = subject
        self.template_name = template_name
        self.context = context
        self.from_email = from_email
        self.to = to
        super().__init__(*args, **kwargs)

    def run(self):
        html_content = render_to_string(self.template_name, self.context)
        msg = EmailMultiAlternatives(self.subject, "", self.from_email, [self.to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()