from django.db import models
from django.contrib.auth.models import AbstractUser
from ckeditor.fields import RichTextField
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.utils.timezone import now
# Create your models here.



class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    is_email_verified = models.BooleanField(default=False)
    gender = models.CharField(
        max_length=10,
        choices=[('Male', 'Erkek'), ('Female', 'Kadın'), ('Other', 'Diğer')],
        null=True,
        blank=True
    )

    REQUIRED_FIELDS = ['email', 'phone', 'birth_date', 'gender']  # Varsayılan alanlara ek olarak zorunlu alanlar
    USERNAME_FIELD = 'username'  # Kullanıcı adı olarak username kullanılacak

    def __str__(self):
        return self.username
    
User = get_user_model()
class MainCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    main_category = models.ForeignKey(MainCategory, on_delete=models.CASCADE, related_name="subcategories")
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True, null=True)
    saved_users = models.ManyToManyField(CustomUser, related_name="saved_categories", blank=True)
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.main_category.name} -> {self.name}"
    
class Question(models.Model):
    topics = [
        ("destek", "Destek Talebi"),
        ("oneri", "Öneri"),
        ("sikayet", "Şikayet"),
        ("diger", "Diğer"),
    ]
    STATUS_CHOICES = [
    ("pending", "Beklemede"),
    ("approved", "Onaylandı"),
    ("rejected", "Reddedildi"),
]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="questions")
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name="question_category", null=True, blank=True)
    topic = models.CharField(max_length=20, choices=topics, verbose_name="Konu", null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(CustomUser, related_name="liked_questions", blank=True)
    dislikes = models.ManyToManyField(CustomUser, related_name="disliked_questions", blank=True)
    views_count = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending", null=True, blank=True)

    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            count = 1
            while Question.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def like_count(self):
        return self.likes.count()

    @property
    def dislike_count(self):
        return self.dislikes.count()


class Poll(models.Model):
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name="poll")
    poll_question = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Poll for: {self.question.title}"


class PollOption(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="options")
    option_text = models.CharField(max_length=255)
    votes = models.PositiveIntegerField(default=0)
    voted_users = models.ManyToManyField(CustomUser, related_name="voted_options", blank=True, null=True)

    def __str__(self):
        return self.option_text
    
    
    
    @property
    def vote_count(self):
        """Toplam oy sayısını döndürür."""
        return self.voted_users.count()
    
class Product(models.Model):
    
    image = models.ImageField(upload_to="product_images/", null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    link = models.URLField(max_length=500, help_text="Ürün bağlantısını ekleyin.")

    def __str__(self):
        return self.title

class Blog(models.Model):
    STATUS_CHOICES = [
    ("pending", "Beklemede"),
    ("approved", "Onaylandı"),
    ("rejected", "Reddedildi"),
]

    category = models.ForeignKey('SubCategory', on_delete=models.SET_NULL, null=True, related_name="blogs")
    extra_categories = models.ManyToManyField('SubCategory', related_name="extra_blogs", blank=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name="product_blog")
    extra_product = models.ManyToManyField(Product, related_name="extra_product_blog", blank=True)
    title = models.CharField(max_length=255)
    short_description = models.TextField(default="", null=True, blank=True)
    
    media = models.ImageField(upload_to='blog_media/', null=True, blank=True)
    media_extra = models.FileField(
        upload_to='blog_media/',
        null=True,
        blank=True,
        help_text="Medya dosyası (resim, video veya ses dosyası) yükleyebilirsiniz."
    )
    user = models.ForeignKey(
        'CustomUser', 
        on_delete=models.CASCADE, 
        related_name="blogs"
    )
    source = models.URLField(max_length=500, null=True, blank=True)  # Kaynak (isteğe bağlı)
    author = models.CharField(max_length=200, null=True, blank=True)  # Kaynak (isteğe bağlı)
    slug = models.SlugField(max_length=255, unique=True, blank=True)  # Slug alanı
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending", null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            while Blog.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']

class CategorySuggestedBlog(models.Model):
    blog = models.OneToOneField(
        Blog,
        on_delete=models.CASCADE,
        related_name="category_suggested_blog"
    )
    is_active = models.BooleanField(default=True)  # Blog önerilerini yönetmek için

    def __str__(self):
        return f"Önerilen: {self.blog.title}"



class SuggestedBlog(models.Model):
    blog = models.OneToOneField(
        Blog,
        on_delete=models.CASCADE,
        related_name="suggested_blog"
    )
    is_active = models.BooleanField(default=True)  # Blog önerilerini yönetmek için

    def __str__(self):
        return f"Önerilen: {self.blog.title}"
    
class SuggestedQuestion(models.Model):
    question = models.OneToOneField(
        Question,
        on_delete=models.CASCADE,
        related_name="suggested_question"
    )
    is_active = models.BooleanField(default=True) 

    def __str__(self):
        return f"Önerilen: {self.question.title}"
    
class MainSuggestedBlog(models.Model):
    blog = models.OneToOneField(
        Blog,
        on_delete=models.CASCADE,
        related_name="main_suggested_blog"
    )
    is_active = models.BooleanField(default=True)  # Blog önerilerini yönetmek için

    def __str__(self):
        return f"Önerilen: {self.blog.title}"


    
class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, null=True, blank=True, related_name="comments")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True, blank=True, related_name="comments")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    anonymous = models.BooleanField(default=False, help_text="Eğer seçilirse yorum anonim olarak yapılır.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.anonymous:
            return f"Anonim Yorum: {self.content[:30]}..."
        return f"{self.user.username}: {self.content[:30]}..."

    class Meta:
        ordering = ['-created_at']

class Save(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="saved_items")
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, null=True, blank=True, related_name="saved_by")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True, blank=True, related_name="saved_by")
    saved_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.blog:
            return f"{self.user.username} saved blog: {self.blog.title}"
        if self.question:
            return f"{self.user.username} saved question: {self.question.title}"
        return f"{self.user.username} saved an item"

    class Meta:
        ordering = ['-saved_at']
        unique_together = ('user', 'blog', 'question')

