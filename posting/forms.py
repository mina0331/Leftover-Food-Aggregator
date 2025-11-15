# forms.py
from django import forms
from .models import Post, Location

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        widgets = {
            "cuisines": forms.CheckboxSelectMultiple(),
        }
        exclude = ("author", "created_at", "updated_at", "read_users")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # nice label and ordering
        self.fields["location"].label = "UVA Building"
        self.fields["location"].queryset = Location.objects.order_by("building_name")