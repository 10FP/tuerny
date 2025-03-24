from django.shortcuts import render, redirect, get_object_or_404
from .models import Poll, Blog, SubCategory, Question, MainCategory, SuggestedBlog, CategorySuggestedBlog, APISettings, PollOption, Comment, MainSuggestedBlog, SavedBlog, UserSettings, CustomUser, SuggestedQuestion, Product, BlogContent, ContactMessage, Notification
from django.contrib.auth import authenticate, login as auth_login,update_session_auth_hash
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import logout
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from itertools import chain
from django.http import JsonResponse
import random
from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.cache import cache
from django.db.models import Count
from django.core.mail import send_mail
from .utils import verify_email_token
from django.utils.text import slugify
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import get_backends
# Create your views here.
User = get_user_model()
from .utils import generate_email_verification_token, HtmlEmailThread
from datetime import datetime, date



def index(request):
    products = Product.objects.all()
    api = APISettings.objects.all()
    blog = Blog.objects.all()
    main = MainSuggestedBlog.objects.all()
    
    if request.user.is_authenticated:
        saved_blogs = Blog.objects.filter(saved_by_users__user=request.user)
    else:
        saved_blogs = Blog.objects.none()  # Kullanıcı giriş yapmamışsa boş bir queryset döndür

    return render(request, 'tuerny_app/index.html', {"blog": blog, "api": api, "main": main,'saved_blogs': saved_blogs, "products": products})

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
        question_id = request.POST.get("type_id")
        content = request.POST.get("content")
        anonymous = request.POST.get("hidden_user_name") == "on"

        # 🔹 Soru kontrolü
        question = get_object_or_404(Question, id=question_id)

        # 🔹 Yorumu oluştur
        comment = Comment.objects.create(
            question=question,
            user=request.user,
            content=content,
            anonymous=anonymous
        )

        # 🔔 Bildirim ve 📧 e-posta göndermek için hedef kullanıcı (soru sahibi)
        receiver = question.user

        if receiver != request.user:  # Kendine bildirim gitmesin
            # 🔔 Site içi bildirim ayarı varsa
            if hasattr(receiver, "settings") and receiver.settings.notify_question_comments:
                Notification.objects.create(
                    user=receiver,
                    content=f"'{question.title}' başlıklı soruna bir yorum yapıldı.",
                    url=reverse("tuerny_app:ask", kwargs={"question_id": question.id}),
                    notification_type="question_comment"
                )

            # 📧 E-posta bildirimi ayarı varsa
            if hasattr(receiver, "settings") and receiver.settings.email_question_comments:
                context = {
                    "user": receiver,
                    "question": question,
                    "comment": comment,
                    "question_url": request.build_absolute_uri(
                        reverse("tuerny_app:ask", kwargs={"question_id": question.id})
                    )
                }

                HtmlEmailThread(
                    subject="Soruna Yorum Yapıldı",
                    template_name="email/question_comment.html",
                    context=context,
                    from_email='no-reply@teurny.com',
                    to=receiver.email
                ).start()

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
        print("gender", gender)
        password = request.POST.get('password')
        password_again = request.POST.get('password_again')


        if not birth_date:
            messages.error(request, "Doğum tarihi zorunludur!")
            return render(request, 'tuerny_app/register.html')

        # Yaş kontrolü
        try:
            birth_date_obj = datetime.strptime(birth_date, "%Y-%m-%d").date()
            today = date.today()
            age = today.year - birth_date_obj.year - ((today.month, today.day) < (birth_date_obj.month, birth_date_obj.day))

            if age < 18:
                messages.error(request, "18 yaşından küçükler kayıt olamaz.")
                return render(request, 'tuerny_app/register.html')
        except ValueError:
            messages.error(request, "Geçerli bir doğum tarihi girin.")
            return render(request, 'tuerny_app/register.html')
        
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
        login(request, user)
        messages.success(request, "Kayıt başarılı! Giriş yapabilirsiniz.")
        return render(request, 'tuerny_app/login.html')  # Başarılı işlem sonrası login sayfasına yönlendirme
    return render(request, 'tuerny_app/register.html') 
