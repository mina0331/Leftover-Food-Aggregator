from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["role", "profile_pic", "display_name", "preferences"]
        widgets = {
            "role" : forms.RadioSelect(),
            "preferences": forms.CheckboxSelectMultiple(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exclude MODERATOR role from regular user selection
        # Moderators can only be assigned by admins
        if 'role' in self.fields:
            # Get current choices excluding MODERATOR
            choices = list(Profile.Role.choices)
            # Filter out MODERATOR choice
            filtered_choices = [(value, label) for value, label in choices if value != 'moderator']
            self.fields['role'].choices = filtered_choices