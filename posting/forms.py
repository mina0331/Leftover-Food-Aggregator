from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["event", "event_description", "cuisine", "image", "publish_at"]
        widgets = {
            "cuisines": forms.CheckboxSelectMultiple(),
            "publish_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }
        # status is excluded and handled automatically in the view