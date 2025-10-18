import paho.mqtt.client as mqtt
from django.core.management.base import BaseCommand
from django.utils import timezone
from iot_dashboard.models import Device

# --- Configuration ---
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
LED_STATUS_TOPIC = "thaitechzone/v2_board/state/led"  # ESP32 ส่งสถานะมา
LED_CONTROL_TOPIC = "thaitechzone/v2_board/control/led"  # เราส่งคำสั่งไป
LED_FEEDBACK_TOPIC = "thaitechzone/v2_board/feedback/led"  # ESP32 ตอบกลับ

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✅ Connected to MQTT Broker successfully!")
        # Subscribe to multiple topics
        client.subscribe(LED_STATUS_TOPIC, qos=1)
        client.subscribe(LED_FEEDBACK_TOPIC, qos=1)
        print(f"📡 Subscribed to topics:")
        print(f"   • {LED_STATUS_TOPIC}")
        print(f"   • {LED_FEEDBACK_TOPIC}")
    else:
        print(f"❌ Failed to connect to MQTT Broker. Code: {rc}")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode('utf-8').upper()
    timestamp = timezone.now().strftime("%H:%M:%S")
    
    print(f"[{timestamp}] 📨 Received: {topic} -> {payload}")

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
            print(f"⚠️  Unknown payload: {payload}")
            return
            
        led_device.save()
        
        # แสดงการเปลี่ยนแปลง
        if previous_status != led_device.is_on:
            status_change = "🟢 ON" if led_device.is_on else "⚫ OFF"
            print(f"🔄 Status changed: {led_device.name} -> {status_change}")
        else:
            print(f"✅ Status confirmed: {led_device.name} is {'ON' if led_device.is_on else 'OFF'}")
            
    except Exception as e:
        print(f"❌ Error processing message: {e}")

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