from django import forms
from django.contrib.auth.models import User
from .models import SupportRequest

class SupportRequestForm(forms.ModelForm):
    class Meta:
        model = SupportRequest
        fields = ['subject', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5}),
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']