User = get_user_model()
def login(request):
    if request.user.is_authenticated:
        return redirect("tuerny_app:index")

    if request.method == "POST":
        email = request.POST.get("email")  # FORM'DAKİ NAME="email" İLE UYUMLU OLMALI
        password = request.POST.get("password")

        print(f"Email: {email}, Password: {password}")  # Debugging İçin

        # Kullanıcıyı email ile getir
        user = User.objects.filter(email=email).first()

        if user and user.check_password(password):  # Şifreyi doğrula
            backend = get_backends()[0].__class__.__module__ + "." + get_backends()[0].__class__.__name__
            auth_login(request, user, backend=backend)
            messages.success(request, "Başarıyla giriş yaptınız.")
            return redirect("tuerny_app:index")
        else:
            messages.error(request, "Hatalı e-posta veya şifre!")
            return redirect("tuerny_app:login")

    return render(request, "tuerny_app/login.html")


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

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from django.shortcuts import render
from .models import Question, SuggestedQuestion

def question(request):
    sort_option = request.GET.get("sort", "latest")  # Varsayılan sıralama

    # **Sadece Onaylı Soruları Getir**
    questions = Question.objects.filter(status="approved").prefetch_related("poll__options")

    # **Sıralama Seçenekleri**
    if sort_option == "latest":
        questions = questions.order_by("-created_at")
    elif sort_option == "oldest":
        questions = questions.order_by("created_at")
    elif sort_option == "most_commented":
        questions = questions.annotate(comment_count=Count("comments")).order_by("-comment_count")
    elif sort_option == "most_liked":
        questions = questions.annotate(like_count_annotated=Count("likes", distinct=True)).order_by("-like_count_annotated")

    # **Paginator Kullanımı**
    page = request.GET.get("page", 1)  # Varsayılan olarak ilk sayfa
    paginator = Paginator(questions, 3)  # Sayfa başına 3 soru gösterilecek

    try:
        questions = paginator.page(page)
    except PageNotAnInteger:
        questions = paginator.page(1)
    except EmptyPage:
        questions = paginator.page(paginator.num_pages)

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
        "selected_sort": sort_option,
        "paginator": paginator,  # Paginator nesnesini şablona gönder
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
    if blog_.status != "approved":
        return redirect("tuerny_app:control_blog", slug=blog_.slug)

    if request.user.is_authenticated:
        saved_blogs = Blog.objects.filter(saved_by_users__user=request.user)
    else:
        saved_blogs = Blog.objects.none() 

    

    return render(request, "tuerny_app/blog_detail.html", {"blog": blog, "blog_": blog_, "s_blog":s_blogs, "saved_blog": saved_blogs})

def control_blog(request, slug):
    blog_ = get_object_or_404(Blog, slug=slug)
    return render(request, "tuerny_app/blog_control.html", {"blog_": blog_})

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
        all_subcategories = list(category.subcategories.all())
        if len(all_subcategories) >= 3:
            random_subcategories = random.sample(all_subcategories[1:], 2)
        else:
            random_subcategories = all_subcategories
        blogs = first_subcategory.blogs.all()
        second = random_subcategories[0].blogs.all()
        seconds = random_subcategories[0].extra_blogs.all()
        merged_second_blogs = chain(second, seconds)
        third = random_subcategories[1].blogs.all()
        thirds = random_subcategories[1].extra_blogs.all()
        merged_third_blogs = chain(third, thirds)
        extra = CategorySuggestedBlog.objects.all()
        return render(request, "tuerny_app/category_detail.html", {"category": category, "blogs": blogs,"second_blogs":merged_second_blogs, "third_blogs": merged_third_blogs,"extra": extra,"saved_blogs": saved_blogs})
        
def confirm(request):
    return render(request, 'tuerny_app/confirm.html')

