
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
app_name="tuerny_app"
urlpatterns = [
    path("", views.index, name="index"),
    path("ask/<int:pool_id>", views.ask_details, name="ask"),
    path("login/", views.login, name="login"),
    path("blog-detail/<str:slug>", views.blog_detail, name="blog_detail"),
    path("register/", views.register, name="register"),
    path("profil/", views.profile, name="profile"),
    path("profil/ayarlar", views.settings, name="settings"),
    path("profil/kaydedilenler", views.settings, name="saved"),
    path("profil/yorumlar/", views.settings, name="comments"),
    path("profil/sorularim/", views.settings, name="questions"),
    path("profil/oylarim/", views.settings, name="votes"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
