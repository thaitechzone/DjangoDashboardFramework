from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('control/led/', views.control_led, name='control_led'),
    path('api/control/led/', views.api_control_led, name='api_control_led'),
]