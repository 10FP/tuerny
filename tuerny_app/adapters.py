import random
import string
from allauth.account.adapter import DefaultAccountAdapter

class CustomAccountAdapter(DefaultAccountAdapter):
    def populate_username(self, request, user):
        """Kullanıcı adı boşsa rastgele bir username oluştur."""
        if not user.username:
            random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            user.username = f"user_{random_suffix}"  # Örnek: user_a1b2c3

    def is_open_for_signup(self, request):
        """Google OAuth ile gelen kullanıcıları otomatik kaydetmek için signup zorunluluğunu kaldır."""
        return True