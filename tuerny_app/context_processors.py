from .models import MainCategory, SubCategory, Blog

def categories_context(request):
    categories = MainCategory.objects.all()
    subcategories = SubCategory.objects.all()
    blogs = Blog.objects.all()
    return {
        'categories': categories,
        'subcategories': subcategories,
        'blog': blogs
    }