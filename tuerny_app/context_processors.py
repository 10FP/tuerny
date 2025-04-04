from .models import MainCategory, SubCategory, Blog, APISettings, InstagramPost

def categories_context(request):
    categories = MainCategory.objects.all()
    subcategories = SubCategory.objects.all()
    blogs = Blog.objects.filter(status="approved")
    insta = InstagramPost.objects.order_by('-created_at')[:9]
    scripts = APISettings.objects.filter(is_active=True).values_list("script", flat=True)
    return {
        'categories': categories,
        'subcategories': subcategories,
        'blog': blogs,
        'insta': insta,
        'scriptsapi': scripts
    }

def api_scripts(request):
    scripts = APISettings.objects.filter(is_active=True).values_list("script", flat=True)
    return {"api_scripts": scripts}