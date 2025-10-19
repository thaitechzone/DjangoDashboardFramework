# -*- coding: utf-8 -*-
"""
Test MQTT Connection for Django IoT Dashboard
สคริปต์ทดสอบการเชื่อมต่อ MQTT และการส่งคำสั่ง
"""

import paho.mqtt.client as mqtt
import time
import json
import uuid
import sys

# การตั้งค่า MQTT
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
LED_CONTROL_TOPIC = "thaitechzone/v2_board/control/led"
LED_STATUS_TOPIC = "thaitechzone/v2_board/status/led"

# Global variables สำหรับติดตาม connection
is_connected = False
publish_success = False
received_messages = []

def on_connect(client, userdata, flags, rc):
    """Callback เมื่อเชื่อมต่อ MQTT Broker สำเร็จ"""
    global is_connected
    print(f"🔌 Connected to MQTT broker with result code: {rc}")
    if rc == 0:
        is_connected = True
        print("✅ Connection successful!")
        # Subscribe to status topic เพื่อรับสถานะจาก ESP32
        client.subscribe(LED_STATUS_TOPIC)
        print(f"📥 Subscribed to topic: {LED_STATUS_TOPIC}")
    else:
        print(f"❌ Connection failed with code: {rc}")
        is_connected = False

def on_publish(client, userdata, mid):
    """Callback เมื่อส่งข้อความสำเร็จ"""
    global publish_success
    print(f"📤 Message published successfully (ID: {mid})")
    publish_success = True

def on_message(client, userdata, msg):
    """Callback เมื่อได้รับข้อความ"""
    global received_messages
    topic = msg.topic
    message = msg.payload.decode()
    print(f"📨 Received message on topic '{topic}': {message}")
    received_messages.append({
        'topic': topic,
        'message': message,
        'timestamp': time.time()
    })

def on_disconnect(client, userdata, rc):
    """Callback เมื่อตัดการเชื่อมต่อ"""
    global is_connected
    print(f"🔌 Disconnected from MQTT broker (code: {rc})")
    is_connected = False

