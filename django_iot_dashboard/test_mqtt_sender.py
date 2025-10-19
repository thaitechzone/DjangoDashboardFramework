"""
Test MQTT - ส่งข้อมูล Sensor และ RELAY ทดสอบ
รันไฟล์นี้เพื่อจำลองข้อมูลจาก ESP32

Usage:
    python test_mqtt_sender.py
"""

import paho.mqtt.client as mqtt
import json
import time
import random

# MQTT Configuration
BROKER = "broker.hivemq.com"
PORT = 1883
CLIENT_ID = "TestSender_Python"

# Topics
SENSOR_TOPIC = "thaitechzone/v2_board/sensor/data"
LED_STATE_TOPIC = "thaitechzone/v2_board/state/led"
RELAY1_STATE_TOPIC = "thaitechzone/v2_board/state/relay1"
RELAY2_STATE_TOPIC = "thaitechzone/v2_board/state/relay2"
RELAY3_STATE_TOPIC = "thaitechzone/v2_board/state/relay3"


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT Broker")
    else:
        print(f"❌ Connection failed with code {rc}")


def send_sensor_data(client):
    """ส่งข้อมูล Temperature และ Humidity"""
    # สุ่มค่า temperature 25-35°C และ humidity 50-80%
    temperature = round(random.uniform(25.0, 35.0), 2)
    humidity = round(random.uniform(50.0, 80.0), 2)
    
    data = {
        "temperature": temperature,
        "humidity": humidity,
        "device_name": "ESP32_DHT22_Test"
    }
    
    payload = json.dumps(data)
    result = client.publish(SENSOR_TOPIC, payload, qos=1)
    
    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        print(f"📤 Sent sensor data:")
        print(f"   🌡️  Temperature: {temperature}°C")
        print(f"   💧 Humidity: {humidity}%")
        print(f"   Topic: {SENSOR_TOPIC}")
        print(f"   Payload: {payload}\n")
        return True
    else:
        print(f"❌ Failed to send sensor data (code: {result.rc})\n")
        return False


def send_led_state(client, state):
    """ส่งสถานะ LED"""
    payload = state.upper()
    result = client.publish(LED_STATE_TOPIC, payload, qos=1)
    
    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        print(f"📤 Sent LED state: {payload}")
        return True
    else:
        print(f"❌ Failed to send LED state")
        return False


def send_relay_state(client, relay_num, state):
    """ส่งสถานะ RELAY"""
    topics = {
        1: RELAY1_STATE_TOPIC,
        2: RELAY2_STATE_TOPIC,
        3: RELAY3_STATE_TOPIC
    }
    
    topic = topics.get(relay_num)
    if not topic:
        print(f"❌ Invalid relay number: {relay_num}")
        return False
    
    payload = state.upper()
    result = client.publish(topic, payload, qos=1)
    
    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        print(f"📤 Sent RELAY {relay_num} state: {payload}")
        return True
    else:
        print(f"❌ Failed to send RELAY {relay_num} state")
        return False


def main():
    print("=" * 60)
    print("  🧪 MQTT Test Sender - จำลองข้อมูลจาก ESP32")
    print("=" * 60)
    print(f"\n🌐 Broker: {BROKER}:{PORT}")
    print(f"🆔 Client ID: {CLIENT_ID}\n")
    
    # สร้าง MQTT client
    client = mqtt.Client(CLIENT_ID)
    client.on_connect = on_connect
    
    try:
        # เชื่อมต่อ broker
        print(f"🔄 Connecting to {BROKER}...\n")
        client.connect(BROKER, PORT, 60)
        client.loop_start()
        time.sleep(2)  # รอให้เชื่อมต่อ
        
        print("=" * 60)
        print("  เริ่มส่งข้อมูลทดสอบ")
        print("=" * 60)
        print("\n📌 กำลังส่งข้อมูล 5 ครั้ง (ทุก 3 วินาที)\n")
        
        for i in range(5):
            print(f"--- ครั้งที่ {i+1} ---")
            
            # ส่งข้อมูล sensor
            send_sensor_data(client)
            
            # ส่งสถานะ LED (สลับ ON/OFF)
            led_state = "ON" if i % 2 == 0 else "OFF"
            send_led_state(client, led_state)
            
            # ส่งสถานะ RELAY (สลับแบบสุ่ม)
            for relay_num in range(1, 4):
                relay_state = "ON" if random.random() > 0.5 else "OFF"
                send_relay_state(client, relay_num, relay_state)
            
            print()
            
            if i < 4:  # ไม่รอหลังครั้งสุดท้าย
                time.sleep(3)
        
        print("=" * 60)
        print("  ✅ ส่งข้อมูลทดสอบเสร็จสิ้น!")
        print("=" * 60)
        print("\n📌 ตรวจสอบผลลัพธ์ที่:")
        print("   1. Terminal ที่รัน: python manage.py mqtt_listener")
        print("   2. หรือ start_mqtt.bat")
        print("   3. Dashboard: http://127.0.0.1:8000/\n")
        
    except KeyboardInterrupt:
        print("\n\n🛑 ยกเลิกการส่งข้อมูล")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    finally:
        client.loop_stop()
        client.disconnect()
        print("👋 Disconnected from broker\n")


if __name__ == "__main__":
    main()