class APISettings(models.Model):
    name = models.CharField(max_length=255, unique=True, help_text="API Adı (Örn: Google Analytics)")
    script = models.TextField(help_text="Tam script kodunu buraya girin")
    is_active = models.BooleanField(default=True, help_text="API'yi aktif/pasif yap")

    def __str__(self):
        return self.name
    
class SavedBlog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_blogs")
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="saved_by_users")
    saved_at = models.DateTimeField(auto_now_add=True)  # Kullanıcı ne zaman kaydetti?

    class Meta:
        unique_together = ('user', 'blog')  # Aynı kullanıcı aynı blogu birden fazla kez kaydedemesin

    def __str__(self):
        return f"{self.user.username} saved {self.blog.title}"
    

class UserSettings(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="settings")
    
    # Email Ayarları
    email_newsletter = models.BooleanField(default=False)
    email_question_votes = models.BooleanField(default=True)       # 👍👎
    email_question_comments = models.BooleanField(default=True)    # 💬
    email_question_approval = models.BooleanField(default=True)    # ✔️
    email_poll_votes = models.BooleanField(default=True)           # 📊
    email_security_alerts = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=False)

    # Bildirim Ayarları
    notify_campaigns = models.BooleanField(default=True)
    notify_trending = models.BooleanField(default=False)
    notify_question_votes = models.BooleanField(default=True)      # 👍👎
    notify_question_comments = models.BooleanField(default=True)   # 💬
    notify_question_approval = models.BooleanField(default=True)   # ✔️
    notify_poll_votes = models.BooleanField(default=True)          # 📊
    notify_security_alerts = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} Ayarları"
    

class BlogContent(models.Model):
    class ContentType(models.TextChoices):
        HEADER = "header", "Başlık"
        SUBHEADER = "subheader", "Alt Başlık"
        PARAGRAPH = "paragraph", "Paragraf"
        IMAGE = "image", "Resim"
        VIDEO = "video", "Video"
        PRODUCT = "product", "Ürün"

    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="contents")
    type = models.CharField(max_length=20, choices=ContentType.choices)
    order = models.PositiveIntegerField()  # İçerik sırasını belirlemek için

    # İçerik alanları
    text = models.TextField(blank=True, null=True)  # Başlık, alt başlık, paragraf için
    image = models.ImageField(upload_to="blog_images/", blank=True, null=True)  # Resimler
    video = models.URLField(blank=True, null=True)  # Video linki
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)  # Ürün ekleme

    class Meta:
        ordering = ["order"]

    def save(self, *args, **kwargs):
        if self.order is None:  # Eğer order girilmemişse
            last_content = BlogContent.objects.filter(blog=self.blog).order_by("-order").first()
            self.order = (last_content.order + 1) if last_content else 1  # Eğer içerik varsa +1 yap, yoksa 1 ata
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.blog.title} - {self.get_type_display()} (Sıra: {self.order})"
    


class ContactMessage(models.Model):
    SUBJECT_CHOICES = [
        ("support", "Destek Talebi"),
        ("offer", "Öneri"),
        ("complaint", "Şikayet"),
        ("other", "Diğer"),
    ]

    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_subject_display()} - {self.email}"
    
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('email_verification', 'E-posta Doğrulama'),
        ('comment', 'Yorum'),
        ('approval', 'Onay'),
        ('vote', 'Anket Oyu'),
        ('like', 'Beğeni'),
        ('dislike', 'Beğenmeme'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    content = models.CharField(max_length=255)
    url = models.URLField(blank=True, null=True)  # Bildirime tıklanınca gidilecek link
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.notification_type}"