def answer(request):
    return render(request, 'tuerny_app/answer.html')

def broken(request):
    return render(request, "tuerny_app/404.html")

def contact(request):
    if request.method == "POST":
        subject = request.POST.get("subject")
        email = request.POST.get("mail")
        phone = request.POST.get("phone")
        message = request.POST.get("message")

        if subject and email and phone and message:
            ContactMessage.objects.create(
                subject=subject,
                email=email,
                phone=phone,
                message=message
            )
            messages.success(request, "Mesajınız başarıyla gönderildi!")
            return redirect("tuerny_app:contact")  # İletişim sayfasına yönlendirme
        else:
            messages.error(request, "Lütfen tüm alanları doldurun!")

    return render(request, "tuerny_app/contact.html")

def contract(request):
    tab = request.GET.get('tab', '')
    
    
    return render(request, 'tuerny_app/contract.html', {"active_tab": tab})

def linkinbio(request):
    return render(request, 'tuerny_app/linkinbio.html')

def logout_view(request):
    # Kullanıcıyı oturumdan çıkar
    logout(request)
    # Oturumdan çıktıktan sonra yönlendirme yap (örneğin anasayfaya)
    return redirect('tuerny_app:index')  # 'home' URL adını kendi projenize göre değiştirin


def vote_poll(request, question_id, option_id):
    if request.method == "POST" and request.user.is_authenticated:
        question = get_object_or_404(Question, id=question_id)
        poll = question.poll
        poll_owner = question.user

        # Önceki oyunu kaldır
        previous_vote = PollOption.objects.filter(poll=poll, voted_users=request.user).first()
        if previous_vote:
            previous_vote.voted_users.remove(request.user)

        # Yeni oy ekle
        new_option = get_object_or_404(PollOption, id=option_id)
        new_option.voted_users.add(request.user)

        # Toplam oyları tekrar hesapla
        total_votes = sum(option.vote_count for option in poll.options.all())

        # Yüzdelik oranları hesapla
        percentages = {
            option.id: round((option.vote_count / total_votes * 100), 1) if total_votes > 0 else 0
            for option in poll.options.all()
        }

        # 🔔 Site içi bildirim & ✉️ Mail
        if poll_owner != request.user and hasattr(poll_owner, "settings"):
            # 🔔 Site içi bildirim
            if poll_owner.settings.notify_poll_votes:
                Notification.objects.create(
                    user=poll_owner,
                    content=f"'{question.title}' başlıklı anketine yeni bir oy verildi.",
                    url=reverse("tuerny_app:ask", kwargs={"question_id": question.id}),
                    notification_type="poll_vote"
                )

            # ✉️ E-posta kontrolü
            if poll_owner.settings.email_poll_votes:
                if total_votes % 10 != 0 or total_votes % 50 != 0:
                    context = {
                        "user": poll_owner,
                        "question": question,
                        "poll": poll,
                        "total_votes": total_votes,
                        "question_url": request.build_absolute_uri(
                            reverse("tuerny_app:ask", kwargs={"question_id": question.id})
                        )
                    }

                    HtmlEmailThread(
                        subject="Anketine Oy Verildi!",
                        template_name="email/poll_vote_milestone.html",
                        context=context,
                        from_email="furkanp2002@gmail.com",
                        to=poll_owner.email
                    ).start()

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
        print("fp1")
        if not request.user.is_authenticated:
            print("fp2")
            return JsonResponse({"redirect": "/login"})
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
    if request.method == "POST":
        if request.user.is_authenticated:
            question = get_object_or_404(Question, id=question_id)

            if request.user in question.likes.all():
                question.likes.remove(request.user)
                liked = False
            else:
                question.likes.add(request.user)
                question.dislikes.remove(request.user)
                liked = True

                # 🔔 Bildirim & Mail
                receiver = question.user
                if receiver != request.user and hasattr(receiver, "settings"):
                    # 🔔 Bildirim ayarı açıksa
                    if receiver.settings.notify_question_votes:
                        Notification.objects.create(
                            user=receiver,
                            content=f"'{question.title}' başlıklı sorun beğenildi.",
                            url=reverse("tuerny_app:ask", kwargs={"question_id": question.id}),
                            notification_type="question_vote"
                        )

                    # 📧 E-posta eşik kontrolü
                    like_count = question.like_count
                    if receiver.settings.email_question_votes:
                        if like_count % 10 == 0 or like_count % 50 == 0:
                            context = {
                                "user": receiver,
                                "question": question,
                                "like_count": like_count,
                                "question_url": request.build_absolute_uri(
                                    reverse("tuerny_app:ask", kwargs={"question_id": question.id})
                                )
                            }

                            HtmlEmailThread(
                                subject="Sorun Beğeniliyor!",
                                template_name="email/question_like_milestone.html",
                                context=context,
                                from_email=settings.DEFAULT_FROM_EMAIL,
                                to=receiver.email
                            ).start()

            return JsonResponse({
                "success": True,
                "liked": liked,
                "like_count": question.like_count,
                "dislike_count": question.dislike_count
            })

        return JsonResponse({"success": False, "message": "Giriş yapmalısınız!"})
    return JsonResponse({"success": False, "message": "Geçersiz istek!"})
