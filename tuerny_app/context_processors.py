from .models import MainCategory, SubCategory, Blog, APISettings

def categories_context(request):
    categories = MainCategory.objects.all()
    subcategories = SubCategory.objects.all()
    blogs = Blog.objects.all()
    return {
        'categories': categories,
        'subcategories': subcategories,
        'blog': blogs
    }

def api_scripts(request):
    scripts = APISettings.objects.filter(is_active=True).values_list("script", flat=True)
    return {"api_scripts": scripts}