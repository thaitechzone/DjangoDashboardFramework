# -*- coding: utf-8 -*-
"""
MQTT Manager - จัดการการเชื่อมต่อ MQTT แบบ Persistent
เพื่อให้การตอบสนองรวดเร็วขึ้น
"""

import paho.mqtt.client as mqtt
import threading
import time
import uuid
import json
import logging
from django.utils import timezone
from django.conf import settings
import queue

# ตั้งค่า logging
logger = logging.getLogger(__name__)

class MQTTManager:
    """
    MQTT Manager สำหรับจัดการการเชื่อมต่อแบบ persistent
    - เชื่อมต่อค้างไว้ตลอดเวลา
    - Auto-reconnect เมื่อขาดการเชื่อมต่อ
    - Thread-safe สำหรับการส่งข้อความ
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, 'initialized'):
            return
        
        # การตั้งค่า MQTT
        self.MQTT_BROKER = "broker.hivemq.com"
        self.MQTT_PORT = 1883
        
        # LED Topics
        self.LED_CONTROL_TOPIC = "thaitechzone/v2_board1/control/led"
        self.LED_STATUS_TOPIC = "thaitechzone/v2_board1/status/led"

        # RELAY Control Topics (Dashboard → ESP32)
        self.RELAY1_CONTROL_TOPIC = "thaitechzone/v2_board1/control/relay1"
        self.RELAY2_CONTROL_TOPIC = "thaitechzone/v2_board1/control/relay2"
        self.RELAY3_CONTROL_TOPIC = "thaitechzone/v2_board1/control/relay3"

        # RELAY State Topics (ESP32 → Dashboard)
        self.RELAY1_STATE_TOPIC = "thaitechzone/v2_board1/state/relay1"
        self.RELAY2_STATE_TOPIC = "thaitechzone/v2_board1/state/relay2"
        self.RELAY3_STATE_TOPIC = "thaitechzone/v2_board1/state/relay3"

        # Sensor Data Topic
        self.SENSOR_DATA_TOPIC = "thaitechzone/v2_board1/sensor/data"

        # สถานะการเชื่อมต่อ
        self.is_connected = False
        self.is_connecting = False
        self.client = None
        self.client_id = f"django_iot_{uuid.uuid4().hex[:8]}"
        
        # Threading
        self._connection_lock = threading.Lock()
        self._send_lock = threading.Lock()
        
        # Message queue สำหรับข้อความที่รอส่ง
        self.pending_messages = queue.Queue()
        
        # Callbacks และ event handlers
        self.message_callbacks = {}
        self.connection_callbacks = []
        
        # Start the manager
        self.initialize()
        self.initialized = True
        
        logger.info(f"🚀 MQTT Manager initialized with client ID: {self.client_id}")
    
    def initialize(self):
        """เริ่มต้นการทำงานของ MQTT Manager"""
        self._setup_client()
        self._start_connection_thread()
        self._start_message_processor()
    
    def _setup_client(self):
        """ตั้งค่า MQTT Client"""
        self.client = mqtt.Client(client_id=self.client_id)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.client.on_publish = self._on_publish
        
        # ตั้งค่า keep alive และ timeouts
        self.client.keepalive = 60
        
        logger.info("🔧 MQTT Client configured")
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback เมื่อเชื่อมต่อสำเร็จ"""
        if rc == 0:
            self.is_connected = True
            self.is_connecting = False
            logger.info("✅ MQTT Connected successfully")
            
            # Subscribe to topics
            self._subscribe_to_topics()
            
            # ส่งข้อความที่รอค้างอยู่
            self._process_pending_messages()
            
            # แจ้ง callbacks
            for callback in self.connection_callbacks:
                try:
                    callback(True)
                except Exception as e:
                    logger.error(f"❌ Connection callback error: {e}")
        else:
            self.is_connected = False
            self.is_connecting = False
            logger.error(f"❌ MQTT Connection failed with code: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback เมื่อขาดการเชื่อมต่อ"""
        self.is_connected = False
        logger.warning(f"⚠️ MQTT Disconnected (code: {rc})")
        
        # แจ้ง callbacks
        for callback in self.connection_callbacks:
            try:
                callback(False)
            except Exception as e:
                logger.error(f"❌ Disconnection callback error: {e}")
    
    def _on_message(self, client, userdata, msg):
        """Callback เมื่อได้รับข้อความ"""
        try:
            topic = msg.topic
            message = msg.payload.decode()
            
            logger.info(f"📨 Received MQTT message on '{topic}': {message}")
            
            # ส่งไปยัง callback ที่ register ไว้
            if topic in self.message_callbacks:
                for callback in self.message_callbacks[topic]:
                    try:
                        callback(topic, message)
                    except Exception as e:
                        logger.error(f"❌ Message callback error: {e}")
        
        except Exception as e:
            logger.error(f"❌ Error processing MQTT message: {e}")
    
    def _on_publish(self, client, userdata, mid):
        """Callback เมื่อส่งข้อความสำเร็จ"""
        logger.debug(f"📤 Message published successfully (ID: {mid})")
    
    def _subscribe_to_topics(self):
        """Subscribe to MQTT topics"""
        topics = [
            (self.LED_STATUS_TOPIC, 1),
            (self.SENSOR_DATA_TOPIC, 1),
            # Subscribe to RELAY state topics (รับสถานะจาก ESP32)
            (self.RELAY1_STATE_TOPIC, 1),
            (self.RELAY2_STATE_TOPIC, 1),
            (self.RELAY3_STATE_TOPIC, 1)
        ]
        
        for topic, qos in topics:
            result = self.client.subscribe(topic, qos)
            logger.info(f"📥 Subscribed to topic: {topic} (QoS: {qos})")
    
    def _start_connection_thread(self):
        """เริ่ม thread สำหรับจัดการการเชื่อมต่อ"""
        connection_thread = threading.Thread(
            target=self._connection_manager, 
            daemon=True,
            name="MQTT_ConnectionManager"
        )
        connection_thread.start()
        logger.info("🔄 Connection manager thread started")
    
    def _connection_manager(self):
        """จัดการการเชื่อมต่อและ auto-reconnect"""
        while True:
            try:
                if not self.is_connected and not self.is_connecting:
                    with self._connection_lock:
                        if not self.is_connected and not self.is_connecting:
                            logger.info("🔌 Attempting to connect to MQTT broker...")
                            self.is_connecting = True
                            
                            try:
                                self.client.connect(self.MQTT_BROKER, self.MQTT_PORT, 60)
                                self.client.loop_start()
                                
                                # รอการเชื่อมต่อ
                                timeout = 10
                                start_time = time.time()
                                while self.is_connecting and (time.time() - start_time) < timeout:
                                    time.sleep(0.1)
                                
                                if not self.is_connected:
                                    logger.error("❌ Connection timeout")
                                    self.is_connecting = False
                                    
                            except Exception as e:
                                logger.error(f"❌ Connection error: {e}")
                                self.is_connecting = False
                
                # ตรวจสอบทุก 5 วินาที
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"❌ Connection manager error: {e}")
                time.sleep(10)
    
    def _start_message_processor(self):
        """เริ่ม thread สำหรับประมวลผลข้อความที่รอส่ง"""
        processor_thread = threading.Thread(
            target=self._message_processor,
            daemon=True,
            name="MQTT_MessageProcessor"
        )
        processor_thread.start()
        logger.info("📮 Message processor thread started")
    
    def _message_processor(self):
        """ประมวลผลข้อความที่รอส่ง"""
        while True:
            try:
                # ดึงข้อความจาก queue (blocking)
                message_data = self.pending_messages.get(timeout=1)
                
                if self.is_connected:
                    topic = message_data['topic']
                    payload = message_data['payload']
                    qos = message_data.get('qos', 1)
                    
                    try:
                        result = self.client.publish(topic, payload, qos)
                        if result.rc == mqtt.MQTT_ERR_SUCCESS:
                            logger.info(f"📤 Message sent to '{topic}': {payload}")
                        else:
                            logger.error(f"❌ Failed to send message to '{topic}': {result.rc}")
                    except Exception as e:
                        logger.error(f"❌ Error sending message: {e}")
                        # ใส่กลับใน queue ถ้าส่งไม่สำเร็จ
                        self.pending_messages.put(message_data)
                else:
                    # ใส่กลับใน queue ถ้ายังไม่เชื่อมต่อ
                    self.pending_messages.put(message_data)
                    logger.warning("⚠️ Not connected, message queued")
                
                self.pending_messages.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"❌ Message processor error: {e}")
    
    def _process_pending_messages(self):
        """ส่งข้อความที่รอค้างอยู่เมื่อเชื่อมต่อสำเร็จ"""
        processed = 0
        while not self.pending_messages.empty() and processed < 10:  # จำกัดไม่เกิน 10 ข้อความต่อครั้ง
            try:
                message_data = self.pending_messages.get_nowait()
                
                topic = message_data['topic']
                payload = message_data['payload']
                qos = message_data.get('qos', 1)
                
                result = self.client.publish(topic, payload, qos)
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    logger.info(f"📤 Pending message sent to '{topic}': {payload}")
                else:
                    # ใส่กลับใน queue ถ้าส่งไม่สำเร็จ
                    self.pending_messages.put(message_data)
                
                processed += 1
                
            except queue.Empty:
                break
            except Exception as e:
                logger.error(f"❌ Error processing pending message: {e}")
    
    def send_message(self, topic, payload, qos=1):
        """
        ส่งข้อความ MQTT
        
        Args:
            topic (str): MQTT topic
            payload (str): ข้อความที่จะส่ง
            qos (int): Quality of Service level
            
        Returns:
            bool: True ถ้าส่งสำเร็จหรือใส่ใน queue แล้ว
        """
        try:
            with self._send_lock:
                message_data = {
                    'topic': topic,
                    'payload': payload,
                    'qos': qos,
                    'timestamp': time.time()
                }
                
                if self.is_connected:
                    # ส่งทันทีถ้าเชื่อมต่ออยู่
                    result = self.client.publish(topic, payload, qos)
                    if result.rc == mqtt.MQTT_ERR_SUCCESS:
                        logger.info(f"📤 Message sent immediately to '{topic}': {payload}")
                        return True
                    else:
                        logger.warning(f"⚠️ Immediate send failed, queuing message")
                        self.pending_messages.put(message_data)
                        return True
                else:
                    # ใส่ใน queue ถ้ายังไม่เชื่อมต่อ
                    self.pending_messages.put(message_data)
                    logger.info(f"📥 Message queued for '{topic}': {payload}")
                    return True
                    
        except Exception as e:
            logger.error(f"❌ Error sending message: {e}")
            return False
    
    def send_led_command(self, command):
        """
        ส่งคำสั่งควบคุม LED
        
        Args:
            command (str): คำสั่ง (ON/OFF)
            
        Returns:
            bool: True ถ้าส่งสำเร็จ
        """
        return self.send_message(self.LED_CONTROL_TOPIC, command)
    
    def send_relay_command(self, relay_num, command):
        """
        ส่งคำสั่งควบคุม RELAY
        
        Args:
            relay_num (int): หมายเลข RELAY (1, 2, 3)
            command (str): คำสั่ง (ON/OFF)
            
        Returns:
            bool: True ถ้าส่งสำเร็จ
        """
        topic_map = {
            1: self.RELAY1_CONTROL_TOPIC,
            2: self.RELAY2_CONTROL_TOPIC,
            3: self.RELAY3_CONTROL_TOPIC
        }
        
        if relay_num not in topic_map:
            logger.error(f"❌ Invalid relay number: {relay_num}")
            return False
        
        topic = topic_map[relay_num]
        success = self.send_message(topic, command)
        
        if success:
            logger.info(f"🔌 RELAY {relay_num} command '{command}' sent to {topic}")
        else:
            logger.error(f"❌ Failed to send RELAY {relay_num} command")
        
        return success
    
    def register_message_callback(self, topic, callback):
        """
        ลงทะเบียน callback สำหรับ topic ที่กำหนด
        
        Args:
            topic (str): MQTT topic
            callback (callable): ฟังก์ชัน callback(topic, message)
        """
        if topic not in self.message_callbacks:
            self.message_callbacks[topic] = []
        self.message_callbacks[topic].append(callback)
        logger.info(f"📋 Registered callback for topic: {topic}")
    
    def register_connection_callback(self, callback):
        """
        ลงทะเบียน callback สำหรับสถานะการเชื่อมต่อ
        
        Args:
            callback (callable): ฟังก์ชัน callback(is_connected)
        """
        self.connection_callbacks.append(callback)
        logger.info("📋 Registered connection callback")
    
    def get_status(self):
        """
        ได้รับสถานะของ MQTT Manager
        
        Returns:
            dict: ข้อมูลสถานะ
        """
        return {
            'connected': self.is_connected,
            'connecting': self.is_connecting,
            'client_id': self.client_id,
            'broker': f"{self.MQTT_BROKER}:{self.MQTT_PORT}",
            'pending_messages': self.pending_messages.qsize(),
            'topics': {
                'led_control': self.LED_CONTROL_TOPIC,
                'led_status': self.LED_STATUS_TOPIC,
                'relay1_control': self.RELAY1_CONTROL_TOPIC,
                'relay2_control': self.RELAY2_CONTROL_TOPIC,
                'relay3_control': self.RELAY3_CONTROL_TOPIC,
                'relay1_state': self.RELAY1_STATE_TOPIC,
                'relay2_state': self.RELAY2_STATE_TOPIC,
                'relay3_state': self.RELAY3_STATE_TOPIC,
                'sensor_data': self.SENSOR_DATA_TOPIC
            }
        }
    
    def shutdown(self):
        """ปิดการทำงานของ MQTT Manager"""
        try:
            if self.client and self.is_connected:
                self.client.loop_stop()
                self.client.disconnect()
            logger.info("🛑 MQTT Manager shutdown")
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")


