from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('my-songs/', views.my_songs, name='my_songs'),
    path('my-payments/', views.my_payments, name='my_payments'),
    path('support/', views.support, name='support'),
    path('support/new/', views.create_support_request, name='create_support_request'),
    path('support/<int:request_id>/', views.support_detail, name='support_detail'),
    path('profile/', views.profile, name='profile'),
    path('submit-song/ajax/', views.ajax_submit_song, name='ajax_submit_song'),  # New URL for AJAX submission
    path('submit-song/', views.dashboard_submit_song, name='submit_song'),
]