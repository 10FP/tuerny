from django.shortcuts import render, redirect, get_object_or_404
from .models import Poll, Blog, SubCategory, Question, MainCategory, SuggestedBlog, CategorySuggestedBlog
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from itertools import chain
import random
# Create your views here.
User = get_user_model()
def index(request):
    blog = Blog.objects.all()
    return render(request, 'tuerny_app/index.html', {"blog": blog})

def ask_details(request, pool_id):
    pool = Poll.objects.get(id=pool_id)
    return render(request, 'tuerny_app/ask-details.html', {"pool": pool})

def asked_details(request, asked_id):
    question = Question.objects.get(id=asked_id)
    return render(request, 'tuerny_app/asked-details.html', {"question": question})

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
    tab = request.GET.get('tab', '')
    print(tab)
    return render(request, 'tuerny_app/profile.html', {"active_tab": tab})

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
    questions = Question.objects.all()
    return render(request, "tuerny_app/question.html", {"questions": questions})

def save(request):
    
    return render(request, "tuerny_app/save.html")

def y(request):
    
    return render(request, "tuerny_app/asked.html")

def v(request):
    
    return render(request, "tuerny_app/votes.html")

def z(request):
    
    return render(request, "tuerny_app/comments.html")

def blog_detail(request, slug):
    blog = Blog.objects.all()
    s_blogs = SuggestedBlog.objects.all()
    blog_ = get_object_or_404(Blog, slug=slug)
    return render(request, "tuerny_app/blog_detail.html", {"blog": blog, "blog_": blog_, "s_blog":s_blogs})

def category(request, slug):
    try:
        category = SubCategory.objects.get(slug=slug)
        
        if category:
            main_category = category.main_category 
            other_subcategories = list(main_category.subcategories.exclude(id=category.id))
            
            extra = CategorySuggestedBlog.objects.all()
            if len(other_subcategories) >= 2:
                random_categories = random.sample(other_subcategories, 2)
                second_category, third_category = random_categories
                second_blogs = second_category.blogs.all()
                second_blogss = second_category.extra_blogs.all()
                merged_second_blogs = chain(second_blogs, second_blogss)
                third_blogs = third_category.blogs.all()
                third_blogss = third_category.extra_blogs.all()
                merged_third_blogs = chain(third_blogs, third_blogss)
                
            blogs = category.blogs.all()
            blogss = category.extra_blogs.all()
            merged_blogs = chain(blogs, blogss)
            return render(request, "tuerny_app/category_detail.html", {"category": category, "blogs": merged_blogs, "second_blogs": merged_second_blogs, "third_blogs": merged_third_blogs, "extra": extra})
    except:
        pass
    
    
    category = MainCategory.objects.get(slug=slug)
    if category:
        first_subcategory = category.subcategories.first()
            
        blogs = first_subcategory.blogs.all()
            
        return render(request, "tuerny_app/category_detail.html", {"category": category, "blogs": blogs})
        
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

def logout_view(request):
    # Kullanıcıyı oturumdan çıkar
    logout(request)
    # Oturumdan çıktıktan sonra yönlendirme yap (örneğin anasayfaya)
    return redirect('tuerny_app:index')  # 'home' URL adını kendi projenize göre değiştirin