import paho.mqtt.client as mqtt
from django.core.management.base import BaseCommand
from iot_dashboard.models import Device

# --- Configuration ---
MQTT_BROKER = "broker.hivemq.com" # Replace with your broker
MQTT_PORT = 1883
LED_STATUS_TOPIC = "thaitechzone/v2_board/state/led" # Topic the ESP32 will publish to

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT Broker with result code {rc}")
    client.subscribe(LED_STATUS_TOPIC)

def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8').upper()
    print(f"Received message on topic {msg.topic}: {payload}")

    # Get or create the Device object for the LED
    led_device, created = Device.objects.get_or_create(name="Onboard LED")

    # Update the status in the database
    if payload == "ON":
        led_device.is_on = True
    elif payload == "OFF":
        led_device.is_on = False
    led_device.save()
    print(f"Updated {led_device.name} status to {led_device.is_on}")

class Command(BaseCommand):
    help = 'Starts the MQTT listener script'

    def handle(self, *args, **kwargs):
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message

        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        self.stdout.write(self.style.SUCCESS('MQTT listener started...'))
        
        # Blocking call that processes network traffic, dispatches callbacks and
        # handles reconnecting.
        client.loop_forever()