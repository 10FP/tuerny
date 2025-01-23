
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
app_name="tuerny_app"
urlpatterns = [
    path("", views.index, name="index"),
    path("ask/<int:pool_id>", views.ask_details, name="ask"),
    path("login/", views.login, name="login"),
    path("ask/", views.ask, name="ask"),
    path("answer/", views.answer, name="answer"),
    path("blog-detail/<str:slug>", views.blog_detail, name="blog_detail"),
    path("questions/", views.question, name="questions"),
    path("contact/", views.contact, name="contact"),
    path("contract/", views.contract, name="contract"),
    path("category/<str:slug>", views.category, name="category"),
    path("link-in-bio/", views.linkinbio, name="linkinbio"),
    path("register/", views.register, name="register"),
    path("profil/", views.profile, name="profile"),
    path("confirm/", views.confirm, name="confirm"),
    path("profil/ayarlar", views.settings, name="settings"),
    path("profil/kaydedilenler", views.saved, name="saved"),
    path("profil/template-parts/saved.html", views.x, name="x"),
    path("profil/template-parts/settings.html", views.settings, name="settings"),
    path("profil/template-parts/asked.html", views.y, name="x"),
    path("profil/template-parts/votes.html", views.v, name="v"),
    path("profil/template-parts/comments.html", views.z, name="z"),
    path("profil/yorumlar/", views.settings, name="comments"),
    path("profil/sorularim/", views.settings, name="questions"),
    path("profil/oylarim/", views.settings, name="votes"),
    path("broken-link/", views.broken, name="404")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
