
-----

````markdown
# Prompt for GitHub Copilot: Create First IoT Dashboard Page to Display LED Status

**Goal:** Build the first complete feature of our IoT dashboard. This involves creating a web page that displays the live status (ON/OFF) of a single device, the ESP32's onboard LED (GPIO2).

This requires creating a database model, a view, a URL, and a template, plus a background script to listen for MQTT messages.

---

### Step 1: Install MQTT Client Library

First, we need a library for Django to communicate with the MQTT broker.

1.  Ensure the virtual environment is active.
2.  Install the `paho-mqtt` library.
3.  Update the `requirements.txt` file.

**Provide the shell commands:**

```bash
pip install paho-mqtt
pip freeze > requirements.txt
````

-----

### Step 2: Create the Database Model (`iot_dashboard/models.py`)

Define a simple model to represent a controllable device in our database. This will store the state of our LED.

**Modify `iot_dashboard/models.py`:**

```python
from django.db import models

class Device(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_on = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} is {'ON' if self.is_on else 'OFF'}"
```

After creating the model, generate and apply the database migrations.

**Provide the shell commands:**

```bash
python manage.py makemigrations iot_dashboard
python manage.py migrate
```

-----

### Step 3: Create the MQTT Listener Script

This is a background script that will listen for MQTT messages from the ESP32 and update our database. Django can run such scripts as "management commands".

1.  Create the necessary directory structure: `iot_dashboard/management/commands/`.
2.  Create a new file named `mqtt_listener.py` inside the `commands` directory.
3.  Write the Python script to connect to an MQTT broker, subscribe to a topic for the LED's status, and update the `Device` model when a message is received.

**Create the file `iot_dashboard/management/commands/mqtt_listener.py`:**

```python
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
```

-----

### Step 4: Create the View and Template

Now, create the components to display the data from the database on a web page.

**1. Create the View (`iot_dashboard/views.py`):**
This function fetches the LED's status from the database and passes it to the template.

```python
from django.shortcuts import render
from .models import Device

def dashboard_view(request):
    # Get the LED device object. Use get_or_create to avoid errors on first run.
    led_device, created = Device.objects.get_or_create(name="Onboard LED")
    
    context = {
        'led': led_device
    }
    return render(request, 'iot_dashboard/dashboard.html', context)
```

**2. Create the Template (`iot_dashboard/templates/iot_dashboard/dashboard.html`):**
This HTML file will display the device's name and status. Create the `templates` and `iot_dashboard` subdirectories first.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>IoT Dashboard</title>
    <style>
        body { font-family: sans-serif; padding: 20px; }
        .device { border: 1px solid #ccc; padding: 15px; margin: 10px; border-radius: 8px; width: 200px; }
        .status-on { color: green; font-weight: bold; }
        .status-off { color: grey; font-weight: bold; }
    </style>
</head>
<body>
    <h1>My IoT Dashboard</h1>

    <div class="device">
        <h2>{{ led.name }}</h2>
        <p>
            Status:
            {% if led.is_on %}
                <span class="status-on">ON</span>
            {% else %}
                <span class="status-off">OFF</span>
            {% endif %}
        </p>
    </div>

</body>
</html>
```

-----

### Step 5: Configure the URLs

Finally, tell Django which URL should trigger our `dashboard_view`.

**1. Create `iot_dashboard/urls.py`:**

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
]
```

**2. Update `dashboard_project/urls.py`:**
Include the URLs from our `iot_dashboard` app.

```python
from django.contrib import admin
from django.urls import path, include # Add 'include'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('iot_dashboard.urls')), # <<< Add this line
]
```

-----

### Step 6: How to Run Everything

To see the result, I will need to run two processes simultaneously in two separate terminals.

**Terminal 1: Run the MQTT Listener**

```bash
# (Activate virtual environment first)
python manage.py mqtt_listener
```

**Terminal 2: Run the Django Web Server**

```bash
# (Activate virtual environment first)
python manage.py runserver
```

Now, I can open `http://127.0.0.1:8000/` in my browser. When a message "ON" or "OFF" is published to the `thaitechzone/v2_board/state/led` topic, the status on the web page should update after a refresh.

```
```