def test_mqtt_connection():
    """ทดสอบการเชื่อมต่อ MQTT"""
    global is_connected, publish_success, received_messages
    
    print("🚀 Starting MQTT Connection Test...")
    print(f"Broker: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"Control Topic: {LED_CONTROL_TOPIC}")
    print(f"Status Topic: {LED_STATUS_TOPIC}")
    print("-" * 60)
    
    # สร้าง MQTT client พร้อม unique client ID
    client_id = f"django_test_{uuid.uuid4().hex[:8]}"
    print(f"🆔 Client ID: {client_id}")
    
    client = mqtt.Client(client_id=client_id)
    
    # ตั้งค่า callbacks
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    
    try:
        # เชื่อมต่อ MQTT broker
        print("⏳ Attempting to connect...")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        
        # เริ่ม network loop
        client.loop_start()
        
        # รอการเชื่อมต่อ
        timeout = 10
        start_time = time.time()
        while not is_connected and (time.time() - start_time) < timeout:
            time.sleep(0.1)
        
        if not is_connected:
            print("❌ Failed to connect within timeout period")
            return False
        
        # ทดสอบส่งคำสั่ง LED ON
        print("\n🔵 Testing LED ON command...")
        publish_success = False
        result = client.publish(LED_CONTROL_TOPIC, "ON", qos=1)
        
        # รอการส่งสำเร็จ
        timeout = 5
        start_time = time.time()
        while not publish_success and (time.time() - start_time) < timeout:
            time.sleep(0.1)
        
        if publish_success:
            print("✅ LED ON command sent successfully")
        else:
            print("❌ Failed to send LED ON command")
        
        # รอรับ response จาก ESP32
        print("⏳ Waiting for ESP32 response...")
        time.sleep(3)
        
        # ทดสอบส่งคำสั่ง LED OFF
        print("\n🔴 Testing LED OFF command...")
        publish_success = False
        result = client.publish(LED_CONTROL_TOPIC, "OFF", qos=1)
        
        # รอการส่งสำเร็จ
        timeout = 5
        start_time = time.time()
        while not publish_success and (time.time() - start_time) < timeout:
            time.sleep(0.1)
        
        if publish_success:
            print("✅ LED OFF command sent successfully")
        else:
            print("❌ Failed to send LED OFF command")
        
        # รอรับ response จาก ESP32
        print("⏳ Waiting for ESP32 response...")
        time.sleep(3)
        
        # แสดงผลข้อความที่ได้รับ
        print("\n📊 MQTT Test Results:")
        print("-" * 60)
        print(f"Connection Status: {'✅ Connected' if is_connected else '❌ Disconnected'}")
        print(f"Messages Received: {len(received_messages)}")
        
        if received_messages:
            print("\nReceived Messages:")
            for i, msg in enumerate(received_messages, 1):
                print(f"  {i}. Topic: {msg['topic']}")
                print(f"     Message: {msg['message']}")
                print(f"     Time: {time.ctime(msg['timestamp'])}")
        else:
            print("⚠️  No messages received from ESP32")
            print("   - Check if ESP32 is connected to WiFi")
            print("   - Verify ESP32 is subscribed to the control topic")
            print("   - Check ESP32 serial monitor for error messages")
        
        # ปิดการเชื่อมต่อ
        client.loop_stop()
        client.disconnect()
        
        return is_connected and publish_success
        
    except Exception as e:
        print(f"❌ MQTT Test Error: {e}")
        return False

def test_esp32_communication():
    """ทดสอบการสื่อสารแบบเต็มรูปแบบกับ ESP32"""
    print("\n🤖 Testing ESP32 Communication...")
    print("-" * 60)
    
    commands = ["ON", "OFF", "ON", "OFF"]
    
    for i, command in enumerate(commands, 1):
        print(f"\n🔄 Test {i}/4: Sending '{command}' command")
        
        # สร้าง client ใหม่สำหรับแต่ละคำสั่ง
        client_id = f"esp32_test_{uuid.uuid4().hex[:8]}"
        client = mqtt.Client(client_id=client_id)
        
        global is_connected, publish_success
        is_connected = False
        publish_success = False
        
        client.on_connect = on_connect
        client.on_publish = on_publish
        client.on_message = on_message
        
        try:
            # เชื่อมต่อและส่งคำสั่ง
            client.connect(MQTT_BROKER, MQTT_PORT, 60)
            client.loop_start()
            
            # รอการเชื่อมต่อ
            timeout = 5
            start_time = time.time()
            while not is_connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if is_connected:
                # ส่งคำสั่ง
                client.publish(LED_CONTROL_TOPIC, command, qos=1)
                time.sleep(1)  # รอให้ส่งเสร็จ
                print(f"   ✅ Command '{command}' sent")
            else:
                print(f"   ❌ Failed to connect for command '{command}'")
            
            client.loop_stop()
            client.disconnect()
            
        except Exception as e:
            print(f"   ❌ Error sending command '{command}': {e}")
        
        # รอระหว่างคำสั่ง
        time.sleep(2)

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 MQTT Connection Test for Django IoT Dashboard")
    print("=" * 60)
    
    # ทดสอบการเชื่อมต่อพื้นฐาน
    success = test_mqtt_connection()
    
    if success:
        print("\n🎉 Basic MQTT test completed successfully!")
        
        # ถามว่าต้องการทดสอบ ESP32 communication หรือไม่
        try:
            response = input("\nDo you want to test ESP32 communication? (y/n): ").lower()
            if response == 'y' or response == 'yes':
                test_esp32_communication()
        except KeyboardInterrupt:
            print("\n\n🛑 Test interrupted by user")
        except:
            pass
    else:
        print("\n❌ Basic MQTT test failed!")
        print("Please check:")
        print("1. Internet connection")
        print("2. MQTT broker availability")
        print("3. Firewall settings")
    
    print("\n✅ Test completed!")