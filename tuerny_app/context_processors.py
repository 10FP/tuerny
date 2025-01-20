from .models import MainCategory, SubCategory

def categories_context(request):
    categories = MainCategory.objects.all()
    subcategories = SubCategory.objects.all()
    return {
        'categories': categories,
        'subcategories': subcategories,
    }