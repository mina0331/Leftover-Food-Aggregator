from django import forms
from django.utils import timezone
from datetime import timedelta
from posting.models import Post
from chat.models import Message


class ModeratorPostEditForm(forms.ModelForm):
    """Form for moderators to edit flagged posts"""
    class Meta:
        model = Post
        fields = ['event', 'event_description', 'cuisine', 'image']
        widgets = {
            'event': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 100%; padding: 8px; margin-bottom: 10px;'}),
            'event_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'style': 'width: 100%; padding: 8px; margin-bottom: 10px;'}),
            'cuisine': forms.Select(attrs={'class': 'form-control', 'style': 'width: 100%; padding: 8px; margin-bottom: 10px;'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'style': 'width: 100%; padding: 8px; margin-bottom: 10px;'}),
        }


class ModeratorMessageEditForm(forms.ModelForm):
    """Form for moderators to edit flagged messages"""
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'style': 'width: 100%; padding: 8px; margin-bottom: 10px;'
            }),
        }


class SuspendUserForm(forms.Form):
    """Form for moderators to suspend a user"""
    reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 5,
            'placeholder': 'Explain why this user is being suspended...',
            'style': 'width: 100%; padding: 10px;'
        }),
        required=True,
        help_text="Required: Provide a clear reason for the suspension"
    )
    duration_days = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=365,
        help_text="Optional: Number of days for temporary suspension (leave empty for permanent)"
    )
    suspended_until = forms.DateTimeField(
        required=False,
        help_text="Optional: Specific date/time for suspension to end (leave empty for permanent)"
    )
    
    def clean(self):
        cleaned_data = super().clean()
        duration_days = cleaned_data.get('duration_days')
        suspended_until = cleaned_data.get('suspended_until')
        
        # If duration_days is provided, calculate suspended_until
        if duration_days and not suspended_until:
            cleaned_data['suspended_until'] = timezone.now() + timedelta(days=duration_days)
        
        return cleaned_data


class ReinstateUserForm(forms.Form):
    """Form for moderators to reinstate a suspended user"""
    notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Optional: Add notes about why this user is being reinstated...',
            'style': 'width: 100%; padding: 10px;'
        }),
        required=False,
        help_text="Optional: Explain why the user is being reinstated"
    )

