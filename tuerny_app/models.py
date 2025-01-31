from django.db import models
from django.contrib.auth.models import AbstractUser
from ckeditor.fields import RichTextField
from django.utils.text import slugify
# Create your models here.
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
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

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.main_category.name} -> {self.name}"
    
class Question(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="questions")
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name="question_category", null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(CustomUser, related_name="liked_questions", blank=True)
    dislikes = models.ManyToManyField(CustomUser, related_name="disliked_questions", blank=True)

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
    


class Blog(models.Model):
    category = models.ForeignKey(
        'SubCategory', 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name="blogs"
    )
    title = models.CharField(max_length=255)
    short_description = RichTextField(default="", null=True, blank=True)
    content = RichTextField()  # CKEditor entegrasyonu için
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

    def save(self, *args, **kwargs):
        if not self.slug:  # Eğer slug yoksa başlık üzerinden oluştur
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        
class SuggestedBlog(models.Model):
    blog = models.OneToOneField(
        Blog,
        on_delete=models.CASCADE,
        related_name="suggested_blog"
    )
    is_active = models.BooleanField(default=True)  # Blog önerilerini yönetmek için

    def __str__(self):
        return f"Önerilen: {self.blog.title}"

class Product(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="products")
    image = models.ImageField(upload_to="product_images/", null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    link = models.URLField(max_length=500, help_text="Ürün bağlantısını ekleyin.")

    def __str__(self):
        return self.title
    
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