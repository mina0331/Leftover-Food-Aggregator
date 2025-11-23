from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["role", "profile_pic", "display_name", "preferences", "allergens", "bio", "major"]
        widgets = {
            "role" : forms.RadioSelect(),
            "preferences": forms.CheckboxSelectMultiple(),
            "allergens": forms.CheckboxSelectMultiple(),
            "bio": forms.Textarea(attrs={"rows": 4}),
            "major": forms.TextInput(),
            "display_name": forms.TextInput(attrs={"maxlength": 50}),
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
        
        # Add character limit validation for display_name
        if 'display_name' in self.fields:
            self.fields['display_name'].max_length = 50
            self.fields['display_name'].help_text = "Maximum 50 characters"
    
    def clean_display_name(self):
        display_name = self.cleaned_data.get('display_name')
        if display_name and len(display_name) > 50:
            raise forms.ValidationError("Display name must be 50 characters or less.")
        return display_name