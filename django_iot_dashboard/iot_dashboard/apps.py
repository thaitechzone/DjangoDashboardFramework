# -*- coding: utf-8 -*-
"""
Django App Startup Script
สคริปต์สำหรับเริ่มต้น MQTT Manager พร้อมกับ Django App
"""

from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class IotDashboardConfig(AppConfig):
    """Configuration สำหรับ IoT Dashboard App"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'iot_dashboard'
    
    def ready(self):
        """เริ่มต้น MQTT Manager เมื่อ Django app พร้อมใช้งาน"""
        try:
            # Import ใน ready() เพื่อหลีกเลี่ยง import errors
            from .mqtt_manager import get_mqtt_manager
            from .models import Device, SensorData
            
            logger.info("🚀 Initializing MQTT Manager...")
            
            # เริ่มต้น MQTT Manager
            mqtt_manager = get_mqtt_manager()
            
            # ลงทะเบียน callbacks สำหรับ LED status
            def handle_led_status(topic, message):
                """จัดการสถานะ LED ที่ได้รับจาก ESP32"""
                try:
                    led_device, created = Device.objects.get_or_create(name="Onboard LED")
                    
                    if message.upper() == 'ON':
                        led_device.is_on = True
                    elif message.upper() == 'OFF':
                        led_device.is_on = False
                    
                    led_device.save()
                    logger.info(f"📱 LED status updated: {message}")
                    
                except Exception as e:
                    logger.error(f"❌ Error handling LED status: {e}")
            
            # ลงทะเบียน callbacks สำหรับ sensor data
            def handle_sensor_data(topic, message):
                """จัดการข้อมูล sensor ที่ได้รับจาก ESP32"""
                try:
                    import json
                    from django.utils import timezone
                    
                    # พยายาม parse JSON
                    try:
                        data = json.loads(message)
                        temperature = data.get('temperature')
                        humidity = data.get('humidity')
                    except json.JSONDecodeError:
                        # ถ้าไม่ใช่ JSON ลองแยกด้วย comma
                        parts = message.split(',')
                        if len(parts) >= 2:
                            temperature = float(parts[0])
                            humidity = float(parts[1])
                        else:
                            logger.warning(f"⚠️ Cannot parse sensor data: {message}")
                            return
                    
                    # บันทึกข้อมูลใน database
                    sensor_data = SensorData.objects.create(
                        device_name="ESP32_DHT22",
                        temperature=temperature,
                        humidity=humidity,
                        timestamp=timezone.now()
                    )
                    
                    logger.info(f"🌡️ Sensor data saved: {temperature}°C, {humidity}%")
                    
                except Exception as e:
                    logger.error(f"❌ Error handling sensor data: {e}")
            
            # ลงทะเบียน callbacks
            mqtt_manager.register_message_callback(
                mqtt_manager.LED_STATUS_TOPIC, 
                handle_led_status
            )
            
            mqtt_manager.register_message_callback(
                mqtt_manager.SENSOR_DATA_TOPIC,
                handle_sensor_data
            )
            
            logger.info("✅ MQTT Manager initialized successfully!")
            logger.info(f"📡 MQTT Status: {mqtt_manager.get_status()}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize MQTT Manager: {e}")
