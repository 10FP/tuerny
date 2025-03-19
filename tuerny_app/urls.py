
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404
from tuerny_app.views import custom_404_view

handler404 = custom_404_view

app_name="tuerny_app"

urlpatterns = [
    path("", views.index, name="index"),
    path("ask/<int:question_id>/", views.ask_details, name="ask"),
    path("asked/<int:asked_id>/", views.asked_details, name="asked"),
    path("login/", views.login, name="login"),
    path("ask/", views.ask, name="ask"),
    path("add-comment/", views.add_comment, name="add-comment"),
    path("add-blog-comment/", views.add_blog_comment, name="add_blog_comment"),
    path("hakkimizda/", views.about, name="about"),
    path("answer/", views.answer, name="answer"),   
    path("questions/", views.question, name="question"),
    path("contact/", views.contact, name="contact"),
    path("teurny-uyelik-ve-gizlilik-sozlesmesi/", views.contract, name="contract"),
    path("category/<str:slug>", views.category, name="category"),
    path("blog-detail/<str:slug>/", views.blog_detail, name="blog_detail"),
    path("link-in-bio/", views.linkinbio, name="linkinbio"),
    path("register/", views.register, name="register"),
    path("profil/", views.profile, name="profile"),
    path("confirm/", views.confirm, name="confirm"),
    path("profil/template-parts/saved.html", views.save, name="x"),
    path("profil/template-parts/settings.html", views.settings, name="settings"),
    path("profil/template-parts/asked.html", views.y, name="y"),
    path("profil/template-parts/votes.html", views.v, name="v"),
    path("profil/template-parts/comments.html", views.z, name="z"),
    path("broken-link/", views.broken, name="404"),
    path('logout/', views.logout_view, name='logout'),
    path("vote/<int:question_id>/<int:option_id>/", views.vote_poll, name="vote_poll"),
    path("save-blog/", views.save_blog, name="save_blog"),
    path("like/<int:question_id>/", views.like_question, name="like_question"),
    path("dislike/<int:question_id>/", views.dislike_question, name="dislike_question"),
    path("update-settings/", views.update_settings, name="settings_page"),
    path("change-password/", views.change_password, name="change_password"),
    path("password-reset/", views.password_reset, name="password-reset"),
    path("reset-password/<uidb64>/<token>/", views.password_reset_confirm, name="password-reset-confirm"),
    path("update-profile/", views.update_profile, name="update_profile"),
    path("toggle-favorite/<int:subcategory_id>/", views.toggle_favorite_subcategory, name="toggle_favorite_subcategory"),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
     path("blog/yeni/", views.create_blog, name="create_blog"),
     path("blog-control/<slug:slug>/", views.control_blog, name="control_blog"),
     path("blog/<slug:slug>/edit/", views.edit_blog, name="edit_blog"),
     path("blog/<int:blog_id>/change-status/", views.change_blog_status, name="change_blog_status"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
