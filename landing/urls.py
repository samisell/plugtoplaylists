from django.urls import path
from . import views
from .views import fetch_song_details

app_name = 'landing'

urlpatterns = [
    path('', views.landing_page, name='index'),
    path('terms/', views.terms_page, name='terms_page'),
    path('privacy/', views.privacy_page, name='privacy_page'),
    path('submit-song/', views.submit_song, name='submit_song'),
    path('submitted/', views.submitted_page, name='submitted_song'),
    path('fetch-song-details/', fetch_song_details, name='fetch_song_details'),
]