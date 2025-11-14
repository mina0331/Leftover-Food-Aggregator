from django import forms
from .models import Post, Location

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        widgets = {"cuisines": forms.CheckboxSelectMultiple()}
        exclude = ("author", "created_at", "updated_at", "read_users")  # author not shown


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ["location_name"]