from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('process/', views.process_payment, name='process'),
    path('verify/', views.verify_payment, name='verify'),
]