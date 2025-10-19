#!/usr/bin/env python
"""
Test script to verify chart data and views
"""
import os
import django
from datetime import datetime, timedelta
import pytz

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_project.settings')
django.setup()

from django.utils import timezone
from iot_dashboard.models import SensorData
from iot_dashboard.views import dashboard_view
from django.test import RequestFactory

print("🧪 Chart Data Testing Script")
print("=" * 50)

# Test 1: Check raw data
print("1️⃣ Testing raw sensor data:")
latest_20 = SensorData.objects.order_by('-timestamp')[:20]
print(f"   Total records: {SensorData.objects.count()}")
print(f"   Latest 20 records: {len(latest_20)}")

if latest_20:
    thai_tz = pytz.timezone('Asia/Bangkok')
    print("   Sample data:")
    for i, sensor in enumerate(latest_20[:3], 1):
        thai_time = sensor.timestamp.astimezone(thai_tz)
        print(f"   {i}. {thai_time.strftime('%H:%M:%S')} - Temp: {sensor.temperature}°C, Hum: {sensor.humidity}%")

# Test 2: Test template filter
print("\n2️⃣ Testing template filter:")
from iot_dashboard.templatetags.timezone_filters import thai_time_format

if latest_20:
    sample = latest_20[0]
    formatted = thai_time_format(sample.timestamp, "%H:%M:%S")
    print(f"   Original: {sample.timestamp}")
    print(f"   Formatted: {formatted}")

# Test 3: Test view function
print("\n3️⃣ Testing view function:")
from django.template.response import TemplateResponse

try:
    # Import the view function
    from iot_dashboard.views import dashboard_view
    
    # Create a mock request
    factory = RequestFactory()
    request = factory.get('/')
    
    # Call the view function directly
    response = dashboard_view(request)
    print(f"   View response status: {response.status_code}")
    print(f"   View response type: {type(response)}")
    
    # Extract context data from TemplateResponse
    if isinstance(response, TemplateResponse):
        context = response.context_data
        print(f"   Context keys: {list(context.keys()) if context else 'No context'}")
        
        if 'recent_sensors' in context:
            recent_sensors = context['recent_sensors']
            print(f"   Recent sensors in context: {len(recent_sensors) if recent_sensors else 0}")
            if recent_sensors:
                print(f"   First sensor: {recent_sensors[0]}")
        else:
            print("   ⚠️ No recent_sensors in context")
    else:
        print("   ⚠️ Response is not TemplateResponse")

except Exception as e:
    print(f"   ❌ Error calling view: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Generate JavaScript-like data
print("\n4️⃣ Generating JavaScript data structure:")
js_data = []
for sensor in latest_20:
    thai_time = sensor.timestamp.astimezone(pytz.timezone('Asia/Bangkok'))
    js_data.append({
        'timestamp': thai_time.strftime('%H:%M:%S'),
        'temperature': float(sensor.temperature) if sensor.temperature else None,
        'humidity': float(sensor.humidity) if sensor.humidity else None
    })

print(f"   Generated {len(js_data)} data points")
if js_data:
    print("   Sample JS data:")
    for i, item in enumerate(js_data[:3], 1):
        print(f"   {i}. {item}")

# Test 5: Chart data validation
print("\n5️⃣ Chart data validation:")
temp_data = [item for item in js_data if item['temperature'] is not None]
hum_data = [item for item in js_data if item['humidity'] is not None]

print(f"   Valid temperature points: {len(temp_data)}")
print(f"   Valid humidity points: {len(hum_data)}")

if len(temp_data) > 0 and len(hum_data) > 0:
    print("   ✅ Sufficient data for charts")
else:
    print("   ❌ Insufficient data for charts")

print("\n🎯 Test completed!")
print("   If charts still don't show, check browser console for JavaScript errors.")