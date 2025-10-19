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

def send_mqtt_command(topic, message):
    """ฟังก์ชันสำหรับส่งคำสั่ง MQTT อย่างปลอดภัย"""
    try:
        # สร้าง MQTT client ใหม่
        client = mqtt.Client(client_id=f"DjangoDashboard_{int(time.time())}")
        
        # ตั้งค่า callback functions
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                logger.info(f"✅ Connected to MQTT broker successfully")
                # ส่งข้อความทันทีหลังจากเชื่อมต่อ
                result = client.publish(topic, message, qos=1, retain=True)
                logger.info(f"📤 Published message: {topic} -> {message}")
                logger.info(f"📊 Publish result: {result}")
            else:
                logger.error(f"❌ Failed to connect to MQTT broker, code: {rc}")
        
        def on_publish(client, userdata, mid):
            logger.info(f"✅ Message published successfully (mid: {mid})")
        
        def on_disconnect(client, userdata, rc):
            logger.info(f"👋 Disconnected from MQTT broker")
        
        # ตั้งค่า callback functions
        client.on_connect = on_connect
        client.on_publish = on_publish
        client.on_disconnect = on_disconnect
        
        # เชื่อมต่อกับ MQTT broker
        logger.info(f"🔄 Connecting to {MQTT_BROKER}:{MQTT_PORT}...")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        
        # รอให้เชื่อมต่อและส่งข้อความ
        client.loop_start()
        time.sleep(2)  # รอให้การเชื่อมต่อและการส่งข้อความเสร็จ
        client.loop_stop()
        client.disconnect()
        
        return True, "Command sent successfully"
        
    except Exception as e:
        error_msg = f"❌ MQTT Error: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

def dashboard_view(request):
    """แสดงหน้า Dashboard หลัก"""
    # Get the LED device object. Use get_or_create to avoid errors on first run.
    led_device, created = Device.objects.get_or_create(name="Onboard LED")
    
    # Get latest sensor data
    latest_sensor = SensorData.objects.first()
    
    # Get recent sensor data for charts (last 10 readings)
    recent_sensors = SensorData.objects.all()[:10]
    
    context = {
        'led': led_device,
        'latest_sensor': latest_sensor,
        'recent_sensors': recent_sensors,
        'last_updated': timezone.now().strftime("%d/%m/%Y %H:%M:%S"),
    }
    return render(request, 'iot_dashboard/dashboard.html', context)

def control_led(request):
    """ควบคุม LED ผ่าน MQTT"""
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
                success_msg = '⚫ ส่งคำสั่งปิด LED สำเร็จ!'
                
            elif action == 'toggle':
                new_state = not led_device.is_on
                command = 'ON' if new_state else 'OFF'
                status_text = 'เปิด' if new_state else 'ปิด'
                success_msg = f'🔄 ส่งคำสั่ง{status_text} LED สำเร็จ!'
                
            else:
                messages.error(request, '❌ คำสั่งไม่ถูกต้อง!')
                return redirect('dashboard')
            
            # ส่งคำสั่ง MQTT
            logger.info(f"🎮 Sending command: {command} to {LED_CONTROL_TOPIC}")
            success, result_msg = send_mqtt_command(LED_CONTROL_TOPIC, command)
            
            if success:
                # อัพเดทสถานะใน database หากส่งสำเร็จ
                led_device.is_on = new_state
                led_device.last_updated = timezone.now()
                led_device.save()
                
                messages.success(request, success_msg)
                logger.info(f"✅ LED control successful: {command}")
            else:
                messages.error(request, f'❌ เกิดข้อผิดพลาด: {result_msg}')
                logger.error(f"❌ LED control failed: {result_msg}")
            
        except Exception as e:
            error_msg = f'❌ เกิดข้อผิดพลาดไม่คาดคิด: {str(e)}'
            messages.error(request, error_msg)
            logger.error(f"❌ Unexpected error in control_led: {e}")
            
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
            
            # ส่งคำสั่ง MQTT
            logger.info(f"🎮 API Sending command: {command}")
            success, result_msg = send_mqtt_command(LED_CONTROL_TOPIC, command)
            
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


@csrf_exempt
def api_sensor_data(request):
    """API สำหรับรับข้อมูล sensor จาก ESP32"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            temperature = data.get('temperature')
            humidity = data.get('humidity')
            device_name = data.get('device_name', 'ESP32_DHT22')
            
            # บันทึกข้อมูลลง database
            sensor_data = SensorData.objects.create(
                device_name=device_name,
                temperature=temperature,
                humidity=humidity,
                timestamp=timezone.now()
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Sensor data saved successfully',
                'id': sensor_data.id,
                'timestamp': sensor_data.get_timestamp_thai()
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    elif request.method == 'GET':
        # ส่งข้อมูล sensor ล่าสุด
        try:
            latest_sensor = SensorData.objects.first()
            if latest_sensor:
                return JsonResponse({
                    'success': True,
                    'data': {
                        'temperature': latest_sensor.temperature,
                        'humidity': latest_sensor.humidity,
                        'timestamp': latest_sensor.get_timestamp_thai(),
                        'temperature_display': latest_sensor.get_temperature_display(),
                        'humidity_display': latest_sensor.get_humidity_display()
                    }
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'No sensor data available'
                })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
