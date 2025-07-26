from django.db import models
from django.contrib.auth.models import User
from payment.models import Package  # Make sure this import works

class SongSubmission(models.Model):
    """Model representing song submissions"""
    GENRE_CHOICES = [
        ('pop', 'Pop'),
        ('hiphop', 'Hip Hop/Rap'),
        ('rnb', 'R&B'),
        ('edm', 'Electronic/Dance'),
        ('rock', 'Rock'),
        ('alternative', 'Alternative'),
        ('country', 'Country'),
        ('jazz', 'Jazz'),
        ('classical', 'Classical'),
        ('other', 'Other'),
    ]

    LINK_TYPE_CHOICES = [
        ('spotify', 'Spotify'),
        ('youtube', 'YouTube Music'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    # User information
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Song details
    artist_name = models.CharField(max_length=100)
    song_title = models.CharField(max_length=100)
    genre = models.CharField(max_length=50, choices=GENRE_CHOICES)
    
    # Media links
    link_type = models.CharField(max_length=20, choices=LINK_TYPE_CHOICES)
    music_link = models.URLField()
    song_file = models.FileField(
        upload_to='song_submissions/%Y/%m/%d/',
        null=True,
        blank=True,
        help_text="Upload your song file if you don't have a streaming link"
    )
    
    # Contact information
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    social_media = models.CharField(
        max_length=100,
        blank=True,
        help_text="Your Instagram/Twitter handle"
    )
    
    # Additional information
    bio = models.TextField(
        blank=True,
        help_text="Tell us about yourself and your music"
    )
    
    # Submission metadata
    submission_date = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    notes = models.TextField(
        blank=True,
        help_text="Internal notes about this submission"
    )
    
    # Payment information
    package = models.ForeignKey(
        Package,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Selected package for this submission"
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    transaction_reference = models.CharField(
        max_length=100,
        blank=True,
        help_text="Flutterwave transaction reference"
    )
    payment_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When payment was completed"
    )

    def __str__(self):
        return f"{self.artist_name} - {self.song_title}"

    class Meta:
        ordering = ['-submission_date']
        verbose_name = "Song Submission"
        verbose_name_plural = "Song Submissions"
        indexes = [
            models.Index(fields=['artist_name']),
            models.Index(fields=['song_title']),
            models.Index(fields=['submission_date']),
            models.Index(fields=['payment_status']),
        ]

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('submission_detail', kwargs={'pk': self.pk})