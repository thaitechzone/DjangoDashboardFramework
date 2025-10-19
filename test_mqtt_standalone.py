# -*- coding: utf-8 -*-
"""
Quick MQTT Test Script (No Django Required)
สคริปต์ทดสอบ MQTT แบบง่ายๆ ไม่ต้องใช้ Django
"""

import sys
import os

# เพิ่ม path ของ project เพื่อให้ import mqtt_manager ได้
sys.path.append(os.path.join(os.path.dirname(__file__), 'django_iot_dashboard', 'iot_dashboard'))

def test_mqtt_manager():
    """ทดสอบ MQTT Manager แบบง่าย"""
    
    print("🧪 Testing MQTT Manager (Standalone)")
    print("=" * 50)
    
    try:
        # Import MQTT Manager
        from mqtt_manager import MQTTManager
        
        print("✅ MQTT Manager imported successfully")
        
        # สร้าง instance
        manager = MQTTManager()
        print("✅ MQTT Manager instance created")
        
        # แสดงสถานะ
        status = manager.get_status()
        print("\n📊 MQTT Manager Status:")
        print(f"   Connected: {status['connected']}")
        print(f"   Client ID: {status['client_id']}")
        print(f"   Broker: {status['broker']}")
        print(f"   Pending Messages: {status['pending_messages']}")
        
        # รอให้เชื่อมต่อ
        import time
        print("\n⏳ Waiting for connection...")
        
        timeout = 15
        start_time = time.time()
        while not manager.is_connected and (time.time() - start_time) < timeout:
            time.sleep(1)
            print(".", end="", flush=True)
        
        print()
        
        if manager.is_connected:
            print("✅ Connected to MQTT broker!")
            
            # ทดสอบส่งคำสั่ง
            print("\n🔵 Testing LED commands...")
            
            commands = ['ON', 'OFF', 'ON']
            for i, cmd in enumerate(commands, 1):
                print(f"   {i}. Sending '{cmd}' command...")
                success = manager.send_led_command(cmd)
                
                if success:
                    print(f"      ✅ Command '{cmd}' sent successfully")
                else:
                    print(f"      ❌ Failed to send command '{cmd}'")
                
                time.sleep(2)
            
            # แสดงสถานะสุดท้าย
            final_status = manager.get_status()
            print("\n📊 Final Status:")
            print(f"   Connected: {final_status['connected']}")
            print(f"   Pending Messages: {final_status['pending_messages']}")
            
        else:
            print("❌ Failed to connect to MQTT broker")
            print("   Check your internet connection")
            print("   Verify MQTT broker is accessible")
        
        print("\n✅ Test completed!")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("   Make sure mqtt_manager.py is in the correct path")
        print("   Install required packages: pip install paho-mqtt")
    except Exception as e:
        print(f"❌ Test Error: {e}")

if __name__ == "__main__":
    test_mqtt_manager()