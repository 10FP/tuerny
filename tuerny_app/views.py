from django.shortcuts import render, redirect, get_object_or_404
from .models import Poll, Blog, SubCategory
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
# Create your views here.
User = get_user_model()
def index(request):
    blog = Blog.objects.all()
    return render(request, 'tuerny_app/index.html', {"blog": blog})

def ask_details(request, pool_id):
    pool = Poll.objects.get(id=pool_id)
    return render(request, 'tuerny_app/ask-details.html', {"pool": pool})

def ask(request):

    return render(request, 'tuerny_app/ask.html')

def register(request):
    if request.user.is_authenticated:
        return redirect("tuerny_app:index")
    if request.method == "POST":
        email = request.POST.get('mail')
        username = request.POST.get('user_name')
        birth_date = request.POST.get('birth_date')
        full_name = request.POST.get('name')
        gender = request.POST.get('gender')
        password = request.POST.get('password')
        password_again = request.POST.get('password_again')
        
        # Temel validasyon
        if not email or not username or not password or not password_again:
            messages.error(request, "Tüm alanları doldurun!")
            return render(request, 'tuerny_app/register.html')  # Hatalı formu geri döndür

        if password != password_again:
            messages.error(request, "Şifreler eşleşmiyor!")
            return render(request, 'tuerny_app/register.html')

        # Kullanıcı mevcut mu kontrolü
        if User.objects.filter(email=email).exists():
            messages.error(request, "Bu e-posta zaten kullanılıyor!")
            return render(request, 'tuerny_app/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Bu kullanıcı adı zaten alınmış!")
            return render(request, 'tuerny_app/register.html')

        # Kullanıcı oluşturma
        user = User(
            email=email,
            username=username,
            first_name=full_name.split()[0],  # Ad
            last_name=" ".join(full_name.split()[1:]),  # Soyad
            gender=gender,  # CustomUser modelinde gender varsa
            birth_date=birth_date  # CustomUser modelinde birth_date varsa
        )
        user.password = make_password(password)  # Şifreyi hash'le
        user.save()

        messages.success(request, "Kayıt başarılı! Giriş yapabilirsiniz.")
        return render(request, 'tuerny_app/login.html')  # Başarılı işlem sonrası login sayfasına yönlendirme
    return render(request, 'tuerny_app/register.html') 

def login(request):
    if request.method == 'POST':
        email = request.POST.get('mail')  # Formdaki "mail" alanını al
        password = request.POST.get('password')  # Formdaki "password" alanını al
        
        # Kullanıcıyı email üzerinden doğrulamak için varsayılan User modeline uygun hale getirin
        try:
            # Email üzerinden kullanıcıyı bul
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None

        if user and user.check_password(password):
            auth_login(request, user)  # Kullanıcıyı giriş yaptır
            messages.success(request, "Başarıyla giriş yaptınız.")
            return redirect('tuerny_app:index')  # Giriş sonrası yönlendirme
        else:
            messages.error(request, "Geçersiz e-posta veya şifre!")  # Hata mesajı ekle
        
        
    
    return render(request, 'tuerny_app/login.html')


@login_required
def profile(request):
    return render(request, 'tuerny_app/profile.html')

def settings(request):
    return render(request, "tuerny_app/settings.html")

def saved(request):
    return render(request, "tuerny_app/saved.html")

def comments(request):
    return render(request, "tuerny_app/saved.html")

def votes(request):
    return render(request, "tuerny_app/votes.html")

def questions(request):
    return render(request, "tuerny_app/questions.html")

def question(request):
    return render(request, "tuerny_app/question.html")

def x(request):
    print(request.user.saved_items.all())
    return render(request, "tuerny_app/x.html")

def y(request):
    print(request.user.saved_items.all())
    return render(request, "tuerny_app/asked.html")

def v(request):
    print(request.user.saved_items.all())
    return render(request, "tuerny_app/votes.html")

def z(request):
    print(request.user.saved_items.all())
    return render(request, "tuerny_app/comments.html")

def blog_detail(request, slug):
    blog = Blog.objects.all()
    blog_ = get_object_or_404(Blog, slug=slug)
    return render(request, "tuerny_app/blog_detail.html", {"blog": blog, "blog_": blog_})

def category(request, slug):
    category = SubCategory.objects.get(slug=slug)
    if category:
        
        blogs = category.blogs.all()
        return render(request, "tuerny_app/category_detail.html", {"category": category, "blogs": blogs})
    else:
        category = SubCategory.subcategories.objects.get(slug=slug)


        return render(request, "tuerny_app/category_detail.html", {"categery": category})
        
def confirm(request):
    return render(request, 'tuerny_app/confirm.html')

def answer(request):
    return render(request, 'tuerny_app/answer.html')

def broken(request):
    return render(request, "tuerny_app/404.html")

def contact(request):
    return render(request, "tuerny_app/contact.html")

def contract(request):
    return render(request, 'tuerny_app/contract.html')

def linkinbio(request):
    return render(request, 'tuerny_app/linkinbio.html')