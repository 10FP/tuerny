from django.shortcuts import render, redirect, get_object_or_404
from .models import Poll, Blog, SubCategory, Question, MainCategory, SuggestedBlog, CategorySuggestedBlog, APISettings, PollOption, Comment, MainSuggestedBlog, SavedBlog, UserSettings, CustomUser, SuggestedQuestion
from django.contrib.auth import authenticate, login as auth_login,update_session_auth_hash
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from itertools import chain
from django.http import JsonResponse
import random
from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.cache import cache
from django.db.models import Count

# Create your views here.
User = get_user_model()
def index(request):
    api = APISettings.objects.all()
    blog = Blog.objects.all()
    main = MainSuggestedBlog.objects.all()
    
    if request.user.is_authenticated:
        saved_blogs = Blog.objects.filter(saved_by_users__user=request.user)
    else:
        saved_blogs = Blog.objects.none()  # Kullanıcı giriş yapmamışsa boş bir queryset döndür

    
        
    return render(request, 'tuerny_app/index.html', {"blog": blog, "api": api, "main": main,'saved_blogs': saved_blogs})

def about(request):
    s_blogs = SuggestedBlog.objects.all()
    return render(request, 'tuerny_app/about.html', {"extra": s_blogs})

def ask_details(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    
    try:
        if question.poll:
            pool = question.poll
            question_id = question.id
        cache_key = f"viewed_question_{question_id}_{request.user.id if request.user.is_authenticated else request.META['REMOTE_ADDR']}" 
        if not cache.get(cache_key):
            question.views_count += 1  # Görüntülenme sayısını artır
            question.save()  # Değişiklikleri veritabanına kaydet
            cache.set(cache_key, True, timeout=10)  

        questions = Question.objects.prefetch_related("poll__options")

        poll_data = {}

        for question in questions:
            if hasattr(question, "poll"):
                # Toplam oyları hesapla (`vote_count` property’sini kullanarak)
                total_votes = sum(option.vote_count for option in question.poll.options.all())

                # Seçeneklerin yüzdesini hesapla
                poll_data[question.id] = {
                    "total_votes": total_votes,
                    "percentages": {
                        option.id: round((option.vote_count / total_votes * 100), 1) if total_votes > 0 else 0
                        for option in question.poll.options.all()
                    }
                }
        
        return render(request, 'tuerny_app/ask-details.html', {"pool": pool, "questions": questions, "poll_data": poll_data})
    except Exception as e:
        return redirect("tuerny_app:asked", asked_id = question.id)
    
        
        
    
    
        

def asked_details(request, asked_id):
    question = Question.objects.get(id=asked_id)
    question_id = question.id
    cache_key = f"viewed_question_{question_id}_{request.user.id if request.user.is_authenticated else request.META['REMOTE_ADDR']}" 
    if not cache.get(cache_key):
            question.views_count += 1  # Görüntülenme sayısını artır
            question.save()  # Değişiklikleri veritabanına kaydet
            cache.set(cache_key, True, timeout=1)  

    return render(request, 'tuerny_app/asked-details.html', {"question": question})

@login_required
def add_blog_comment(request):
    blog = Blog.objects.all()
    s_blogs = SuggestedBlog.objects.all()
    
    if request.method == "POST":
        
        blog_id = request.POST.get("blog_id")  # Formdaki blog yazısının ID'si
        
        content = request.POST.get("content")
        
        anonymous = request.POST.get("hidden_user_name") == "on"  # Checkbox "on" olarak gelir

        # 🔹 Blog yazısının var olup olmadığını kontrol et
        try:
            
            blog_ = get_object_or_404(Blog, id=blog_id)
        
       
            comment = Comment.objects.create(
                blog=blog_,
                user=request.user,
                content=content,
                anonymous=anonymous
        )
        except Exception as e:
            print(e)

        
        
        return render(request, "tuerny_app/blog_detail.html", {"blog": blog, "blog_": blog_, "s_blog":s_blogs})

    return render(request, "tuerny_app/blog_detail.html", {"blog": blog, "blog_": blog_, "s_blog":s_blogs})

def add_comment(request):
    
    if request.method == "POST":
        question_id = request.POST.get("type_id")  # Formdaki `type_id`, `Question` ID'sini tutuyor
        
        content = request.POST.get("content")
        anonymous = request.POST.get("hidden_user_name") == "on"  # Checkbox "on" olarak gelir

        # 🔹 Sorunun var olup olmadığını kontrol et
        question = get_object_or_404(Question, id=question_id)

        # 🔹 Yorum ekle
        comment = Comment.objects.create(
            question=question,
            user=request.user,
            content=content,
            anonymous=anonymous
        )
        
        
        return redirect("tuerny_app:ask", question_id=question_id)

    return JsonResponse({"status": "error", "message": "Geçersiz istek!"}, status=400)

def ask(request):
    subs = SubCategory.objects.all()
    if request.method == "POST":
        # 🔹 Formdan gelen verileri al
        subcategory_id = request.POST.get("subcategory")
        topic = request.POST.get("topic")
        title = request.POST.get("title")
        description = request.POST.get("description")
        anonymous = request.POST.get("anonymous") == "on"  # Checkbox "on" olarak gelir
        add_survey = request.POST.get("add_survey") == "on"  # Anket ekleme checkbox

        # 🔹 Subcategory kontrolü
        subcategory = SubCategory.objects.filter(id=subcategory_id).first() if subcategory_id else None

        # 🔹 Question modeline kaydet
        question = Question.objects.create(
            user=request.user,
            subcategory=subcategory,
            topic=topic,
            title=title,
            description=description,
            anonymous=anonymous
        )

        # 🔹 Eğer "Anket Ekle" seçeneği seçilmişse, Poll ve PollOptions oluştur
        if add_survey:
            survey_title = request.POST.get("survey_title")
            selection_a = request.POST.get("selection_a")
            selection_b = request.POST.get("selection_b")
            selection_c = request.POST.get("selection_c", "").strip()
            selection_d = request.POST.get("selection_d", "").strip()

            # Eğer anket sorusu ve en az iki seçenek girilmişse
            if survey_title and selection_a and selection_b:
                poll = Poll.objects.create(
                    question=question,
                    poll_question=survey_title
                )

                # Anket seçeneklerini ekleyelim
                PollOption.objects.create(poll=poll, option_text=selection_a)
                PollOption.objects.create(poll=poll, option_text=selection_b)

                # 3. ve 4. seçenekler boş değilse ekleyelim
                if selection_c:
                    PollOption.objects.create(poll=poll, option_text=selection_c)
                if selection_d:
                    PollOption.objects.create(poll=poll, option_text=selection_d)

        
        return render(request, 'tuerny_app/ask.html', context={"subs": subs})
    
    return render(request, 'tuerny_app/ask.html', context={"subs": subs})

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
    
    
    return render(request, 'tuerny_app/profile.html', {"active_tab": tab})

def settings(request):
    user_settings, created = UserSettings.objects.get_or_create(user=request.user)
    return render(request, "tuerny_app/settings.html", {"user_settings": user_settings})

def saved(request):
    return render(request, "tuerny_app/saved.html")

def comments(request):
    return render(request, "tuerny_app/saved.html")

def votes(request):
    return render(request, "tuerny_app/votes.html")

def questions(request):
    return render(request, "tuerny_app/questions.html")

def question(request):
    sort_option = request.GET.get("sort", "latest")  # Varsayılan: "En son eklenenler"

    # **Sıralama Seçenekleri**
    if sort_option == "latest":
        questions = Question.objects.prefetch_related("poll__options").order_by("-created_at")
    elif sort_option == "oldest":
        questions = Question.objects.prefetch_related("poll__options").order_by("created_at")
    elif sort_option == "most_commented":
        questions = Question.objects.prefetch_related("poll__options").annotate(comment_count=Count("comments")).order_by("-comment_count")
    elif sort_option == "most_liked":
        questions = Question.objects.prefetch_related("poll__options") \
    .annotate(like_count_annotated=Count("likes", distinct=True)) \
    .order_by("-like_count_annotated")
    else:
        questions = Question.objects.prefetch_related("poll__options")

    # **Anket Verilerini Hazırla**
    poll_data = {}
    for question in questions:
        if hasattr(question, "poll"):
            total_votes = sum(option.vote_count for option in question.poll.options.all())
            poll_data[question.id] = {
                "total_votes": total_votes,
                "percentages": {
                    option.id: round((option.vote_count / total_votes * 100), 1) if total_votes > 0 else 0
                    for option in question.poll.options.all()
                }
            }

    s_questions = SuggestedQuestion.objects.all()
    return render(request, "tuerny_app/question.html", {
        "questions": questions,
        "poll_data": poll_data,
        "s_q": s_questions,
        "selected_sort": sort_option  # Seçili sıralama bilgisini gönderiyoruz
    })

def save(request):
    
    return render(request, "tuerny_app/save.html")

def y(request):
    
    return render(request, "tuerny_app/asked.html")

def v(request):
    questions = Question.objects.prefetch_related("poll__options")

    poll_data = {}

    for question in questions:
        if hasattr(question, "poll"):
            # Toplam oyları hesapla (`vote_count` property’sini kullanarak)
            total_votes = sum(option.vote_count for option in question.poll.options.all())

            # Seçeneklerin yüzdesini hesapla
            poll_data[question.id] = {
                "total_votes": total_votes,
                "percentages": {
                    option.id: round((option.vote_count / total_votes * 100), 1) if total_votes > 0 else 0
                    for option in question.poll.options.all()
                }
            }
    return render(request, "tuerny_app/votes.html", {"poll_data": poll_data})

def z(request):
    
    return render(request, "tuerny_app/comments.html")

def blog_detail(request, slug):
    blog = Blog.objects.all()
    s_blogs = SuggestedBlog.objects.all()
    blog_ = get_object_or_404(Blog, slug=slug)

    if request.user.is_authenticated:
        saved_blogs = Blog.objects.filter(saved_by_users__user=request.user)
    else:
        saved_blogs = Blog.objects.none() 

    print(blog_ in saved_blogs)

    return render(request, "tuerny_app/blog_detail.html", {"blog": blog, "blog_": blog_, "s_blog":s_blogs, "saved_blog": saved_blogs})

def category(request, slug):
    if request.user.is_authenticated:
        saved_blogs = Blog.objects.filter(saved_by_users__user=request.user)
    else:
        saved_blogs = Blog.objects.none()  # Kullanıcı giriş yapmamışsa boş bir queryset döndür
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
            return render(request, "tuerny_app/category_detail.html", {"category": category, "blogs": merged_blogs, "second_blogs": merged_second_blogs, "third_blogs": merged_third_blogs, "extra": extra, "saved_blogs": saved_blogs})
    except:
        pass
    
    
    category = MainCategory.objects.get(slug=slug)
    if category:
        first_subcategory = category.subcategories.first()
            
        blogs = first_subcategory.blogs.all()
            
        return render(request, "tuerny_app/category_detail.html", {"category": category, "blogs": blogs, "saved_blogs": saved_blogs})
        
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


def vote_poll(request, question_id, option_id):
    """
    Kullanıcı yeni oy verirse ekler, eski oyunu değiştirmek isterse günceller.
    """
    if request.method == "POST" and request.user.is_authenticated:
        question = get_object_or_404(Question, id=question_id)

        # Kullanıcının bu anket için önceki oyunu var mı?
        previous_vote = PollOption.objects.filter(poll=question.poll, voted_users=request.user).first()

        # Eğer daha önce oy verdiyse eski oyunu kaldır
        if previous_vote:
            previous_vote.voted_users.remove(request.user)

        # Yeni oyu ekle
        new_option = get_object_or_404(PollOption, id=option_id)
        new_option.voted_users.add(request.user)

        # Toplam oyları tekrar hesapla
        total_votes = sum(option.vote_count for option in question.poll.options.all())

        # Yüzdelik oranları tekrar hesapla
        percentages = {
            option.id: round((option.vote_count / total_votes * 100), 1) if total_votes > 0 else 0
            for option in question.poll.options.all()
        }

        return JsonResponse({
            "success": True,
            "message": "Oy başarıyla güncellendi!",
            "total_votes": total_votes,
            "percentages": percentages
        })

    return JsonResponse({"success": False, "message": "Geçersiz istek!"})


@csrf_exempt
@login_required
def save_blog(request):
    if request.method == "POST":
        
        data = json.loads(request.body)
        blog_id = data.get("blog_id")

        try:
            blog = Blog.objects.get(id=blog_id)
        except Blog.DoesNotExist:
            return JsonResponse({"error": "Blog not found"}, status=404)

        saved_blog, created = SavedBlog.objects.get_or_create(user=request.user, blog=blog)

        if not created:
            saved_blog.delete()
            print("unsaved")
            return JsonResponse({"status": "unsaved"})
        print("saved")
        return JsonResponse({"status": "saved"})

    return JsonResponse({"error": "Invalid request"}, status=400)


def like_question(request, question_id):
    """
    Kullanıcı bir soruyu beğenirse ekler, tekrar basarsa beğeniyi kaldırır.
    Eğer kullanıcı daha önce beğenmediyse ve beğenmediyse, beğenme işlemi yapılır.
    """
    print("✅ FP: Fonksiyon çalıştı")
    
    if request.method == "POST":
        print("✅ FP: POST isteği geldi")

        if request.user.is_authenticated:
            print(f"✅ FP: Kullanıcı giriş yapmış - {request.user}")

            question = get_object_or_404(Question, id=question_id)
            print(f"✅ FP: Soru bulundu - {question.title}")

            if request.user in question.likes.all():
                question.likes.remove(request.user)
                liked = False
                print("✅ FP: Kullanıcı beğeniyi kaldırdı")
            else:
                question.likes.add(request.user)
                question.dislikes.remove(request.user)  # Beğenmediyse önceki beğenmeyi kaldır
                liked = True
                print("✅ FP: Kullanıcı beğendi")

            print(f"✅ FP: Güncel beğeni sayısı: {question.like_count}")
            print(f"✅ FP: Güncel beğenmeme sayısı: {question.dislike_count}")

            return JsonResponse({
                "success": True,
                "liked": liked,
                "like_count": question.like_count,
                "dislike_count": question.dislike_count
            })
        else:
            print("❌ FP: Kullanıcı giriş yapmamış!")
            return JsonResponse({"success": False, "message": "Giriş yapmalısınız!"})
    else:
        print("❌ FP: GET isteği geldi, işlem yapılmadı!")
        return JsonResponse({"success": False, "message": "Geçersiz istek!"})
    
def dislike_question(request, question_id):
    """
    Kullanıcı bir soruyu beğenmezse ekler, tekrar basarsa kaldırır.
    Eğer kullanıcı daha önce beğendiyse, beğenisini kaldırır ve beğenmeyi ekler.
    """
    if request.method == "POST" and request.user.is_authenticated:
        question = get_object_or_404(Question, id=question_id)
        
        if request.user in question.dislikes.all():
            question.dislikes.remove(request.user)
            disliked = False
        else:
            question.dislikes.add(request.user)
            question.likes.remove(request.user)  # Önceki beğeniyi kaldır
            disliked = True

        return JsonResponse({
            "success": True,
            "disliked": disliked,
            "like_count": question.like_count,
            "dislike_count": question.dislike_count
        })

    return JsonResponse({"success": False, "message": "Geçersiz istek!"})


@login_required
def update_settings(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Debug logları ekleyelim
            print("🔹 Gelen Veri:", data)  

            setting_name = data.get("setting")  # Eğer key yoksa None döndürür
            setting_value = data.get("value")  

            if setting_name is None or setting_value is None:
                return JsonResponse({"success": False, "message": "Eksik veri!"}, status=400)

            user_settings, created = UserSettings.objects.get_or_create(user=request.user)

            if hasattr(user_settings, setting_name):
                setattr(user_settings, setting_name, setting_value)
                user_settings.save()
                return JsonResponse({"success": True, "message": "Ayar güncellendi!"})
            else:
                return JsonResponse({"success": False, "message": "Geçersiz ayar adı!"}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Geçersiz JSON formatı!"}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "message": f"Hata: {str(e)}"}, status=500)

    return JsonResponse({"success": False, "message": "Geçersiz istek!"}, status=405)



@login_required
@csrf_exempt  # AJAX POST için CSRF korumasını esnetiyoruz (güvenlik için dikkat edilmeli)
def change_password(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            old_password = data.get("old_pass")
            new_password = data.get("new_pass")
            new_password_again = data.get("new_pass_again")

            user = request.user

            # Eski şifre doğrulama
            if not user.check_password(old_password):
                return JsonResponse({"success": False, "message": "Eski şifreniz yanlış!"}, status=400)

            # Yeni şifreler uyuşuyor mu?
            if new_password != new_password_again:
                return JsonResponse({"success": False, "message": "Yeni şifreler eşleşmiyor!"}, status=400)

            # Yeni şifreyi belirle
            user.set_password(new_password)
            user.save()

            # Kullanıcının oturumunu açık tut
            update_session_auth_hash(request, user)

            return JsonResponse({"success": True, "message": "Şifreniz başarıyla değiştirildi!"})

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Geçersiz JSON formatı!"}, status=400)

    return JsonResponse({"success": False, "message": "Geçersiz istek!"}, status=405)


@login_required
@csrf_exempt  # AJAX ile POST işlemi için CSRF korumasını kaldırıyoruz (Güvenlik için dikkat edilmeli)
def update_profile(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            username = data.get("user_name")
            email = data.get("mail")
            phone = data.get("phone")
            gender = data.get("gender")
            birth_date = data.get("birth_date")

            user = request.user

            # Kullanıcı adı boş veya zaten başka biri tarafından alınmış mı kontrol et
            if username and username != user.username:
                if CustomUser.objects.filter(username=username).exclude(id=user.id).exists():
                    return JsonResponse({"success": False, "message": "Bu kullanıcı adı zaten kullanılıyor!"}, status=400)
                user.username = username

            # Email doğrulama
            if email and email != user.email:
                if CustomUser.objects.filter(email=email).exclude(id=user.id).exists():
                    return JsonResponse({"success": False, "message": "Bu e-posta adresi zaten kayıtlı!"}, status=400)
                user.email = email

            # Telefon doğrulama (Opsiyonel: Format kontrolü eklenebilir)
            if phone:
                user.phone = phone

            # Cinsiyet güncelleme
            if gender in ["Female", "Male"]:
                user.gender = gender

            # Doğum tarihi güncelleme
            if birth_date:
                user.birth_date = birth_date

            user.save()
            return JsonResponse({"success": True, "message": "Profiliniz başarıyla güncellendi!"})

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Geçersiz JSON formatı!"}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "message": f"Hata: {str(e)}"}, status=500)

    return JsonResponse({"success": False, "message": "Geçersiz istek!"}, status=405)

@csrf_exempt  # AJAX ile CSRF hatasını önlemek için
def toggle_favorite_subcategory(request, subcategory_id):
    
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "message": "Giriş yapmalısınız!"}, status=401)

    subcategory = get_object_or_404(SubCategory, id=subcategory_id)

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            status = data.get("status", False)

            if status:
                subcategory.saved_users.add(request.user)
            else:
                subcategory.saved_users.remove(request.user)

            return JsonResponse({"success": True, "message": "Favori güncellendi!"})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=400)

    return JsonResponse({"success": False, "message": "Geçersiz istek!"}, status=400)