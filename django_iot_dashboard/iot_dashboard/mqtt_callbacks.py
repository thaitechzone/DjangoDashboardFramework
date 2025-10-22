# -*- coding: utf-8 -*-
"""
MQTT Callbacks - จัดการข้อความที่ได้รับจาก MQTT
อัปเดต database เมื่อ ESP32 ส่งสถานะกลับมา
"""

import logging
from django.utils import timezone
from .models import Relay, Device

logger = logging.getLogger(__name__)

def handle_relay_state_message(topic, message):
    """
    จัดการข้อความสถานะ RELAY ที่ได้รับจาก ESP32
    
    Args:
        topic (str): MQTT topic (e.g., 'thaitechzone/v2_board/state/relay1')
        message (str): ข้อความสถานะ (ON/OFF)
    """
    try:
        # ดึงหมายเลข RELAY จาก topic
        if 'relay1' in topic:
            relay_num = 1
        elif 'relay2' in topic:
            relay_num = 2
        elif 'relay3' in topic:
            relay_num = 3
        else:
            logger.warning(f"⚠️ Unknown relay topic: {topic}")
            return
        
        # แปลงสถานะ
        message_upper = message.upper().strip()
        new_state = (message_upper == 'ON')
        
        logger.info(f"📥 Received RELAY {relay_num} state: {message_upper}")
        
        # อัปเดต database
        relay_controller, created = Relay.objects.get_or_create(
            name="ESP32 Relay Controller",
            defaults={
                'relay1_status': False,
                'relay2_status': False,
                'relay3_status': False
            }
        )
        
        # อัปเดตสถานะของ relay ที่เจาะจง
        if relay_num == 1:
            old_state = relay_controller.relay1_status
            relay_controller.relay1_status = new_state
        elif relay_num == 2:
            old_state = relay_controller.relay2_status
            relay_controller.relay2_status = new_state
        elif relay_num == 3:
            old_state = relay_controller.relay3_status
            relay_controller.relay3_status = new_state
        
        relay_controller.last_updated = timezone.now()
        relay_controller.save()
        
        # แสดง log เฉพาะเมื่อสถานะเปลี่ยน
        if old_state != new_state:
            logger.info(f"✅ RELAY {relay_num} updated: {old_state} → {new_state}")
        else:
            logger.debug(f"🔄 RELAY {relay_num} state confirmed: {new_state}")
        
    except Exception as e:
        logger.error(f"❌ Error handling relay state message: {e}")

