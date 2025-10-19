from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
import logging
from .models import Device, SensorData, Relay
from .mqtt_manager import get_mqtt_manager, send_led_command, send_relay_command

# Setup logging
logger = logging.getLogger(__name__)

def dashboard_simple(request):
    """หน้า Dashboard แบบเรียบง่าย - ทำงานได้แน่นอน"""
    
    # Get LED device
    led_device, created = Device.objects.get_or_create(name="Onboard LED")
    
    # Get or create Relay controller
    relay_controller, created = Relay.objects.get_or_create(
        name="ESP32 Relay Controller",
        defaults={
            'relay1_status': False,
            'relay2_status': False,
            'relay3_status': False
        }
    )
    
    # Get latest sensor data
    latest_sensor = SensorData.objects.order_by('-timestamp').first()
    
    # Get recent 20 sensor data for charts
    recent_sensors = SensorData.objects.order_by('-timestamp')[:20]
    
    context = {
        'led': led_device,
        'relay': relay_controller,
        'latest_sensor': latest_sensor,
        'recent_sensors': recent_sensors,
        'current_time': timezone.now(),
        'total_readings': SensorData.objects.count(),
    }
    
    return render(request, 'iot_dashboard/dashboard_simple.html', context)

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
                
            else:
                messages.error(request, '❌ คำสั่งไม่ถูกต้อง')
                return redirect('dashboard_simple')
            
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
    
    return redirect('dashboard_simple')

def control_relay(request):
    """ควบคุม RELAY 1, 2, 3 ผ่าน MQTT Manager"""
    if request.method == 'POST':
        relay_num = request.POST.get('relay_num')  # '1', '2', '3'
        action = request.POST.get('action')  # 'on', 'off', 'toggle'
        
        relay_controller, created = Relay.objects.get_or_create(
            name="ESP32 Relay Controller",
            defaults={
                'relay1_status': False,
                'relay2_status': False,
                'relay3_status': False
            }
        )
        
        try:
            # กำหนดสถานะปัจจุบันของ relay
            if relay_num == '1':
                current_status = relay_controller.relay1_status
                relay_name = "RELAY 1"
            elif relay_num == '2':
                current_status = relay_controller.relay2_status
                relay_name = "RELAY 2"
            elif relay_num == '3':
                current_status = relay_controller.relay3_status
                relay_name = "RELAY 3"
            else:
                messages.error(request, '❌ หมายเลข Relay ไม่ถูกต้อง')
                return redirect('dashboard_simple')
            
            # กำหนดคำสั่งและสถานะใหม่
            if action == 'on':
                new_state = True
                mqtt_command = 'ON'
                success_msg = f'🟢 ส่งคำสั่งเปิด {relay_name} สำเร็จ!'
                
            elif action == 'off':
                new_state = False
                mqtt_command = 'OFF'
                success_msg = f'🔴 ส่งคำสั่งปิด {relay_name} สำเร็จ!'
                
            elif action == 'toggle':
                new_state = not current_status
                mqtt_command = 'ON' if new_state else 'OFF'
                success_msg = f'🔄 ส่งคำสั่ง Toggle {relay_name} เป็น {"เปิด" if new_state else "ปิด"}!'
            else:
                messages.error(request, '❌ คำสั่งไม่ถูกต้อง')
                return redirect('dashboard_simple')
            
            # ส่งคำสั่งผ่าน MQTT Manager
            logger.info(f"🎮 Sending RELAY {relay_num} command: {mqtt_command}")
            
            # ใช้ฟังก์ชัน send_relay_command
            success, result_msg = send_relay_command(int(relay_num), mqtt_command)
            
            if success:
                # อัพเดทสถานะใน database
                if relay_num == '1':
                    relay_controller.relay1_status = new_state
                elif relay_num == '2':
                    relay_controller.relay2_status = new_state
                elif relay_num == '3':
                    relay_controller.relay3_status = new_state
                
                relay_controller.last_updated = timezone.now()
                relay_controller.save()
                
                messages.success(request, success_msg)
                logger.info(f"✅ RELAY command successful: {mqtt_command} to RELAY {relay_num}")
            else:
                messages.error(request, f'❌ ส่งคำสั่งไม่สำเร็จ: {result_msg}')
                logger.error(f"❌ RELAY command failed: {result_msg}")
                
        except Exception as e:
            messages.error(request, f'❌ เกิดข้อผิดพลาด: {str(e)}')
            logger.error(f"❌ Error in control_relay: {e}")
    
    return redirect('dashboard_simple')

@csrf_exempt
def api_sensor_data(request):
    """API สำหรับดึงข้อมูล sensor - แบบง่าย"""
    try:
        # ดึงข้อมูล sensor ล่าสุด
        limit = int(request.GET.get('limit', 20))
        sensors = SensorData.objects.order_by('-timestamp')[:limit]
        
        data = []
        for sensor in sensors:
            data.append({
                'id': sensor.id,
                'temperature': float(sensor.temperature) if sensor.temperature is not None else None,
                'humidity': float(sensor.humidity) if sensor.humidity is not None else None,
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

@csrf_exempt
def api_chart_data(request):
    """API สำหรับดึงข้อมูลกราฟ - แบบง่าย"""
    try:
        # ดึงข้อมูลล่าสุด 50 รายการ
        sensors = SensorData.objects.order_by('-timestamp')[:50]
        
        # จัดรูปแบบข้อมูลสำหรับ Chart.js
        chart_data = {
            'labels': [],
            'temperature': [],
            'humidity': []
        }
        
        for sensor in reversed(sensors):  # เรียงจากเก่าไปใหม่
            chart_data['labels'].append(sensor.timestamp.strftime('%H:%M:%S'))
            chart_data['temperature'].append(
                float(sensor.temperature) if sensor.temperature is not None else None
            )
            chart_data['humidity'].append(
                float(sensor.humidity) if sensor.humidity is not None else None
            )
        
        # ข้อมูลล่าสุด
        latest = sensors.first() if sensors else None
        latest_data = {
            'temperature': float(latest.temperature) if latest and latest.temperature else None,
            'humidity': float(latest.humidity) if latest and latest.humidity else None,
            'timestamp': latest.timestamp.strftime('%Y-%m-%d %H:%M:%S') if latest else None
        }
        
        return JsonResponse({
            'success': True,
            'chart_data': chart_data,
            'latest': latest_data,
            'total_points': len(sensors)
        })
        
    except Exception as e:
        logger.error(f"❌ Chart Data API Error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