def dislike_question(request, question_id):
    if request.method == "POST" and request.user.is_authenticated:
        question = get_object_or_404(Question, id=question_id)

        if request.user in question.dislikes.all():
            question.dislikes.remove(request.user)
            disliked = False
        else:
            question.dislikes.add(request.user)
            question.likes.remove(request.user)
            disliked = True

            # 🔔 Bildirim & Mail
            receiver = question.user
            if receiver != request.user and hasattr(receiver, "settings"):
                if receiver.settings.notify_question_votes:
                    Notification.objects.create(
                        user=receiver,
                        content=f"'{question.title}' başlıklı sorun beğenilmedi.",
                        url=reverse("tuerny_app:ask", kwargs={"question_id": question.id}),
                        notification_type="question_vote"
                    )

                dislike_count = question.dislike_count
                if receiver.settings.email_question_votes:
                    if dislike_count % 10 == 0 or dislike_count % 50 == 0:
                        context = {
                            "user": receiver,
                            "question": question,
                            "dislike_count": dislike_count,
                            "question_url": request.build_absolute_uri(
                                reverse("tuerny_app:ask", kwargs={"question_id": question.id})
                            )
                        }

                        HtmlEmailThread(
                            subject="Sorun Beğenilmedi!",
                            template_name="email/question_dislike_milestone.html",
                            context=context,
                            from_email="furkanp2002@gmail.com",
                            to=receiver.email
                        ).start()

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

def password_reset(request):
    if request.method == "POST":
        email = request.POST.get("mail")  # Formdan gelen email'i al
        try:
            user = User.objects.get(email=email)  # Kullanıcıyı bul
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = request.build_absolute_uri(f"/reset-password/{uid}/{token}/")

            # **Kullanıcıya Şifre Sıfırlama Maili Gönder**
            send_mail(
                "Şifre Sıfırlama Talebi",
                f"Şifreni sıfırlamak için aşağıdaki bağlantıya tıkla:\n{reset_link}",
                "furkanp2002@gmail.com",
                [email],
                fail_silently=False,
            )

            messages.success(request, "Şifre sıfırlama bağlantısı e-posta adresine gönderildi.")
            return redirect("tuerny_app:password-reset")

        except User.DoesNotExist:
            messages.error(request, "Bu e-posta adresi sistemde kayıtlı değil!")
    return render(request, "tuerny_app/password_reset.html")


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

def verify_email_page(request):
    send_verification_email(request.user)
    return render(request, 'tuerny_app/verify_email.html')

