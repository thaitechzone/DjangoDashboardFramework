from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import paho.mqtt.client as mqtt
import json
import time
from .models import Device

# MQTT Configuration
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
LED_CONTROL_TOPIC = "thaitechzone/v2_board/control/led"
LED_STATUS_TOPIC = "thaitechzone/v2_board/state/led"

def dashboard_view(request):
    """แสดงหน้า Dashboard หลัก"""
    # Get the LED device object. Use get_or_create to avoid errors on first run.
    led_device, created = Device.objects.get_or_create(name="Onboard LED")
    
    context = {
        'led': led_device,
        'last_updated': timezone.now().strftime("%d/%m/%Y %H:%M:%S"),
    }
    return render(request, 'iot_dashboard/dashboard.html', context)

def control_led(request):
    """ควบคุม LED ผ่าน MQTT"""
    if request.method == 'POST':
        action = request.POST.get('action')
        
        try:
            # สร้าง MQTT client
            client = mqtt.Client()
            
            # เชื่อมต่อกับ MQTT broker
            client.connect(MQTT_BROKER, MQTT_PORT, 60)
            
            # ส่งคำสั่งตาม action
            if action == 'on':
                client.publish(LED_CONTROL_TOPIC, 'ON', qos=1)
                # อัพเดทใน database ด้วย
                led_device, created = Device.objects.get_or_create(name="Onboard LED")
                led_device.is_on = True
                led_device.save()
                messages.success(request, '🟢 ส่งคำสั่งเปิด LED สำเร็จ!')
                
            elif action == 'off':
                client.publish(LED_CONTROL_TOPIC, 'OFF', qos=1)
                # อัพเดทใน database ด้วย
                led_device, created = Device.objects.get_or_create(name="Onboard LED")
                led_device.is_on = False
                led_device.save()
                messages.success(request, '⚫ ส่งคำสั่งปิด LED สำเร็จ!')
            
            elif action == 'toggle':
                # ตัวเองเปลี่ยนสถานะ
                led_device, created = Device.objects.get_or_create(name="Onboard LED")
                new_state = not led_device.is_on
                command = 'ON' if new_state else 'OFF'
                
                client.publish(LED_CONTROL_TOPIC, command, qos=1)
                led_device.is_on = new_state
                led_device.save()
                
                status_msg = 'เปิด' if new_state else 'ปิด'
                messages.success(request, f'🔄 ส่งคำสั่ง{status_msg} LED สำเร็จ!')
            
            # รอให้ message ส่ง
            time.sleep(0.1)
            client.disconnect()
            
        except Exception as e:
            messages.error(request, f'❌ เกิดข้อผิดพลาด: {str(e)}')
            
    return redirect('dashboard')

@csrf_exempt
def api_control_led(request):
    """API สำหรับควบคุม LED (สำหรับ AJAX calls)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            action = data.get('action')
            
            # สร้าง MQTT client
            client = mqtt.Client()
            client.connect(MQTT_BROKER, MQTT_PORT, 60)
            
            if action == 'on':
                client.publish(LED_CONTROL_TOPIC, 'ON', qos=1)
                led_device, created = Device.objects.get_or_create(name="Onboard LED")
                led_device.is_on = True
                led_device.save()
                
            elif action == 'off':
                client.publish(LED_CONTROL_TOPIC, 'OFF', qos=1)
                led_device, created = Device.objects.get_or_create(name="Onboard LED")
                led_device.is_on = False
                led_device.save()
            
            elif action == 'toggle':
                led_device, created = Device.objects.get_or_create(name="Onboard LED")
                new_state = not led_device.is_on
                command = 'ON' if new_state else 'OFF'
                
                client.publish(LED_CONTROL_TOPIC, command, qos=1)
                led_device.is_on = new_state
                led_device.save()
            
            time.sleep(0.1)
            client.disconnect()
            
            # ส่งข้อมูลกลับ
            led_device, created = Device.objects.get_or_create(name="Onboard LED")
            return JsonResponse({
                'success': True,
                'status': led_device.is_on,
                'message': f'LED is now {"ON" if led_device.is_on else "OFF"}'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
