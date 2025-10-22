# -*- coding: utf-8 -*-
"""
MQTT Callbacks - จัดการข้อความที่ได้รับจาก MQTT
อัปเดต database เมื่อ ESP32 ส่งสถานะกลับมา
"""

import logging
import re
from django.utils import timezone
from .models import Relay, Device

logger = logging.getLogger(__name__)

def extract_board_id_from_topic(topic):
    """
    Extract board_id from MQTT topic
    
    Topic format: thaitechzone/{board_id}/{category}/{type}
    Example: thaitechzone/v2_board/state/relay1 -> v2_board
    
    Args:
        topic (str): MQTT topic
        
    Returns:
        str: board_id or None if not found
    """
    try:
        parts = topic.split('/')
        if len(parts) >= 2:
            return parts[1]  # board_id is the second part
    except Exception as e:
        logger.error(f"❌ Error extracting board_id from topic '{topic}': {e}")
    return None

def handle_relay_state_message(topic, message):
    """
    จัดการข้อความสถานะ RELAY ที่ได้รับจาก ESP32
    
    Args:
        topic (str): MQTT topic (e.g., 'thaitechzone/board_01/state/relay1')
        message (str): ข้อความสถานะ (ON/OFF)
    """
    try:
        # Extract board_id from topic
        board_id = extract_board_id_from_topic(topic)
        if not board_id:
            logger.warning(f"⚠️ Could not extract board_id from topic: {topic}")
            return
        
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
        
        logger.info(f"📥 Received [{board_id}] RELAY {relay_num} state: {message_upper}")
        
        # อัปเดต database
        relay_controller, created = Relay.objects.get_or_create(
            board_id=board_id,
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
            logger.info(f"✅ [{board_id}] RELAY {relay_num} updated: {old_state} → {new_state}")
        else:
            logger.debug(f"🔄 [{board_id}] RELAY {relay_num} state confirmed: {new_state}")
        
    except Exception as e:
        logger.error(f"❌ Error handling relay state message: {e}")

def handle_sensor_data_message(topic, message):
    """
    จัดการข้อความ sensor data ที่ได้รับจาก ESP32
    
    Args:
        topic (str): MQTT topic
        message (str): ข้อความ JSON ของ sensor data
    """
    try:
        import json
        from .models import SensorData
        
        # Extract board_id from topic
        board_id = extract_board_id_from_topic(topic)
        if not board_id:
            logger.warning(f"⚠️ Could not extract board_id from topic: {topic}")
            board_id = "unknown"
        
        # Parse JSON
        data = json.loads(message)
        
        # สร้างข้อมูล sensor ใหม่
        sensor_data = SensorData.objects.create(
            board_id=board_id,
            device_name=data.get('device', f'ESP32_{board_id}'),
            temperature=data.get('temperature'),
            humidity=data.get('humidity'),
            timestamp=timezone.now()
        )
        
        logger.info(f"📊 [{board_id}] Sensor data saved: Temp={sensor_data.temperature}°C, Hum={sensor_data.humidity}%")
        
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
        # Extract board_id from topic
        board_id = extract_board_id_from_topic(topic)
        if not board_id:
            logger.warning(f"⚠️ Could not extract board_id from topic: {topic}")
            return
        
        message_upper = message.upper().strip()
        new_state = (message_upper == 'ON')
        
        logger.info(f"💡 Received [{board_id}] LED state: {message_upper}")
        
        # อัปเดต database
        led_device, created = Device.objects.get_or_create(
            board_id=board_id,
            name="Onboard LED"
        )
        
        old_state = led_device.is_on
        led_device.is_on = new_state
        led_device.last_updated = timezone.now()
        led_device.save()
        
        if old_state != new_state:
            logger.info(f"✅ [{board_id}] LED updated: {old_state} → {new_state}")
        
    except Exception as e:
        logger.error(f"❌ Error handling LED status message: {e}")

def register_mqtt_callbacks(mqtt_manager):
    """
    ลงทะเบียน callbacks ทั้งหมดกับ MQTT Manager
    
    Args:
        mqtt_manager: MQTT Manager instance
    """
    try:
        # Register callbacks using wildcard pattern matching
        # The callback will receive any topic that matches the pattern
        
        # Register RELAY state callbacks for all boards
        # Pattern: thaitechzone/+/state/relay#
        for board_id in mqtt_manager.get_tracked_boards():
            mqtt_manager.register_message_callback(
                mqtt_manager.get_topic(board_id, "state", "relay1"),
                handle_relay_state_message
            )
            mqtt_manager.register_message_callback(
                mqtt_manager.get_topic(board_id, "state", "relay2"),
                handle_relay_state_message
            )
            mqtt_manager.register_message_callback(
                mqtt_manager.get_topic(board_id, "state", "relay3"),
                handle_relay_state_message
            )
            
            # Register sensor data callback
            mqtt_manager.register_message_callback(
                mqtt_manager.get_topic(board_id, "sensor", "data"),
                handle_sensor_data_message
            )
            
            # Register LED status callback
            mqtt_manager.register_message_callback(
                mqtt_manager.get_topic(board_id, "status", "led"),
                handle_led_status_message
            )
        
        logger.info("✅ All MQTT callbacks registered successfully")
        
    except Exception as e:
        logger.error(f"❌ Error registering MQTT callbacks: {e}")
