from django.urls import path
from . import views
from . import views_simple
from .debug_views import debug_view
from django.shortcuts import render

def test_view(request):
    return render(request, 'iot_dashboard/test.html')

urlpatterns = [
    # Simple dashboard (recommended)
    path('', views_simple.dashboard_simple, name='dashboard_simple'),
    
    # Original complex dashboard (backup)
    path('complex/', views.dashboard_view, name='dashboard'),
    
    # Debug and test pages
    path('debug/', debug_view, name='debug'),
    path('test/', test_view, name='test'),
    
    # LED Control
    path('control-led/', views_simple.control_led, name='control_led'),
    
    # API Endpoints
    path('api/control-led/', views.api_control_led, name='api_control_led'),
    path('api/sensor-data/', views_simple.api_sensor_data, name='api_sensor_data'),
    path('api/chart-data/', views_simple.api_chart_data, name='api_chart_data'),
    path('api/mqtt-status/', views.api_mqtt_status, name='api_mqtt_status'),
]