# forms.py
from django import forms
from .models import Post, Location, Report

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["event", "event_description", "cuisine", "image", "location", "publish_at"]
        widgets = {
            "cuisines": forms.CheckboxSelectMultiple(),
            "publish_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }
        # status is excluded and handled automatically in the view

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # nice label and ordering
        if "location" in self.fields:
            self.fields["location"].label = "UVA Building"
            self.fields["location"].queryset = Location.objects.order_by("building_name")

class ReportForm(forms.ModelForm):
    class Meta: 
        model = Report 
        fields = ["reason", "description"]
        widgets = {
            "reason": forms.Select(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Describe what you saw (optional)"}),
        }