def handle_sensor_data_message(topic, message):
    """
    จัดการข้อความ sensor data ที่ได้รับจาก ESP32
    พร้อมตรวจสอบ Threshold และควบคุม Relay 1 อัตโนมัติ (ถ้าเปิดโหมด AUTO)
    
    Args:
        topic (str): MQTT topic
        message (str): ข้อความ JSON ของ sensor data
    """
    try:
        import json
        from .models import SensorData, ThresholdSetting
        from .mqtt_manager import send_relay_command
        
        # Parse JSON
        data = json.loads(message)
        
        # สร้างข้อมูล sensor ใหม่
        sensor_data = SensorData.objects.create(
            device_name=data.get('device', 'ESP32'),
            temperature=data.get('temperature'),
            humidity=data.get('humidity'),
            timestamp=timezone.now()
        )
        
        logger.info(f"📊 Sensor data saved: Temp={sensor_data.temperature}°C, Hum={sensor_data.humidity}%")
        
        # ========================================
        # AUTO THRESHOLD CONTROL
        # ========================================
        # ตรวจสอบ Threshold และควบคุม Relay 1 อัตโนมัติ
        try:
            threshold = ThresholdSetting.get_or_create_default()
            
            # ตรวจสอบเฉพาะเมื่อเปิดโหมด AUTO
            if threshold.mode == 'AUTO' and threshold.relay1_auto_enabled:
                check_result = threshold.check_threshold(sensor_data)
                
                # ตรวจสอบว่าควรเปิด Alarm หรือไม่
                should_trigger = check_result['should_trigger']
                
                # ถ้าเกิน threshold และยังไม่ได้เปิด Alarm
                if should_trigger and not threshold.alarm_active:
                    logger.warning(f"🚨 THRESHOLD EXCEEDED: {check_result['reason']}")
                    
                    # เปิด Relay 1
                    send_relay_command(1, 'ON')
                    
                    # อัพเดทสถานะ Alarm
                    threshold.activate_alarm(reason=check_result['reason'])
                    
                    logger.info(f"✅ Auto-Control: Relay 1 turned ON (Alarm Activated)")
                
                # ถ้ากลับมาปกติและ Alarm เปิดอยู่
                elif not should_trigger and threshold.alarm_active:
                    logger.info(f"✅ THRESHOLD NORMALIZED: {check_result['reason']}")
                    
                    # ปิด Relay 1
                    send_relay_command(1, 'OFF')
                    
                    # ปิด Alarm
                    threshold.deactivate_alarm()
                    
                    logger.info(f"✅ Auto-Control: Relay 1 turned OFF (Alarm Deactivated)")
                
                # Log สถานะปัจจุบัน
                else:
                    if threshold.alarm_active:
                        logger.debug(f"🔄 Alarm Active: Monitoring... (Temp={sensor_data.temperature}°C, Hum={sensor_data.humidity}%)")
                    else:
                        logger.debug(f"✅ Normal: No action needed (Temp={sensor_data.temperature}°C, Hum={sensor_data.humidity}%)")
        
        except Exception as threshold_error:
            logger.error(f"❌ Threshold check error: {threshold_error}")
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON in sensor data: {message}")
    except Exception as e:
        logger.error(f"❌ Error handling sensor data message: {e}")

def handle_led_status_message(topic, message):
    """
    จัดการข้อความสถานะ LED ที่ได้รับจาก ESP32
    
    Args:
        topic (str): MQTT topic
        message (str): ข้อความสถานะ (ON/OFF)
    """
    try:
        message_upper = message.upper().strip()
        new_state = (message_upper == 'ON')
        
        logger.info(f"💡 Received LED state: {message_upper}")
        
        # อัปเดต database
        led_device, created = Device.objects.get_or_create(name="Onboard LED")
        
        old_state = led_device.is_on
        led_device.is_on = new_state
        led_device.last_updated = timezone.now()
        led_device.save()
        
        if old_state != new_state:
            logger.info(f"✅ LED updated: {old_state} → {new_state}")
        
    except Exception as e:
        logger.error(f"❌ Error handling LED status message: {e}")

def register_mqtt_callbacks(mqtt_manager):
    """
    ลงทะเบียน callbacks ทั้งหมดกับ MQTT Manager
    
    Args:
        mqtt_manager: MQTT Manager instance
    """
    try:
        # Register RELAY state callbacks
        mqtt_manager.register_message_callback(
            mqtt_manager.RELAY1_STATE_TOPIC,
            handle_relay_state_message
        )
        mqtt_manager.register_message_callback(
            mqtt_manager.RELAY2_STATE_TOPIC,
            handle_relay_state_message
        )
        mqtt_manager.register_message_callback(
            mqtt_manager.RELAY3_STATE_TOPIC,
            handle_relay_state_message
        )
        
        # Register sensor data callback
        mqtt_manager.register_message_callback(
            mqtt_manager.SENSOR_DATA_TOPIC,
            handle_sensor_data_message
        )
        
        # Register LED status callback
        mqtt_manager.register_message_callback(
            mqtt_manager.LED_STATUS_TOPIC,
            handle_led_status_message
        )
        
        logger.info("✅ All MQTT callbacks registered successfully")
        
    except Exception as e:
        logger.error(f"❌ Error registering MQTT callbacks: {e}")
