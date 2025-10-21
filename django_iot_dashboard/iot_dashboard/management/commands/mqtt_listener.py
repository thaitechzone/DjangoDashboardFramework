import paho.mqtt.client as mqtt
import json
from django.core.management.base import BaseCommand
from django.utils import timezone
from iot_dashboard.models import Device, SensorData

# --- Configuration ---
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
LED_STATUS_TOPIC = "thaitechzone/v2_board1/state/led"  # ESP32 ส่งสถานะมา
LED_CONTROL_TOPIC = "thaitechzone/v2_board1/control/led"  # เราส่งคำสั่งไป
LED_FEEDBACK_TOPIC = "thaitechzone/v2_board1/feedback/led"  # ESP32 ตอบกลับ
SENSOR_DATA_TOPIC = "thaitechzone/v2_board1/sensor/data"  # ESP32 ส่งข้อมูล sensor (แก้จาก sensors → sensor)

# RELAY Topics
RELAY1_STATE_TOPIC = "thaitechzone/v2_board1/state/relay1"
RELAY2_STATE_TOPIC = "thaitechzone/v2_board1/state/relay2"
RELAY3_STATE_TOPIC = "thaitechzone/v2_board1/state/relay3"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✅ Connected to MQTT Broker successfully!")
        # Subscribe to multiple topics
        client.subscribe(LED_STATUS_TOPIC, qos=1)
        client.subscribe(LED_FEEDBACK_TOPIC, qos=1)
        client.subscribe(SENSOR_DATA_TOPIC, qos=1)
        client.subscribe(RELAY1_STATE_TOPIC, qos=1)
        client.subscribe(RELAY2_STATE_TOPIC, qos=1)
        client.subscribe(RELAY3_STATE_TOPIC, qos=1)
        print(f"📡 Subscribed to topics:")
        print(f"   • {LED_STATUS_TOPIC}")
        print(f"   • {LED_FEEDBACK_TOPIC}")
        print(f"   • {SENSOR_DATA_TOPIC}")
        print(f"   • {RELAY1_STATE_TOPIC}")
        print(f"   • {RELAY2_STATE_TOPIC}")
        print(f"   • {RELAY3_STATE_TOPIC}")
    else:
        print(f"❌ Failed to connect to MQTT Broker. Code: {rc}")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode('utf-8')
    timestamp = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"\n[{timestamp}] 📨 Message Received:")
    print(f"  Topic: {topic}")
    print(f"  Payload: {payload}")

    try:
        # Handle LED status/feedback messages
        if topic in [LED_STATUS_TOPIC, LED_FEEDBACK_TOPIC]:
            handle_led_message(payload.upper())
        
        # Handle sensor data messages
        elif topic == SENSOR_DATA_TOPIC:
            handle_sensor_message(payload)
        
        # Handle RELAY state messages
        elif topic in [RELAY1_STATE_TOPIC, RELAY2_STATE_TOPIC, RELAY3_STATE_TOPIC]:
            handle_relay_message(topic, payload.upper())
        
        else:
            print(f"⚠️  Unknown topic: {topic}")
            
    except Exception as e:
        print(f"❌ Error processing message: {e}")
        import traceback
        traceback.print_exc()


def handle_led_message(payload):
    """จัดการข้อความสำหรับ LED"""
    try:
        # Get or create the Device object for the LED
        led_device, created = Device.objects.get_or_create(name="Onboard LED")
        
        if created:
            print(f"🆕 Created new device: {led_device.name}")

        # Update the status in the database
        previous_status = led_device.is_on
        
        if payload == "ON":
            led_device.is_on = True
        elif payload == "OFF":
            led_device.is_on = False
        else:
            print(f"⚠️  Unknown LED payload: {payload}")
            return
            
        led_device.save()
        
        # แสดงการเปลี่ยนแปลง
        if previous_status != led_device.is_on:
            status_change = "🟢 ON" if led_device.is_on else "⚫ OFF"
            print(f"🔄 LED Status changed: {led_device.name} -> {status_change}")
        else:
            print(f"✅ LED Status confirmed: {led_device.name} is {'ON' if led_device.is_on else 'OFF'}")
            
    except Exception as e:
        print(f"❌ Error handling LED message: {e}")


