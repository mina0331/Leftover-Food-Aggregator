from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        widgets = {"cuisines": forms.CheckboxSelectMultiple()}
        exclude = ("author", "created_at", "updated_at")  # author not shown