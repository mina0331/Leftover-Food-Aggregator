from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["role", "profile_pic", "display_name"]
        widgets = {
            "role" : forms.RadioSelect(),
        }