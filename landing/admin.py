from django.contrib import admin
from .models import SongSubmission

@admin.register(SongSubmission)
class SongSubmissionAdmin(admin.ModelAdmin):
    list_display = ('artist_name', 'song_title', 'genre', 'email', 'submission_date', 'is_approved')
    list_filter = ('genre', 'is_approved')
    search_fields = ('artist_name', 'song_title', 'email')