def send_verification_email(user):
    token = generate_email_verification_token(user.email)
    verification_link = f"http://172.20.10.2:8000/verify-email/{token}"

    context = {
        "user": user,
        "verification_link": verification_link,
        "user": user
    }

    HtmlEmailThread(
        subject="E-posta Adresinizi Doğrulayın",
        template_name="email/verify_email.html",
        context=context,
        from_email='furkanp2002@gmail.com',
        to=user.email
    ).start()

def verify_email(request, token):
    email = verify_email_token(token)
    if email is None:
        return JsonResponse({"message": "Geçersiz veya süresi dolmuş token!"}, status=400)

    try:
        user = User.objects.get(email=email)
        user.is_email_verified = True
        user.save()
        return redirect("tuerny_app:index")
        return JsonResponse({"message": "E-posta doğrulandı!"}, status=200)
    except User.DoesNotExist:
        return JsonResponse({"message": "Kullanıcı bulunamadı!"}, status=404)



@login_required
def create_blog(request):
    if request.method == "POST":
        # Blog temel bilgileri
        title = request.POST.get("title")
        category_id = request.POST.get("category")
        short_description = request.POST.get("short_description", "")
        media = request.FILES.get("media", None)
        media_extra = request.FILES.get("media_extra", None)
        product_id = request.POST.get("product", None)
        extra_product_ids = request.POST.getlist("extra_product[]")
        author = request.POST.get("author", "")
        extra_category_ids = request.POST.getlist("extra_categories[]")
        # Blog oluştur
        blog = Blog.objects.create(
            title=title,
            author=author,
            category_id=category_id,
            short_description=short_description,
            media=media,
            media_extra=media_extra,
            user=request.user,
            slug=slugify(title),
            product_id=product_id if product_id else None
        )

        # Ekstra ürünleri ManyToMany olarak ekle
        if extra_product_ids:
            
            blog.extra_product.set(extra_product_ids)

        if extra_category_ids:
            blog.extra_categories.set(extra_category_ids)

        # Blog içeriğini işle
        content_types = request.POST.getlist("content_type[]")
        content_texts = request.POST.getlist("content_text[]")
        content_videos = request.POST.getlist("content_video[]")
        content_products = request.POST.getlist("content_product[]")

        # Resimleri doğru sıraya almak için
        content_ids = request.POST.getlist("content_id[]")
        existing_image_ids = request.POST.getlist("existing_content_image[]")
        content_images_raw = request.FILES.getlist("content_image[]")
        image_index = 0
        for i in range(len(content_ids)):
            content_id = content_ids[i]
            image = None

            # image type ise işlem yap
            if content_types[i] == "image":
                if image_index < len(content_images_raw):
                    image = content_images_raw[image_index]
                    image_index += 1
                elif content_id and content_id != "new":
                    old_content = BlogContent.objects.filter(id=content_id).first()
                    image = old_content.image if old_content else None
        content_images = []  
        image_index = 0  

        for content_type in content_types:
            if content_type == "image" and image_index < len(content_images_raw):
                content_images.append(content_images_raw[image_index])
                image_index += 1
            else:
                content_images.append(None)  # Diğer türlerde image boş olmalı

        order = 1
        for i in range(len(content_types)):
            content_type = content_types[i]
            text = content_texts[i] if len(content_texts) > i else None
            image = content_images[i] if len(content_images) > i else None
            video = content_videos[i] if len(content_videos) > i else None
            product_id = content_products[i] if len(content_products) > i and content_products[i] else None
            product = Product.objects.get(id=product_id) if product_id else None

            BlogContent.objects.create(
                blog=blog,
                type=content_type,
                order=order,
                text=text,
                image=image,
                video=video,
                product=product
            )
            order += 1

        return redirect("tuerny_app:blog_detail", slug=blog.slug)

    return render(request, "tuerny_app/blog_create.html", {
        "products": Product.objects.all()
    })

