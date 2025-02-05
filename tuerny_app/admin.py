from django.contrib import admin
from .models import CustomUser, Question, Poll, PollOption, SubCategory, MainCategory, Blog, Product, Comment, Save, SuggestedBlog, CategorySuggestedBlog
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
import csv
import zipfile
from io import StringIO, BytesIO
from django.http import HttpResponse
from django.apps import apps
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.urls import path
# Register your models here.

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        ('Ek Alanlar', {
            'fields': ('phone', 'birth_date', 'gender'),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Ek Alanlar', {
            'fields': ('email', 'phone', 'birth_date', 'gender'),
        }),
    )


class PollOptionInline(admin.TabularInline):
    model = PollOption
    extra = 2  
    max_num = 4  

class PollAdmin(admin.ModelAdmin):
    list_display = ('poll_question', 'question', 'created_at')
    inlines = [PollOptionInline]

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at', 'like_count', 'dislike_count', 'subcategory')
    list_filter = ('created_at',)
    search_fields = ('title', 'description')
    readonly_fields = ('like_count', 'dislike_count')


class SubCategoryInline(admin.TabularInline):
    model = SubCategory
    extra = 1
    prepopulated_fields = {"slug": ("name",)}

class MainCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [SubCategoryInline]
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'user', 'created_at', 'copy_blog_link')
    search_fields = ('title', 'content')
    list_filter = ('category', 'created_at')
    prepopulated_fields = {'slug': ('title',)} 
    
    def copy_blog(self, request, queryset):
        """
        Seçilen blog objelerini kopyalar.
        """
        for blog in queryset:
            blog.pk = None  # Yeni bir nesne oluşturmak için id'yi sıfırla
            blog.slug = f"{blog.slug}-copy"  # Slug'ı farklı yapmak için ekleme yap
            blog.title = f"{blog.title} (Copy)"  # Başlıkta kopya olduğunu belirt
            blog.save()

        self.message_user(request, f"{queryset.count()} blog başarıyla kopyalandı.")

    copy_blog.short_description = "Seçili blogları kopyala"

    actions = ['copy_blog']  # Admin actions'a kopyalama işlevini ekle

    def copy_blog_link(self, obj):
        """
        Admin panelinde her bir blog objesi için kopyalama linki.
        """
        url = reverse('admin:tuerny_app_blog_add')  # Yeni blog ekleme sayfasına yönlendir
        return format_html('<a href="{}?title={}&category={}&user={}">Kopyala</a>',
                           url, obj.title, obj.category.id if obj.category else '', obj.user.id)

    copy_blog_link.short_description = "Kopyala"
    copy_blog_link.allow_tags = True

class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'blog', 'link')
    search_fields = ('title', 'description')
    list_filter = ('blog',)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('get_user', 'content', 'created_at', 'anonymous')
    list_filter = ('anonymous', 'created_at')
    search_fields = ('content',)

    def get_user(self, obj):
        return "Anonim" if obj.anonymous else obj.user.username
    get_user.short_description = "Kullanıcı"

class SaveAdmin(admin.ModelAdmin):
    list_display = ('get_user', 'get_saved_item', 'saved_at')
    list_filter = ('saved_at',)
    search_fields = ('user__username', 'blog__title', 'question__title')

    def get_user(self, obj):
        return obj.user.username
    get_user.short_description = "Kullanıcı"

    def get_saved_item(self, obj):
        if obj.blog:
            return f"Blog: {obj.blog.title}"
        if obj.question:
            return f"Soru: {obj.question.title}"
        return "Bilinmeyen"
    get_saved_item.short_description = "Kaydedilen İçerik"

class CustomAdminSite(AdminSite):
    site_header = "Yönetim Paneli"
    site_title = "Admin Panel"
    index_title = "Hoş Geldiniz"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export-all-csv/', self.export_all_csv, name='export_all_csv'),
        ]
        return custom_urls + urls

    def export_all_csv(self, request):
        # ZIP dosyası oluşturmak için geçici bir bellek alanı
        buffer = BytesIO()
        zip_file = zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED)

        # Tüm modelleri al
        models = apps.get_models()

        for model in models:
            model_name = model._meta.verbose_name_plural
            queryset = model.objects.all()

            # CSV yazmak için StringIO kullan
            csv_buffer = StringIO()
            writer = csv.writer(csv_buffer)

            # CSV başlıkları
            fields = [field.name for field in model._meta.fields]
            writer.writerow(fields)

            # Verileri yaz
            for obj in queryset:
                writer.writerow([getattr(obj, field) for field in fields])

            # CSV dosyasını ZIP'e ekle
            csv_filename = f"{model_name}.csv"
            zip_file.writestr(csv_filename, csv_buffer.getvalue())
            csv_buffer.close()

        # ZIP dosyasını kapat
        zip_file.close()
        buffer.seek(0)

        # HTTP yanıtını döndür
        response = HttpResponse(buffer, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="all_tables.zip"'
        return response

@admin.register(SuggestedBlog)
class SuggestedBlogAdmin(admin.ModelAdmin):
    list_display = ('blog', 'is_active')  # Liste görünümünde blog başlığı ve aktiflik durumu gösterilir
    list_filter = ('is_active',)  # Filtreleme seçeneği eklenir
    search_fields = ('blog__title',)  # Blog başlığına göre arama yapılabilir
    actions = ['make_active', 'make_inactive']  # Toplu işlem butonları

    def make_active(self, request, queryset):
        queryset.update(is_active=True)
    make_active.short_description = "Seçili blogları aktif hale getir"

    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
    make_inactive.short_description = "Seçili blogları pasif hale getir"

@admin.register(CategorySuggestedBlog)
class CategorySuggestedBlogAdmin(admin.ModelAdmin):
    list_display = ('blog', 'is_active')  # Liste görünümünde blog başlığı ve aktiflik durumu gösterilir
    list_filter = ('is_active',)  # Filtreleme seçeneği eklenir
    search_fields = ('blog__title',)  # Blog başlığına göre arama yapılabilir
    actions = ['make_active', 'make_inactive']  # Toplu işlem butonları

    def make_active(self, request, queryset):
        queryset.update(is_active=True)
    make_active.short_description = "Seçili blogları aktif hale getir"

    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
    make_inactive.short_description = "Seçili blogları pasif hale getir"
# Özel admin siteyi tanımlayın
custom_admin_site = CustomAdminSite(name='custom_admin')

# Tüm modelleri admin'e ekle
models = apps.get_models()
for model in models:
    try:
        custom_admin_site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
admin.site.register(Question, QuestionAdmin)
admin.site.register(Poll, PollAdmin)
admin.site.register(MainCategory, MainCategoryAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Save, SaveAdmin)