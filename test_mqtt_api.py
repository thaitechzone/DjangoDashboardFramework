# -*- coding: utf-8 -*-
"""
MQTT Status API Test
ทดสอบ API สำหรับตรวจสอบสถานะ MQTT Manager
"""

import requests
import json
import time

def test_mqtt_status_api():
    """ทดสอบ MQTT Status API"""
    
    # URL ของ Django server
    base_url = "http://127.0.0.1:8000"
    mqtt_status_url = f"{base_url}/api/mqtt-status/"
    led_control_url = f"{base_url}/api/control-led/"
    
    print("🧪 Testing MQTT Manager APIs")
    print("=" * 50)
    
    try:
        # 1. ทดสอบ MQTT Status API
        print("1️⃣ Testing MQTT Status API...")
        response = requests.get(mqtt_status_url)
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                mqtt_status = data['mqtt_status']
                print("✅ MQTT Status API working!")
                print(f"   Connected: {mqtt_status['connected']}")
                print(f"   Client ID: {mqtt_status['client_id']}")
                print(f"   Broker: {mqtt_status['broker']}")
                print(f"   Pending Messages: {mqtt_status['pending_messages']}")
                print(f"   Topics: {json.dumps(mqtt_status['topics'], indent=6)}")
            else:
                print("❌ MQTT Status API returned error")
        else:
            print(f"❌ MQTT Status API failed with status: {response.status_code}")
        
        print()
        
        # 2. ทดสอบ LED Control API
        print("2️⃣ Testing LED Control API...")
        
        commands = ['on', 'off', 'toggle']
        
        for command in commands:
            print(f"   Testing command: {command}")
            
            payload = {'action': command}
            response = requests.post(
                led_control_url,
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    print(f"   ✅ Command '{command}' successful")
                    print(f"      LED Status: {data['status']}")
                    print(f"      Message: {data['message']}")
                    print(f"      Command Sent: {data['command_sent']}")
                else:
                    print(f"   ❌ Command '{command}' failed: {data['error']}")
            else:
                print(f"   ❌ Command '{command}' failed with status: {response.status_code}")
            
            # รอระหว่างคำสั่ง
            time.sleep(1)
        
        print()
        
        # 3. ทดสอบ MQTT Status อีกครั้งหลังจากส่งคำสั่ง
        print("3️⃣ Checking MQTT Status after commands...")
        response = requests.get(mqtt_status_url)
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                mqtt_status = data['mqtt_status']
                print("✅ Final MQTT Status:")
                print(f"   Connected: {mqtt_status['connected']}")
                print(f"   Pending Messages: {mqtt_status['pending_messages']}")
            else:
                print("❌ Final MQTT Status check failed")
        
        print("\n🎉 API Test completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Django server")
        print("   Make sure Django server is running: python manage.py runserver")
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_mqtt_status_api()