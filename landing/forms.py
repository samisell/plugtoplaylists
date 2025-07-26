from django import forms
from .models import SongSubmission
from payment.models import Package

class SongSubmissionForm(forms.ModelForm):
    link_type = forms.ChoiceField(
        choices=SongSubmission.LINK_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'link-type-selector'}),
        initial='spotify'
    )
    
    package = forms.ModelChoiceField(
        queryset=Package.objects.filter(is_active=True),
        empty_label="Select a package",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    
    terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='I agree to the terms and conditions'
    )
    
    class Meta:
        model = SongSubmission
        fields = [
            'artist_name',
            'song_title',
            'genre',
            'link_type',
            'music_link',
            'song_file',
            'email',
            'phone',
            'social_media',
            'bio',
            'package',
            'terms'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'song_file': 'Or upload your song file (optional)',
        }