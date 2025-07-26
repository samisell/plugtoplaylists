from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [
    # Registration and login
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Password reset
    path('password_reset/', 
         views.CustomPasswordResetView.as_view(), 
         name='password_reset'),
    path('password_reset/done/', 
         views.CustomPasswordResetDoneView.as_view(), 
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
         views.CustomPasswordResetConfirmView.as_view(), 
         name='password_reset_confirm'),
    path('reset/done/', 
         views.CustomPasswordResetCompleteView.as_view(), 
         name='password_reset_complete'),
    
    # Password change
    path('password_change/', 
         views.password_change_view, 
         name='password_change'),
    path('password_change/done/', 
         views.password_change_done_view, 
         name='password_change_done'),
]