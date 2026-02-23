from django.urls import path
from . import views
from . import views_simple

urlpatterns = [
    # Main dashboard
    path('', views_simple.dashboard_simple, name='dashboard_simple'),
    
    # AI Agent Dashboard
    path('ai/', views_simple.ai_dashboard, name='ai_dashboard'),
    
    # Original complex dashboard
    path('complex/', views.dashboard_view, name='dashboard'),
    
    # LED Control (Web Form)
    path('control-led/', views_simple.control_led, name='control_led'),
    
    # Relay Control (Web Form)
    path('control-relay/', views_simple.control_relay, name='control_relay'),
    
    # Original API Endpoints
    path('api/control-led/', views.api_control_led, name='api_control_led'),
    path('api/control-relay/', views.api_control_relay, name='api_control_relay'),
    path('api/sensor-data/', views_simple.api_sensor_data, name='api_sensor_data'),
    path('api/chart-data/', views_simple.api_chart_data, name='api_chart_data'),
    path('api/mqtt-status/', views.api_mqtt_status, name='api_mqtt_status'),
    
    # ============================================
    # REST API Endpoints for Postman
    # ============================================
    
    # LED API
    path('api/v1/led/', views_simple.api_led_status, name='api_v1_led_status'),
    
    # Relay API
    path('api/v1/relay/', views_simple.api_relay_status, name='api_v1_relay_status'),
    
    # Sensor API
    path('api/v1/sensors/', views_simple.api_sensors_list, name='api_v1_sensors_list'),
    path('api/v1/sensors/latest/', views_simple.api_sensors_latest, name='api_v1_sensors_latest'),
    path('api/v1/sensors/stats/', views_simple.api_sensors_stats, name='api_v1_sensors_stats'),
    path('api/v1/sensors/<int:sensor_id>/', views_simple.api_sensor_detail, name='api_v1_sensor_detail'),
    
    # System Status API
    path('api/v1/system/status/', views_simple.api_system_status, name='api_v1_system_status'),
    
    # Threshold Management API
    path('api/v1/threshold/', views_simple.api_threshold_settings, name='api_v1_threshold_settings'),
    path('api/v1/threshold/check/', views_simple.api_threshold_check, name='api_v1_threshold_check'),
    path('api/v1/threshold/reset/', views_simple.api_threshold_reset, name='api_v1_threshold_reset'),
    
    # AI Agent API
    path('api/v1/ai/status/', views_simple.api_ai_status, name='api_v1_ai_status'),
    path('api/v1/ai/decisions/', views_simple.api_ai_decisions, name='api_v1_ai_decisions'),
    path('api/v1/ai/analyze-now/', views_simple.api_ai_analyze_now, name='api_v1_ai_analyze_now'),
    path('api/v1/ai/stats/', views_simple.api_ai_stats, name='api_v1_ai_stats'),
]
