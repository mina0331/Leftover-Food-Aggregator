from django import forms
from .models import Post
from .models import Report


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        widgets = {"cuisines": forms.CheckboxSelectMultiple()}
        exclude = ("author", "created_at", "updated_at")  # author not shown

class ReportForm(forms.ModelForm):
    class Meta: 
        model = Report 
        fields = ["reason", "description"]
        widgets = {
            "reason": forms.Select(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Describe what you saw (optional)"}),
        }