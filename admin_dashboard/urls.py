from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    # Add login URL at the top
    path('login/', views.admin_login, name='login'),
    
    # Existing URLs
    path('', views.dashboard_home, name='home'),
    
    # Song submission management
    path('songs/', views.song_list, name='song_list'),
    path('songs/<int:song_id>/', views.song_detail, name='song_detail'),
    path('songs/<int:song_id>/approve/', views.song_approve, name='song_approve'),
    path('songs/<int:song_id>/reject/', views.song_reject, name='song_reject'),
    
    # Payment management
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/<int:payment_id>/', views.payment_detail, name='payment_detail'),
    
    # Package management
    path('packages/', views.package_list, name='package_list'),
    path('packages/add/', views.package_add, name='package_add'),
    path('packages/<int:package_id>/edit/', views.package_edit, name='package_edit'),
    path('packages/<int:package_id>/delete/', views.package_delete, name='package_delete'),
    
    # Analytics
    path('analytics/', views.analytics, name='analytics'),
]