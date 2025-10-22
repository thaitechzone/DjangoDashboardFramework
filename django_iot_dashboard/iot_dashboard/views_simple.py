from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
import logging
import pytz
from .models import Device, SensorData, Relay, ThresholdSetting
from .mqtt_manager import get_mqtt_manager, send_led_command, send_relay_command

# Setup logging
logger = logging.getLogger(__name__)

# Helper function to format datetime with Bangkok timezone
def format_datetime_local(dt):
    """แปลง datetime เป็น string พร้อม timezone Bangkok (+7)"""
    if not dt:
        return None
    
    # แปลงเป็น Bangkok timezone
    bangkok_tz = pytz.timezone('Asia/Bangkok')
    if timezone.is_aware(dt):
        local_dt = dt.astimezone(bangkok_tz)
    else:
        # ถ้าเป็น naive datetime ให้ถือว่าเป็น UTC แล้วแปลงเป็น Bangkok
        utc_dt = pytz.utc.localize(dt)
        local_dt = utc_dt.astimezone(bangkok_tz)
    
    return local_dt.strftime('%Y-%m-%d %H:%M:%S')

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

def ai_dashboard(request):
    """AI Agent Dashboard - แสดงผลการวิเคราะห์และการตัดสินใจของ AI Agent"""
    
    context = {
        'current_time': timezone.now(),
    }
    
    return render(request, 'iot_dashboard/ai_dashboard.html', context)

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
            # แปลงเป็น Bangkok timezone ก่อนส่ง
            bangkok_time = timezone.localtime(sensor.timestamp, timezone=timezone.get_current_timezone())
            
            data.append({
                'id': sensor.id,
                'temperature': float(sensor.temperature) if sensor.temperature is not None else None,
                'humidity': float(sensor.humidity) if sensor.humidity is not None else None,
                'timestamp': bangkok_time.isoformat(),  # ใช้ ISO format พร้อม timezone
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
            # แปลงเป็น Bangkok timezone
            bangkok_time = timezone.localtime(sensor.timestamp, timezone=timezone.get_current_timezone())
            chart_data['labels'].append(bangkok_time.strftime('%H:%M:%S'))
            chart_data['temperature'].append(
                float(sensor.temperature) if sensor.temperature is not None else None
            )
            chart_data['humidity'].append(
                float(sensor.humidity) if sensor.humidity is not None else None
            )
        
        # ข้อมูลล่าสุด
        latest = sensors.first() if sensors else None
        if latest:
            # แปลงเป็น Bangkok timezone
            bangkok_time = timezone.localtime(latest.timestamp, timezone=timezone.get_current_timezone())
            latest_data = {
                'temperature': float(latest.temperature) if latest.temperature else None,
                'humidity': float(latest.humidity) if latest.humidity else None,
                'timestamp': bangkok_time.isoformat()  # ใช้ ISO format พร้อม timezone
            }
        else:
            latest_data = {
                'temperature': None,
                'humidity': None,
                'timestamp': None
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


# ============================================
# REST API Endpoints for Postman
# ============================================

@csrf_exempt
def api_led_status(request):
    """
    GET: อ่านสถานะ LED
    POST: ควบคุม LED (เปิด/ปิด)
    """
    if request.method == 'GET':
        try:
            led_device, created = Device.objects.get_or_create(name="Onboard LED")
            
            return JsonResponse({
                'success': True,
                'data': {
                    'id': led_device.id,
                    'name': led_device.name,
                    'is_on': led_device.is_on,
                    'last_updated': led_device.last_updated.strftime('%Y-%m-%d %H:%M:%S') if led_device.last_updated else None
                }
            })
        except Exception as e:
            logger.error(f"❌ GET LED Status Error: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    elif request.method == 'POST':
        try:
            # Parse JSON body
            data = json.loads(request.body)
            command = data.get('command', '').upper()  # 'ON', 'OFF', 'TOGGLE'
            
            if command not in ['ON', 'OFF', 'TOGGLE']:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid command. Use: ON, OFF, or TOGGLE'
                }, status=400)
            
            led_device, created = Device.objects.get_or_create(name="Onboard LED")
            
            # Handle TOGGLE
            if command == 'TOGGLE':
                command = 'OFF' if led_device.is_on else 'ON'
            
            # Send MQTT command
            success, result_msg = send_led_command(command)
            
            if success:
                # Update database
                led_device.is_on = (command == 'ON')
                led_device.last_updated = timezone.now()
                led_device.save()
                
                return JsonResponse({
                    'success': True,
                    'message': f'LED turned {command}',
                    'data': {
                        'id': led_device.id,
                        'name': led_device.name,
                        'is_on': led_device.is_on,
                        'command_sent': command,
                        'last_updated': led_device.last_updated.strftime('%Y-%m-%d %H:%M:%S')
                    }
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'MQTT command failed: {result_msg}'
                }, status=500)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON body'
            }, status=400)
        except Exception as e:
            logger.error(f"❌ POST LED Control Error: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    else:
        return JsonResponse({
            'success': False,
            'error': 'Method not allowed. Use GET or POST'
        }, status=405)


@csrf_exempt
def api_relay_status(request):
    """
    GET: อ่านสถานะ RELAY ทั้งหมด
    POST: ควบคุม RELAY (เปิด/ปิด/toggle)
    """
    if request.method == 'GET':
        try:
            relay_controller, created = Relay.objects.get_or_create(
                name="ESP32 Relay Controller",
                defaults={
                    'relay1_status': False,
                    'relay2_status': False,
                    'relay3_status': False
                }
            )
            
            return JsonResponse({
                'success': True,
                'data': {
                    'id': relay_controller.id,
                    'name': relay_controller.name,
                    'relay1': relay_controller.relay1_status,
                    'relay2': relay_controller.relay2_status,
                    'relay3': relay_controller.relay3_status,
                    'last_updated': relay_controller.last_updated.strftime('%Y-%m-%d %H:%M:%S') if relay_controller.last_updated else None
                }
            })
        except Exception as e:
            logger.error(f"❌ GET Relay Status Error: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    elif request.method == 'POST':
        try:
            # Parse JSON body
            data = json.loads(request.body)
            relay_num = data.get('relay_num')  # 1, 2, or 3
            command = data.get('command', '').upper()  # 'ON', 'OFF', 'TOGGLE'
            
            if relay_num not in [1, 2, 3]:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid relay_num. Use: 1, 2, or 3'
                }, status=400)
            
            if command not in ['ON', 'OFF', 'TOGGLE']:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid command. Use: ON, OFF, or TOGGLE'
                }, status=400)
            
            relay_controller, created = Relay.objects.get_or_create(
                name="ESP32 Relay Controller",
                defaults={
                    'relay1_status': False,
                    'relay2_status': False,
                    'relay3_status': False
                }
            )
            
            # Get current status
            if relay_num == 1:
                current_status = relay_controller.relay1_status
            elif relay_num == 2:
                current_status = relay_controller.relay2_status
            else:
                current_status = relay_controller.relay3_status
            
            # Handle TOGGLE
            if command == 'TOGGLE':
                command = 'OFF' if current_status else 'ON'
            
            # Send MQTT command
            success, result_msg = send_relay_command(relay_num, command)
            
            if success:
                # Update database
                new_status = (command == 'ON')
                if relay_num == 1:
                    relay_controller.relay1_status = new_status
                elif relay_num == 2:
                    relay_controller.relay2_status = new_status
                else:
                    relay_controller.relay3_status = new_status
                
                relay_controller.last_updated = timezone.now()
                relay_controller.save()
                
                return JsonResponse({
                    'success': True,
                    'message': f'Relay {relay_num} turned {command}',
                    'data': {
                        'id': relay_controller.id,
                        'relay_num': relay_num,
                        'status': new_status,
                        'command_sent': command,
                        'last_updated': relay_controller.last_updated.strftime('%Y-%m-%d %H:%M:%S')
                    }
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'MQTT command failed: {result_msg}'
                }, status=500)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON body'
            }, status=400)
        except Exception as e:
            logger.error(f"❌ POST Relay Control Error: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    else:
        return JsonResponse({
            'success': False,
            'error': 'Method not allowed. Use GET or POST'
        }, status=405)


@csrf_exempt
def api_sensors_list(request):
    """
    GET: ดึงรายการข้อมูล sensor (พร้อม pagination)
    POST: เพิ่มข้อมูล sensor ใหม่ (สำหรับทดสอบ)
    """
    if request.method == 'GET':
        try:
            # Get query parameters
            limit = int(request.GET.get('limit', 20))
            offset = int(request.GET.get('offset', 0))
            
            # Get total count
            total_count = SensorData.objects.count()
            
            # Get sensors with pagination
            sensors = SensorData.objects.order_by('-timestamp')[offset:offset+limit]
            
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
                'pagination': {
                    'total': total_count,
                    'limit': limit,
                    'offset': offset,
                    'count': len(data)
                }
            })
        except Exception as e:
            logger.error(f"❌ GET Sensors Error: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    elif request.method == 'POST':
        try:
            # Parse JSON body
            data = json.loads(request.body)
            temperature = data.get('temperature')
            humidity = data.get('humidity')
            device_name = data.get('device_name', 'API_Manual')
            
            if temperature is None or humidity is None:
                return JsonResponse({
                    'success': False,
                    'error': 'temperature and humidity are required'
                }, status=400)
            
            # Create sensor data
            sensor = SensorData.objects.create(
                temperature=float(temperature),
                humidity=float(humidity),
                device_name=device_name,
                timestamp=timezone.now()
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Sensor data created successfully',
                'data': {
                    'id': sensor.id,
                    'temperature': float(sensor.temperature),
                    'humidity': float(sensor.humidity),
                    'device_name': sensor.device_name,
                    'timestamp': sensor.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                }
            }, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON body'
            }, status=400)
        except Exception as e:
            logger.error(f"❌ POST Sensor Error: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    else:
        return JsonResponse({
            'success': False,
            'error': 'Method not allowed. Use GET or POST'
        }, status=405)


@csrf_exempt
def api_sensor_detail(request, sensor_id):
    """
    GET: ดึงข้อมูล sensor ตาม ID
    PUT/PATCH: แก้ไขข้อมูล sensor
    DELETE: ลบข้อมูล sensor
    """
    try:
        sensor = SensorData.objects.get(id=sensor_id)
    except SensorData.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': f'Sensor with ID {sensor_id} not found'
        }, status=404)
    
    if request.method == 'GET':
        try:
            return JsonResponse({
                'success': True,
                'data': {
                    'id': sensor.id,
                    'temperature': float(sensor.temperature) if sensor.temperature is not None else None,
                    'humidity': float(sensor.humidity) if sensor.humidity is not None else None,
                    'timestamp': sensor.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'device_name': sensor.device_name
                }
            })
        except Exception as e:
            logger.error(f"❌ GET Sensor Detail Error: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    elif request.method in ['PUT', 'PATCH']:
        try:
            # Parse JSON body
            data = json.loads(request.body)
            
            if 'temperature' in data:
                sensor.temperature = float(data['temperature'])
            if 'humidity' in data:
                sensor.humidity = float(data['humidity'])
            if 'device_name' in data:
                sensor.device_name = data['device_name']
            
            sensor.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Sensor data updated successfully',
                'data': {
                    'id': sensor.id,
                    'temperature': float(sensor.temperature) if sensor.temperature is not None else None,
                    'humidity': float(sensor.humidity) if sensor.humidity is not None else None,
                    'timestamp': sensor.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'device_name': sensor.device_name
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON body'
            }, status=400)
        except Exception as e:
            logger.error(f"❌ UPDATE Sensor Error: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    elif request.method == 'DELETE':
        try:
            sensor_data = {
                'id': sensor.id,
                'temperature': float(sensor.temperature) if sensor.temperature is not None else None,
                'humidity': float(sensor.humidity) if sensor.humidity is not None else None,
                'timestamp': sensor.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }
            sensor.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Sensor data deleted successfully',
                'deleted_data': sensor_data
            })
        except Exception as e:
            logger.error(f"❌ DELETE Sensor Error: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    else:
        return JsonResponse({
            'success': False,
            'error': 'Method not allowed. Use GET, PUT, PATCH, or DELETE'
        }, status=405)


@csrf_exempt
def api_sensors_latest(request):
    """GET: ดึงข้อมูล sensor ล่าสุด"""
    try:
        latest = SensorData.objects.order_by('-timestamp').first()
        
        if not latest:
            return JsonResponse({
                'success': True,
                'data': None,
                'message': 'No sensor data available'
            })
        
        return JsonResponse({
            'success': True,
            'data': {
                'id': latest.id,
                'temperature': float(latest.temperature) if latest.temperature is not None else None,
                'humidity': float(latest.humidity) if latest.humidity is not None else None,
                'timestamp': latest.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'device_name': latest.device_name
            }
        })
    except Exception as e:
        logger.error(f"❌ GET Latest Sensor Error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
def api_sensors_stats(request):
    """GET: ดึงสถิติข้อมูล sensor"""
    try:
        from django.db.models import Avg, Max, Min, Count
        
        stats = SensorData.objects.aggregate(
            total_count=Count('id'),
            avg_temperature=Avg('temperature'),
            max_temperature=Max('temperature'),
            min_temperature=Min('temperature'),
            avg_humidity=Avg('humidity'),
            max_humidity=Max('humidity'),
            min_humidity=Min('humidity')
        )
        
        latest = SensorData.objects.order_by('-timestamp').first()
        oldest = SensorData.objects.order_by('timestamp').first()
        
        return JsonResponse({
            'success': True,
            'data': {
                'total_readings': stats['total_count'],
                'temperature': {
                    'average': round(float(stats['avg_temperature']), 2) if stats['avg_temperature'] else None,
                    'max': float(stats['max_temperature']) if stats['max_temperature'] else None,
                    'min': float(stats['min_temperature']) if stats['min_temperature'] else None
                },
                'humidity': {
                    'average': round(float(stats['avg_humidity']), 2) if stats['avg_humidity'] else None,
                    'max': float(stats['max_humidity']) if stats['max_humidity'] else None,
                    'min': float(stats['min_humidity']) if stats['min_humidity'] else None
                },
                'latest_reading': latest.timestamp.strftime('%Y-%m-%d %H:%M:%S') if latest else None,
                'oldest_reading': oldest.timestamp.strftime('%Y-%m-%d %H:%M:%S') if oldest else None
            }
        })
    except Exception as e:
        logger.error(f"❌ GET Sensor Stats Error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
def api_system_status(request):
    """GET: ดึงสถานะระบบทั้งหมด"""
    try:
        # Get LED status
        led_device, _ = Device.objects.get_or_create(name="Onboard LED")
        
        # Get Relay status
        relay_controller, _ = Relay.objects.get_or_create(
            name="ESP32 Relay Controller",
            defaults={
                'relay1_status': False,
                'relay2_status': False,
                'relay3_status': False
            }
        )
        
        # Get sensor stats
        latest_sensor = SensorData.objects.order_by('-timestamp').first()
        total_sensors = SensorData.objects.count()
        
        # Get MQTT status
        mqtt_manager = get_mqtt_manager()
        mqtt_connected = mqtt_manager.is_connected if mqtt_manager else False
        
        return JsonResponse({
            'success': True,
            'data': {
                'led': {
                    'is_on': led_device.is_on,
                    'last_updated': led_device.last_updated.strftime('%Y-%m-%d %H:%M:%S') if led_device.last_updated else None
                },
                'relays': {
                    'relay1': relay_controller.relay1_status,
                    'relay2': relay_controller.relay2_status,
                    'relay3': relay_controller.relay3_status,
                    'last_updated': relay_controller.last_updated.strftime('%Y-%m-%d %H:%M:%S') if relay_controller.last_updated else None
                },
                'sensors': {
                    'total_readings': total_sensors,
                    'latest': {
                        'temperature': float(latest_sensor.temperature) if latest_sensor and latest_sensor.temperature else None,
                        'humidity': float(latest_sensor.humidity) if latest_sensor and latest_sensor.humidity else None,
                        'timestamp': latest_sensor.timestamp.strftime('%Y-%m-%d %H:%M:%S') if latest_sensor else None
                    } if latest_sensor else None
                },
                'mqtt': {
                    'connected': mqtt_connected,
                    'broker': 'broker.hivemq.com',
                    'port': 1883
                },
                'server_time': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    except Exception as e:
        logger.error(f"❌ GET System Status Error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ========================================
# Threshold Management API Endpoints
# ========================================

@csrf_exempt
def api_threshold_settings(request):
    """
    API สำหรับจัดการ Threshold Settings
    
    GET: ดึงข้อมูล Threshold ปัจจุบัน พร้อมค่าเฉลี่ย
    POST/PUT/PATCH: อัพเดท Threshold Settings
    
    POST/PUT/PATCH Body (JSON):
    {
        "temperature_high": 35.0,
        "temperature_low": 20.0,
        "humidity_high": 80.0,
        "humidity_low": 30.0,
        "mode": "AUTO" or "MANUAL",
        "relay1_auto_enabled": true,
        "hysteresis_percentage": 2.0,
        "average_window": 10
    }
    
    Response:
    {
        "success": true,
        "data": {
            "id": 1,
            "temperature_high": 35.0,
            "temperature_low": 20.0,
            "humidity_high": 80.0,
            "humidity_low": 30.0,
            "mode": "AUTO",
            "relay1_auto_enabled": true,
            "alarm_active": false,
            "alarm_reason": "",
            "last_triggered": null,
            "hysteresis_percentage": 2.0,
            "average_window": 10,
            "current_averages": {
                "temperature": 28.5,
                "humidity": 65.2
            },
            "latest_sensor": {
                "temperature": 29.0,
                "humidity": 66.0,
                "timestamp": "2024-01-15 10:30:00"
            },
            "created_at": "2024-01-15 09:00:00",
            "updated_at": "2024-01-15 10:00:00"
        }
    }
    """
    try:
        # Get or create singleton ThresholdSetting
        threshold = ThresholdSetting.get_or_create_default()
        
        # GET: Return current settings
        if request.method == 'GET':
            # Get current averages
            avg_temp, avg_humidity = threshold.get_current_averages()
            
            # Get latest sensor
            latest_sensor = SensorData.objects.order_by('-timestamp').first()
            
            return JsonResponse({
                'success': True,
                'data': {
                    'id': threshold.id,
                    'temperature_high': float(threshold.temperature_high),
                    'temperature_low': float(threshold.temperature_low),
                    'humidity_high': float(threshold.humidity_high),
                    'humidity_low': float(threshold.humidity_low),
                    'mode': threshold.mode,
                    'mode_display': threshold.get_mode_display_thai(),
                    'relay1_auto_enabled': threshold.relay1_auto_enabled,
                    'alarm_active': threshold.alarm_active,
                    'alarm_status_display': threshold.get_alarm_status_display(),
                    'alarm_reason': threshold.alarm_reason,
                    'last_triggered': threshold.last_triggered.strftime('%Y-%m-%d %H:%M:%S') if threshold.last_triggered else None,
                    'hysteresis_percentage': float(threshold.hysteresis_percentage),
                    'average_window': threshold.average_window,
                    'current_averages': {
                        'temperature': round(float(avg_temp), 2) if avg_temp else None,
                        'humidity': round(float(avg_humidity), 2) if avg_humidity else None
                    },
                    'latest_sensor': {
                        'temperature': float(latest_sensor.temperature) if latest_sensor and latest_sensor.temperature else None,
                        'humidity': float(latest_sensor.humidity) if latest_sensor and latest_sensor.humidity else None,
                        'timestamp': latest_sensor.timestamp.strftime('%Y-%m-%d %H:%M:%S') if latest_sensor else None
                    } if latest_sensor else None,
                    'created_at': threshold.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': threshold.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            })
        
        # POST/PUT/PATCH: Update settings
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid JSON format'
                }, status=400)
            
            # Update fields if provided
            if 'temperature_high' in data:
                threshold.temperature_high = float(data['temperature_high'])
            if 'temperature_low' in data:
                threshold.temperature_low = float(data['temperature_low'])
            if 'humidity_high' in data:
                threshold.humidity_high = float(data['humidity_high'])
            if 'humidity_low' in data:
                threshold.humidity_low = float(data['humidity_low'])
            if 'mode' in data:
                mode = data['mode'].upper()
                if mode not in ['AUTO', 'MANUAL']:
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid mode. Must be AUTO or MANUAL'
                    }, status=400)
                threshold.mode = mode
            if 'relay1_auto_enabled' in data:
                threshold.relay1_auto_enabled = bool(data['relay1_auto_enabled'])
            if 'hysteresis_percentage' in data:
                threshold.hysteresis_percentage = float(data['hysteresis_percentage'])
            if 'average_window' in data:
                threshold.average_window = int(data['average_window'])
            
            threshold.save()
            
            logger.info(f"✅ Threshold Settings Updated: Mode={threshold.mode}, Temp={threshold.temperature_low}~{threshold.temperature_high}°C, Hum={threshold.humidity_low}~{threshold.humidity_high}%")
            
            # Return updated settings
            avg_temp, avg_humidity = threshold.get_current_averages()
            latest_sensor = SensorData.objects.order_by('-timestamp').first()
            
            return JsonResponse({
                'success': True,
                'message': 'Threshold settings updated successfully',
                'data': {
                    'id': threshold.id,
                    'temperature_high': float(threshold.temperature_high),
                    'temperature_low': float(threshold.temperature_low),
                    'humidity_high': float(threshold.humidity_high),
                    'humidity_low': float(threshold.humidity_low),
                    'mode': threshold.mode,
                    'mode_display': threshold.get_mode_display_thai(),
                    'relay1_auto_enabled': threshold.relay1_auto_enabled,
                    'alarm_active': threshold.alarm_active,
                    'alarm_status_display': threshold.get_alarm_status_display(),
                    'alarm_reason': threshold.alarm_reason,
                    'last_triggered': threshold.last_triggered.strftime('%Y-%m-%d %H:%M:%S') if threshold.last_triggered else None,
                    'hysteresis_percentage': float(threshold.hysteresis_percentage),
                    'average_window': threshold.average_window,
                    'current_averages': {
                        'temperature': round(float(avg_temp), 2) if avg_temp else None,
                        'humidity': round(float(avg_humidity), 2) if avg_humidity else None
                    },
                    'latest_sensor': {
                        'temperature': float(latest_sensor.temperature) if latest_sensor and latest_sensor.temperature else None,
                        'humidity': float(latest_sensor.humidity) if latest_sensor and latest_sensor.humidity else None,
                        'timestamp': latest_sensor.timestamp.strftime('%Y-%m-%d %H:%M:%S') if latest_sensor else None
                    } if latest_sensor else None,
                    'created_at': threshold.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': threshold.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            })
        
        # Other methods not allowed
        return JsonResponse({
            'success': False,
            'error': 'Method not allowed. Use GET, POST, PUT, or PATCH'
        }, status=405)
        
    except Exception as e:
        logger.error(f"❌ Threshold Settings API Error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
def api_threshold_check(request):
    """
    API สำหรับตรวจสอบ Threshold กับ Sensor Data ล่าสุด
    
    GET: ตรวจสอบว่า Sensor Data ล่าสุดเกิน Threshold หรือไม่
    
    Response:
    {
        "success": true,
        "data": {
            "threshold_exceeded": true,
            "should_trigger_alarm": true,
            "reason": "🌡️ อุณหภูมิสูง: 36.5°C > 35.0°C",
            "current_sensor": {
                "temperature": 36.5,
                "humidity": 75.0,
                "timestamp": "2024-01-15 10:30:00"
            },
            "averages": {
                "temperature": 30.2,
                "humidity": 68.5
            },
            "threshold_settings": {
                "temperature_high": 35.0,
                "temperature_low": 20.0,
                "humidity_high": 80.0,
                "humidity_low": 30.0,
                "mode": "AUTO"
            }
        }
    }
    """
    try:
        if request.method != 'GET':
            return JsonResponse({
                'success': False,
                'error': 'Method not allowed. Use GET'
            }, status=405)
        
        # Get threshold settings
        threshold = ThresholdSetting.get_or_create_default()
        
        # Get latest sensor data
        latest_sensor = SensorData.objects.order_by('-timestamp').first()
        
        if not latest_sensor:
            return JsonResponse({
                'success': False,
                'error': 'No sensor data available'
            }, status=404)
        
        # Check threshold
        check_result = threshold.check_threshold(latest_sensor)
        
        return JsonResponse({
            'success': True,
            'data': {
                'threshold_exceeded': check_result['should_trigger'],
                'should_trigger_alarm': threshold.should_activate_alarm(latest_sensor),
                'reason': check_result['reason'],
                'current_sensor': {
                    'temperature': check_result['temperature'],
                    'humidity': check_result['humidity'],
                    'timestamp': latest_sensor.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                },
                'averages': {
                    'temperature': round(float(check_result['avg_temperature']), 2) if check_result['avg_temperature'] else None,
                    'humidity': round(float(check_result['avg_humidity']), 2) if check_result['avg_humidity'] else None
                },
                'threshold_settings': {
                    'temperature_high': float(threshold.temperature_high),
                    'temperature_low': float(threshold.temperature_low),
                    'humidity_high': float(threshold.humidity_high),
                    'humidity_low': float(threshold.humidity_low),
                    'mode': threshold.mode,
                    'relay1_auto_enabled': threshold.relay1_auto_enabled,
                    'alarm_active': threshold.alarm_active
                }
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Threshold Check API Error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
def api_threshold_reset(request):
    """
    API สำหรับรีเซ็ต Alarm (ปิด Alarm และ Relay 1)
    
    POST: รีเซ็ต Alarm และปิด Relay 1
    
    Response:
    {
        "success": true,
        "message": "Alarm reset successfully",
        "data": {
            "alarm_active": false,
            "relay1_status": false
        }
    }
    """
    try:
        if request.method != 'POST':
            return JsonResponse({
                'success': False,
                'error': 'Method not allowed. Use POST'
            }, status=405)
        
        # Get threshold settings
        threshold = ThresholdSetting.get_or_create_default()
        
        # Deactivate alarm
        threshold.deactivate_alarm()
        
        # Turn off Relay 1
        relay_controller, created = Relay.objects.get_or_create(
            name="ESP32 Relay Controller",
            defaults={
                'relay1_status': False,
                'relay2_status': False,
                'relay3_status': False
            }
        )
        
        relay_controller.relay1_status = False
        relay_controller.last_updated = timezone.now()
        relay_controller.save()
        
        # Send MQTT command to turn off relay
        send_relay_command(1, 'OFF')
        
        logger.info("✅ Alarm Reset: Relay 1 turned OFF")
        
        return JsonResponse({
            'success': True,
            'message': 'Alarm reset successfully. Relay 1 turned OFF.',
            'data': {
                'alarm_active': threshold.alarm_active,
                'relay1_status': relay_controller.relay1_status
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Threshold Reset API Error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ========================================
# AI Agent API Endpoints
# ========================================

@csrf_exempt
def api_ai_status(request):
    """
    GET: ดึงสถานะ AI Agent และการตัดสินใจล่าสุด
    
    Response:
    {
        "success": true,
        "data": {
            "scheduler": {
                "is_running": true,
                "interval_minutes": 15,
                "next_run": "2024-01-15 11:00:00"
            },
            "recent_decisions": [
                {
                    "id": 123,
                    "decision": "ON",
                    "confidence": 0.85,
                    "reasoning": "อุณหภูมิสูง...",
                    "action_taken": true,
                    "timestamp": "2024-01-15 10:45:00"
                },
                ...
            ]
        }
    }
    """
    try:
        if request.method != 'GET':
            return JsonResponse({
                'success': False,
                'error': 'Method not allowed. Use GET'
            }, status=405)
        
        from .ai_agent.scheduler import get_ai_scheduler
        from .models import AIDecisionLog, Relay
        
        # Get scheduler status
        scheduler = get_ai_scheduler()
        scheduler_status = scheduler.get_status()
        
        # Get current Relay 2 status (สถานะจริงปัจจุบัน)
        relay_controller = Relay.objects.first()
        current_relay2_status = relay_controller.relay2_status if relay_controller else False
        
        # Get recent decisions (last 5)
        recent_decisions = AIDecisionLog.get_recent_decisions(limit=5)
        decisions_data = []
        
        for decision in recent_decisions:
            decisions_data.append({
                'id': decision.id,
                'decision': decision.decision,
                'confidence': float(decision.confidence),
                'reasoning': decision.reasoning,
                'weather_data': decision.weather_data,
                'relay_status': decision.relay_status,
                'command_sent': decision.command_sent,
                'timestamp': format_datetime_local(decision.timestamp)
            })
        
        # Get latest decision for weather display
        latest_decision = None
        if recent_decisions:
            latest = recent_decisions[0]
            latest_decision = {
                'id': latest.id,
                'decision': latest.decision,
                'confidence': float(latest.confidence),
                'reasoning': latest.reasoning,
                'weather_data': latest.weather_data,
                'relay_status': latest.relay_status,
                'command_sent': latest.command_sent,
                'timestamp': format_datetime_local(latest.timestamp)
            }
        
        return JsonResponse({
            'success': True,
            'data': {
                'scheduler': scheduler_status,
                'recent_decisions': decisions_data,
                'latest_decision': latest_decision,
                'relay2_current_status': current_relay2_status  # เพิ่มสถานะจริงของ Relay 2
            }
        })
        
    except Exception as e:
        logger.error(f"❌ AI Status API Error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
def api_ai_decisions(request):
    """
    GET: ดึงประวัติการตัดสินใจของ AI (พร้อม pagination)
    
    Query Parameters:
    - limit: จำนวนรายการต่อหน้า (default=20)
    - offset: เริ่มจากรายการที่ (default=0)
    
    Response:
    {
        "success": true,
        "data": [...],
        "pagination": {
            "total": 100,
            "limit": 20,
            "offset": 0,
            "count": 20
        }
    }
    """
    try:
        if request.method != 'GET':
            return JsonResponse({
                'success': False,
                'error': 'Method not allowed. Use GET'
            }, status=405)
        
        from .models import AIDecisionLog
        
        # Get pagination parameters
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))
        
        # Get total count
        total_count = AIDecisionLog.objects.count()
        
        # Get decisions with pagination
        decisions = AIDecisionLog.objects.all()[offset:offset+limit]
        
        decisions_data = []
        for decision in decisions:
            decisions_data.append({
                'id': decision.id,
                'decision': decision.decision,
                'confidence': float(decision.confidence),
                'reasoning': decision.reasoning,
                'weather_data': decision.weather_data,
                'relay_status': decision.relay_status,
                'command_sent': decision.command_sent,
                'timestamp': format_datetime_local(decision.timestamp)
            })
        
        return JsonResponse({
            'success': True,
            'data': decisions_data,
            'pagination': {
                'total': total_count,
                'limit': limit,
                'offset': offset,
                'count': len(decisions_data)
            }
        })
        
    except Exception as e:
        logger.error(f"❌ AI Decisions API Error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
def api_ai_analyze_now(request):
    """
    POST: สั่งให้ AI Agent วิเคราะห์และตัดสินใจทันที (ไม่รอ schedule)
    
    Response:
    {
        "success": true,
        "message": "AI analysis triggered successfully",
        "data": {
            "latest_decision": {
                "id": 124,
                "decision": "OFF",
                "confidence": 0.75,
                "reasoning": "อุณหภูมิต่ำ...",
                "timestamp": "2024-01-15 10:50:00"
            }
        }
    }
    """
    try:
        if request.method != 'POST':
            return JsonResponse({
                'success': False,
                'error': 'Method not allowed. Use POST'
            }, status=405)
        
        from .ai_agent.scheduler import get_ai_scheduler
        from .models import AIDecisionLog
        
        # Trigger AI analysis
        scheduler = get_ai_scheduler()
        result = scheduler.trigger_manual_analysis()
        
        if not result['success']:
            return JsonResponse({
                'success': False,
                'error': result.get('message', 'AI analysis failed')
            }, status=500)
        
        # Get latest decision
        latest_decision = AIDecisionLog.objects.first()
        
        decision_data = None
        if latest_decision:
            decision_data = {
                'id': latest_decision.id,
                'decision': latest_decision.decision,
                'confidence': float(latest_decision.confidence),
                'reasoning': latest_decision.reasoning,
                'weather_data': latest_decision.weather_data,
                'relay_status': latest_decision.relay_status,
                'command_sent': latest_decision.command_sent,
                'timestamp': format_datetime_local(latest_decision.timestamp)
            }
        
        return JsonResponse({
            'success': True,
            'message': 'AI analysis triggered successfully',
            'data': {
                'latest_decision': decision_data
            }
        })
        
    except Exception as e:
        logger.error(f"❌ AI Analyze Now API Error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
def api_ai_stats(request):
    """
    GET: ดึงสถิติการทำงานของ AI Agent
    
    Query Parameters:
    - days: จำนวนวันย้อนหลัง (default=7)
    
    Response:
    {
        "success": true,
        "data": {
            "total_decisions": 100,
            "actions_taken": 25,
            "on_decisions": 60,
            "off_decisions": 40,
            "avg_confidence": 0.82,
            "period_days": 7
        }
    }
    """
    try:
        if request.method != 'GET':
            return JsonResponse({
                'success': False,
                'error': 'Method not allowed. Use GET'
            }, status=405)
        
        from .models import AIDecisionLog
        
        # Get days parameter
        days = int(request.GET.get('days', 7))
        
        # Get statistics
        stats = AIDecisionLog.get_statistics(days=days)
        
        return JsonResponse({
            'success': True,
            'data': {
                'total_decisions': stats['total_decisions'],
                'on_decisions': stats['on_decisions'],
                'off_decisions': stats['off_decisions'],
                'avg_confidence': round(float(stats['avg_confidence']), 3),
                'period_days': days,
                'daily_breakdown': stats['daily_breakdown']
            }
        })
        
    except Exception as e:
        logger.error(f"❌ AI Stats API Error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
