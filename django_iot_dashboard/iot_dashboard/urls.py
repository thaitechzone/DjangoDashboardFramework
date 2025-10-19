from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('control-led/', views.control_led, name='control_led'),
    path('api/control-led/', views.api_control_led, name='api_control_led'),
    path('api/sensor-data/', views.api_sensor_data, name='api_sensor_data'),
    path('api/mqtt-status/', views.api_mqtt_status, name='api_mqtt_status'),
]