# forms.py
from django import forms
from .models import Post, Location, RSVP

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["event", "event_description", "cuisine", "image", "location", "publish_at", "pickup_deadline"]
        widgets = {
            "cuisines": forms.CheckboxSelectMultiple(),
            "publish_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "pickup_deadline": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            'image': forms.FileInput(attrs={
                'id': 'imageInput',
                'style': 'display:none;',  
                'accept': 'image/*'  
            }),
        }
        # status is excluded and handled automatically in the view

    def clean_image(self):
        pic = self.cleaned_data.get("image")

        # If no new file was uploaded → skip validation
        if not pic or not hasattr(pic, "content_type"):
            return pic

        # Validate MIME type
        if pic.content_type not in ["image/jpeg", "image/png"]:
            raise forms.ValidationError("Only JPEG and PNG files are allowed.")

        # Validate size (5MB limit)
        if pic.size > 5 * 1024 * 1024:
            raise forms.ValidationError("File too large! Maximum size is 5MB.")

        return pic
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields required except publish_at and pickup_deadline (which are optional)
        self.fields["event"].required = True
        self.fields["event_description"].required = True
        self.fields["cuisine"].required = True
        self.fields["image"].required = True
        self.fields["location"].required = True
        # publish_at and pickup_deadline remain optional
        
        # nice label and ordering
        if "location" in self.fields:
            self.fields["location"].label = "UVA Building"
            self.fields["location"].queryset = Location.objects.order_by("building_name")
        if "pickup_deadline" in self.fields:
            self.fields["pickup_deadline"].label = "Pickup Deadline (Optional)"
            self.fields["pickup_deadline"].help_text = "When will you stop giving out food? Leave empty if no specific deadline."


class RSVPForm(forms.ModelForm):
    """Form for users to RSVP to pick up food"""
    class Meta:
        model = RSVP
        fields = ['estimated_arrival_minutes']
        widgets = {
            'estimated_arrival_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '300',
                'placeholder': 'Minutes until arrival (1-300)',
                'style': 'width: 100%; padding: 10px; margin-bottom: 10px;'
            }),
        }
        labels = {
            'estimated_arrival_minutes': 'Estimated Arrival Time (minutes)',
        }
        help_texts = {
            'estimated_arrival_minutes': 'How many minutes until you arrive? (1-300 minutes)',
        }

    def clean_estimated_arrival_minutes(self):
        minutes = self.cleaned_data.get('estimated_arrival_minutes')
        if minutes < 1 or minutes > 300:
            raise forms.ValidationError('Estimated arrival time must be between 1 and 300 minutes.')
        return minutes