@login_required
def edit_blog(request, slug):
    blog_ = get_object_or_404(Blog, slug=slug)

    if request.method == "POST":
        blog_.title = request.POST.get("title")
        blog_.category_id = request.POST.get("category")
        blog_.short_description = request.POST.get("short_description", "")
        blog_.author = request.POST.get("author", "")

        if request.FILES.get("media"):
            blog_.media = request.FILES["media"]
        if request.FILES.get("media_extra"):
            blog_.media_extra = request.FILES["media_extra"]

        # Benzersiz slug oluştur
        base_slug = slugify(blog_.title)
        slug = base_slug
        counter = 1
        while Blog.objects.filter(slug=slug).exclude(pk=blog_.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        blog_.slug = slug

        # Kategori ve ürünler
        extra_category_ids = request.POST.getlist("extra_categories[]")
        blog_.extra_categories.set(extra_category_ids)

        product_id = request.POST.get("product")
        blog_.product = Product.objects.get(id=product_id) if product_id else None

        extra_product_ids = request.POST.getlist("extra_product[]")
        blog_.extra_product.set(extra_product_ids)

        blog_.save()

        # İçerik verileri
        content_ids = request.POST.getlist("content_id[]")
        content_types = request.POST.getlist("content_type[]")
        content_texts = request.POST.getlist("content_text[]")
        content_videos = request.POST.getlist("content_video[]")
        content_products = request.POST.getlist("content_product[]")
        content_orders = request.POST.getlist("content_order[]")
        existing_image_ids = request.POST.getlist("existing_content_image[]")
        content_images_raw = request.FILES.getlist("content_image[]")

        # Eski içerikleri silmeden önce yedekle
        old_contents = {str(content.id): content for content in BlogContent.objects.filter(blog=blog_)}

        # Tüm içerikleri sil
        BlogContent.objects.filter(blog=blog_).delete()

        # Görsel sıralaması için index
        image_index = 0

        for i in range(len(content_ids)):
            content_id = content_ids[i]
            content_type = content_types[i]
            text = content_texts[i] if len(content_texts) > i else None
            video = content_videos[i] if len(content_videos) > i else None
            product_id = content_products[i] if len(content_products) > i and content_products[i] else None
            product = Product.objects.get(id=product_id) if product_id else None
            order = int(content_orders[i]) if len(content_orders) > i else i + 1

            # Görsel işle
            image = None
            if content_type == "image":
                if image_index < len(content_images_raw):
                    image = content_images_raw[image_index]
                    image_index += 1
                elif content_id != "new" and content_id in old_contents:
                    image = old_contents[content_id].image

            BlogContent.objects.create(
                blog=blog_,
                type=content_type,
                order=order,
                text=text,
                image=image,
                video=video,
                product=product
            )

        return redirect("tuerny_app:blog_detail", slug=blog_.slug)

    s_category = SubCategory.objects.all()
    return render(request, "tuerny_app/blog_edit.html", {
        "blog_": blog_,
        "s_cat": s_category,
        "contents": blog_.contents.all(),
        "products": Product.objects.all()
    })

def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

        if not default_token_generator.check_token(user, token):
            messages.error(request, "Geçersiz veya süresi dolmuş bağlantı.")
            return redirect("tuerny_app:password-reset")

    except (User.DoesNotExist, ValueError, TypeError):
        messages.error(request, "Geçersiz bağlantı!")
        return redirect("tuerny_app:password-reset")

    if request.method == "POST":
        new_password = request.POST.get("password")
        user.set_password(new_password)
        user.save()
        messages.success(request, "Şifre başarıyla değiştirildi. Giriş yapabilirsiniz.")
        return redirect("tuerny_app:login")

    return render(request, "tuerny_app/password_reset_confirm.html", {"uidb64": uidb64, "token": token})

@login_required
def change_blog_status(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)

    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in ["pending", "approved", "rejected"]:  # Geçerli değerleri kontrol et
            blog.status = new_status
            blog.save()

    return redirect("tuerny_app:blog_detail", slug=blog.slug)  # Blog detay sayfasına yönlendir

def custom_404_view(request, exception):
    return render(request, "404.html", status=404)