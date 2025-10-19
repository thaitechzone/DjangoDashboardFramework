from django.shortcuts import render
from django.utils import timezone
from datetime import datetime
import pytz
from .models import Device, SensorData
from .mqtt_manager import get_mqtt_manager

def debug_view(request):
    """Debug view to check template data"""
    # Mirror the dashboard_view logic exactly
    led_device, created = Device.objects.get_or_create(name="Onboard LED")
    latest_sensor = SensorData.objects.order_by('-timestamp').first()
    recent_sensors = SensorData.objects.order_by('-timestamp')[:20]
    
    thai_tz = pytz.timezone('Asia/Bangkok')
    
    sensor_stats = {
        'total_readings': SensorData.objects.count(),
        'latest_temp': None,
        'latest_humidity': None,
        'temp_stats': {'min': 0, 'max': 0, 'avg': 0},
        'humidity_stats': {'min': 0, 'max': 0, 'avg': 0}
    }
    
    if latest_sensor:
        sensor_stats['latest_temp'] = latest_sensor.temperature
        sensor_stats['latest_humidity'] = latest_sensor.humidity
    
    # Calculate temperature statistics
    temp_data = SensorData.objects.filter(temperature__isnull=False).order_by('-timestamp')[:50]
    if temp_data.exists():
        temps = [s.temperature for s in temp_data]
        sensor_stats['temp_stats'] = {
            'min': min(temps),
            'max': max(temps),
            'avg': sum(temps) / len(temps)
        }
    
    # Calculate humidity statistics  
    humidity_data = SensorData.objects.filter(humidity__isnull=False).order_by('-timestamp')[:50]
    if humidity_data.exists():
        humidities = [s.humidity for s in humidity_data]
        sensor_stats['humidity_stats'] = {
            'min': min(humidities),
            'max': max(humidities),
            'avg': sum(humidities) / len(humidities)
        }
    
    mqtt_manager = get_mqtt_manager()
    mqtt_status = mqtt_manager.get_status()
    
    context = {
        'led': led_device,
        'latest_sensor': latest_sensor,
        'recent_sensors': recent_sensors,
        'sensor_stats': sensor_stats,
        'mqtt_status': mqtt_status,
        'last_updated': timezone.now().astimezone(thai_tz).strftime("%d/%m/%Y %H:%M:%S"),
        'current_time': timezone.now().astimezone(thai_tz),
        'thai_tz': thai_tz,
    }
    
    return render(request, 'iot_dashboard/debug.html', context)