# Global instance
mqtt_manager = None

def get_mqtt_manager():
    """ได้รับ MQTT Manager instance (Singleton)"""
    global mqtt_manager
    if mqtt_manager is None:
        mqtt_manager = MQTTManager()
    return mqtt_manager

def send_led_command(command):
    """
    ส่งคำสั่งควบคุม LED ผ่าน MQTT Manager
    
    Args:
        command (str): คำสั่ง (ON/OFF)
        
    Returns:
        tuple: (success, message)
    """
    try:
        manager = get_mqtt_manager()
        success = manager.send_led_command(command)
        
        if success:
            return True, f"Command '{command}' sent successfully"
        else:
            return False, f"Failed to send command '{command}'"
            
    except Exception as e:
        logger.error(f"❌ Error in send_led_command: {e}")
        return False, f"Error: {e}"

def send_relay_command(relay_num, command):
    """
    ส่งคำสั่งควบคุม RELAY ผ่าน MQTT Manager
    
    Args:
        relay_num (int): หมายเลข RELAY (1, 2, 3)
        command (str): คำสั่ง (ON/OFF)
        
    Returns:
        tuple: (success, message)
    """
    try:
        manager = get_mqtt_manager()
        success = manager.send_relay_command(relay_num, command)
        
        if success:
            return True, f"RELAY {relay_num} command '{command}' sent successfully"
        else:
            return False, f"Failed to send RELAY {relay_num} command '{command}'"
            
    except Exception as e:
        logger.error(f"❌ Error in send_relay_command: {e}")
        return False, f"Error: {e}"
