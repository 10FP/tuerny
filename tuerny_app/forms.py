from django import forms
from .models import Blog, BlogContent

class BlogPostForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ["category", "extra_categories", "title", "short_description", "media", "media_extra", "source", "author"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Blog Başlığı"}),
            "short_description": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Kısa Açıklama"}),
            "source": forms.URLInput(attrs={"class": "form-control", "placeholder": "Kaynak URL"}),
            "author": forms.TextInput(attrs={"class": "form-control", "placeholder": "Yazar Adı"}),
        }

class BlogContentForm(forms.ModelForm):
    class Meta:
        model = BlogContent
        fields = ["type", "text", "image", "video", "product"]
        widgets = {
            "type": forms.Select(attrs={"class": "form-control"}),
            "text": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "İçerik"}),
            "image": forms.FileInput(attrs={"class": "form-control"}),
            "video": forms.URLInput(attrs={"class": "form-control", "placeholder": "Video URL"}),
            "product": forms.Select(attrs={"class": "form-control"}),
        }