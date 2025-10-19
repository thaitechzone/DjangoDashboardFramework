from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
import logging
from .models import Device, SensorData
from .mqtt_manager import get_mqtt_manager, send_led_command

# Setup logging
logger = logging.getLogger(__name__)

def dashboard(request):
    """หน้า Dashboard หลัก"""
    # ดึงข้อมูลอุปกรณ์
    devices = Device.objects.all()
    
    # ดึงข้อมูล sensor ล่าสุด 10 รายการ
    recent_sensors = SensorData.objects.order_by('-timestamp')[:10]
    
    # ดึงข้อมูลสถิติ sensor
    sensor_stats = {
        'total_readings': SensorData.objects.count(),
        'latest_temp': None,
        'latest_humidity': None
    }
    
    latest_sensor = SensorData.objects.order_by('-timestamp').first()
    if latest_sensor:
        sensor_stats['latest_temp'] = latest_sensor.temperature
        sensor_stats['latest_humidity'] = latest_sensor.humidity
    
    # ได้รับสถานะ MQTT Manager
    mqtt_manager = get_mqtt_manager()
    mqtt_status = mqtt_manager.get_status()
    
    context = {
        'devices': devices,
        'recent_sensors': recent_sensors,
        'sensor_stats': sensor_stats,
        'mqtt_status': mqtt_status,
    }
    
    return render(request, 'iot_dashboard/dashboard.html', context)

def dashboard_view(request):
    """แสดงหน้า Dashboard หลัก"""
    # Get the LED device object. Use get_or_create to avoid errors on first run.
    led_device, created = Device.objects.get_or_create(name="Onboard LED")
    
    # Get latest sensor data
    latest_sensor = SensorData.objects.order_by('-timestamp').first()
    
    # Get recent sensor data for charts (last 10 readings)
    recent_sensors = SensorData.objects.order_by('-timestamp')[:10]
    
    # ได้รับสถานะ MQTT Manager
    mqtt_manager = get_mqtt_manager()
    mqtt_status = mqtt_manager.get_status()
    
    context = {
        'led': led_device,
        'latest_sensor': latest_sensor,
        'recent_sensors': recent_sensors,
        'mqtt_status': mqtt_status,
        'last_updated': timezone.now().strftime("%d/%m/%Y %H:%M:%S"),
    }
    return render(request, 'iot_dashboard/dashboard.html', context)

def control_led(request):
    """ควบคุม LED ผ่าน MQTT Manager"""
    if request.method == 'POST':
        action = request.POST.get('action')
        
        led_device, created = Device.objects.get_or_create(name="Onboard LED")
        
        try:
            # กำหนดคำสั่งและสถานะใหม่
            if action == 'on':
                command = 'ON'
                new_state = True
                success_msg = '🟢 ส่งคำสั่งเปิด LED สำเร็จ!'
                
            elif action == 'off':
                command = 'OFF'
                new_state = False
                success_msg = '🔴 ส่งคำสั่งปิด LED สำเร็จ!'
                
            elif action == 'toggle':
                new_state = not led_device.is_on
                command = 'ON' if new_state else 'OFF'
                success_msg = f'🔄 ส่งคำสั่ง Toggle LED เป็น {"เปิด" if new_state else "ปิด"}!'
            else:
                messages.error(request, '❌ คำสั่งไม่ถูกต้อง')
                return redirect('dashboard')
            
            # ส่งคำสั่งผ่าน MQTT Manager
            logger.info(f"🎮 Sending command: {command}")
            success, result_msg = send_led_command(command)
            
            if success:
                # อัพเดทสถานะใน database
                led_device.is_on = new_state
                led_device.last_updated = timezone.now()
                led_device.save()
                
                messages.success(request, success_msg)
                logger.info(f"✅ LED command successful: {command}")
            else:
                messages.error(request, f'❌ ส่งคำสั่งไม่สำเร็จ: {result_msg}')
                logger.error(f"❌ LED command failed: {result_msg}")
                
        except Exception as e:
            messages.error(request, f'❌ เกิดข้อผิดพลาด: {str(e)}')
            logger.error(f"❌ Error in control_led: {e}")
    
    return redirect('dashboard')

@csrf_exempt
def api_control_led(request):
    """API สำหรับควบคุม LED (สำหรับ AJAX calls)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            action = data.get('action')
            
            led_device, created = Device.objects.get_or_create(name="Onboard LED")
            
            # กำหนดคำสั่งและสถานะใหม่
            if action == 'on':
                command = 'ON'
                new_state = True
            elif action == 'off':
                command = 'OFF'
                new_state = False
            elif action == 'toggle':
                new_state = not led_device.is_on
                command = 'ON' if new_state else 'OFF'
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid action'
                })
            
            # ส่งคำสั่ง MQTT ผ่าน Manager
            logger.info(f"🎮 API Sending command: {command}")
            success, result_msg = send_led_command(command)
            
            if success:
                # อัพเดทสถานะใน database
                led_device.is_on = new_state
                led_device.last_updated = timezone.now()
                led_device.save()
                
                return JsonResponse({
                    'success': True,
                    'status': led_device.is_on,
                    'message': f'LED is now {"ON" if led_device.is_on else "OFF"}',
                    'command_sent': command
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': result_msg
                })
            
        except Exception as e:
            logger.error(f"❌ API Error: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def api_sensor_data(request):
    """API สำหรับดึงข้อมูล sensor"""
    try:
        # ดึงข้อมูล sensor ล่าสุด
        limit = int(request.GET.get('limit', 10))
        sensors = SensorData.objects.order_by('-timestamp')[:limit]
        
        data = []
        for sensor in sensors:
            data.append({
                'id': sensor.id,
                'temperature': float(sensor.temperature),
                'humidity': float(sensor.humidity),
                'timestamp': sensor.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'device_name': sensor.device_name
            })
        
        return JsonResponse({
            'success': True,
            'data': data,
            'count': len(data)
        })
        
    except Exception as e:
        logger.error(f"❌ API Error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

def api_mqtt_status(request):
    """API สำหรับตรวจสอบสถานะ MQTT Manager"""
    try:
        mqtt_manager = get_mqtt_manager()
        status = mqtt_manager.get_status()
        
        return JsonResponse({
            'success': True,
            'mqtt_status': status
        })
        
    except Exception as e:
        logger.error(f"❌ MQTT Status API Error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })