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
            from .mqtt_callbacks import register_mqtt_callbacks
            
            logger.info("🚀 Initializing MQTT Manager...")
            
            # เริ่มต้น MQTT Manager
            mqtt_manager = get_mqtt_manager()
            
            # ลงทะเบียน callbacks ทั้งหมด (LED, RELAY, Sensor)
            register_mqtt_callbacks(mqtt_manager)
            
            logger.info("✅ MQTT Manager initialized successfully!")
            logger.info(f"📡 MQTT Status: {mqtt_manager.get_status()}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize MQTT Manager: {e}")