def handle_relay_message(topic, payload):
    """จัดการข้อความสำหรับ RELAY state"""
    try:
        from iot_dashboard.models import Relay
        
        # หา relay number จาก topic
        if "relay1" in topic:
            relay_num = 1
        elif "relay2" in topic:
            relay_num = 2
        elif "relay3" in topic:
            relay_num = 3
        else:
            print(f"⚠️  Unknown RELAY topic: {topic}")
            return
        
        # Get or create Relay controller
        relay_controller, created = Relay.objects.get_or_create(name="Relay Controller")
        if created:
            print(f"🆕 Created new RELAY controller")
        
        # Update status
        field_name = f"relay{relay_num}_status"
        old_status = getattr(relay_controller, field_name)
        new_status = (payload == "ON")
        setattr(relay_controller, field_name, new_status)
        relay_controller.save()
        
        # แสดงผล
        status_icon = "🟢" if new_status else "⚫"
        print(f"⚡ RELAY {relay_num} Status: {status_icon} {payload}")
        if old_status != new_status:
            print(f"  → Changed from {'ON' if old_status else 'OFF'} to {payload}")
        print(f"✅ RELAY {relay_num} state saved to database")
        
    except Exception as e:
        print(f"❌ Error handling RELAY message: {e}")
        import traceback
        traceback.print_exc()


def handle_sensor_message(payload):
    """จัดการข้อความสำหรับ sensor data"""
    try:
        # พยายาม parse JSON
        try:
            data = json.loads(payload)
            temperature = data.get('temperature')
            humidity = data.get('humidity')
            device_name = data.get('device_name', 'ESP32_DHT22')
            
            print(f"  📊 Parsed JSON data:")
            print(f"     Temperature: {temperature}°C")
            print(f"     Humidity: {humidity}%")
            
        except json.JSONDecodeError:
            # ถ้าไม่ใช่ JSON ลองแยกด้วย comma (format: temp,humidity)
            parts = payload.split(',')
            if len(parts) >= 2:
                temperature = float(parts[0])
                humidity = float(parts[1])
                device_name = 'ESP32_DHT22'
                print(f"  📊 Parsed CSV data:")
                print(f"     Temperature: {temperature}°C")
                print(f"     Humidity: {humidity}%")
            else:
                print(f"⚠️  Invalid sensor data format: {payload}")
                print(f"  Expected: JSON {{'temperature': 28.5, 'humidity': 65.2}}")
                print(f"  Or CSV: 28.5,65.2")
                return
        
        # บันทึกลง database
        sensor_data = SensorData.objects.create(
            device_name=device_name,
            temperature=temperature,
            humidity=humidity,
            timestamp=timezone.now()
        )
        
        print(f"🌡️  Temperature: {sensor_data.get_temperature_display()}")
        print(f"💧 Humidity: {sensor_data.get_humidity_display()}")
        print(f"✅ Sensor data saved to database (ID: {sensor_data.id})")
        
        # นับจำนวน records
        total_count = SensorData.objects.count()
        print(f"📊 Total sensor records in database: {total_count}")
        
        # ลบข้อมูลเก่าเกิน 100 records เพื่อประหยัดพื้นที่
        if total_count > 100:
            old_data = SensorData.objects.all().order_by('-timestamp')[100:]
            count = old_data.count()
            if count > 0:
                SensorData.objects.filter(id__in=[item.id for item in old_data]).delete()
                print(f"🗑️  Cleaned up {count} old sensor records")
            
    except Exception as e:
        print(f"❌ Error handling sensor message: {e}")
        import traceback
        traceback.print_exc()

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("❌ Unexpected disconnection from MQTT broker")
    else:
        print("👋 Disconnected from MQTT broker")

def on_subscribe(client, userdata, mid, granted_qos):
    print(f"✅ Subscription confirmed with QoS: {granted_qos}")

class Command(BaseCommand):
    help = 'Starts the MQTT listener script for IoT Dashboard'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output',
        )

    def handle(self, *args, **kwargs):
        verbose = kwargs.get('verbose', False)
        
        print("🚀 Starting MQTT Listener for IoT Dashboard...")
        print(f"🌐 Broker: {MQTT_BROKER}:{MQTT_PORT}")
        print("=" * 50)
        
        try:
            # สร้าง MQTT client
            client = mqtt.Client()
            
            # ตั้งค่า callback functions
            client.on_connect = on_connect
            client.on_message = on_message
            client.on_disconnect = on_disconnect
            client.on_subscribe = on_subscribe
            
            # เชื่อมต่อกับ broker
            print(f"🔄 Connecting to {MQTT_BROKER}...")
            client.connect(MQTT_BROKER, MQTT_PORT, 60)
            
            self.stdout.write(
                self.style.SUCCESS('✅ MQTT listener started successfully!')
            )
            self.stdout.write(
                self.style.WARNING('📱 Ready to receive messages from ESP32...')
            )
            self.stdout.write(
                self.style.WARNING('🛑 Press Ctrl+C to stop')
            )
            
            # Blocking call ที่ประมวลผล network traffic
            client.loop_forever()
            
        except KeyboardInterrupt:
            print("\n🛑 MQTT Listener stopped by user")
            self.stdout.write(
                self.style.WARNING('👋 MQTT listener stopped')
            )
        except Exception as e:
            print(f"\n❌ Error: {e}")
            self.stdout.write(
                self.style.ERROR(f'❌ MQTT listener error: {e}')
            )