

-----

### \#\# ส่วนที่ 1: 🤖 อัปเกรด ESP32 ให้อ่านและส่งค่า Temp/Humid

ก่อนอื่น เราต้องเชื่อมต่อเซ็นเซอร์กับ ESP32 และเขียนโค้ดให้อ่านค่าแล้วส่งไปยัง MQTT Broker ครับ เซ็นเซอร์ที่นิยมและง่ายที่สุดสำหรับผู้เริ่มต้นคือ **DHT22** (หรือ DHT11)

#### **การเชื่อมต่อฮาร์ดแวร์**

เชื่อมต่อเซ็นเซอร์ DHT22 เข้ากับบอร์ด ESP32 ของคุณ:

  * **VCC (+):** ต่อเข้ากับขา **3.3V**
  * **GND (-):** ต่อเข้ากับขา **GND**
  * **DATA:** ต่อเข้ากับขา **GPIO 26** (หรือขาอื่นที่ว่าง)

#### **Prompt สำหรับ ESP32 (คัดลอกทั้งหมดนี้ไปใช้ได้เลย)**

````markdown
# Prompt for Copilot: Add DHT22 Sensor to ESP32 for MQTT Publishing

**Goal:** Modify the existing ESP32 application to read temperature and humidity data from a DHT22 sensor and publish these readings to specific MQTT topics every 30 seconds.

---

### 1. Update PlatformIO Configuration (`platformio.ini`)

Add the necessary libraries for the DHT sensor. The `Adafruit Unified Sensor` is a required dependency.

```ini
[env:esp32dev]
platform = espressif32
board = esp32dev
framework = arduino
monitor_speed = 115200

# Library dependencies
lib_deps =
  knolleary/PubSubClient@^2.8
  adafruit/Adafruit Unified Sensor
  adafruit/DHT sensor library
````

-----

### 2\. Modify Main Application Code (`src/main.cpp`)

Update the code to initialize the sensor, read data periodically, and publish it.

#### a. Add New Headers and Definitions

Include the DHT library and define the sensor pin, type, and new MQTT topics.

```cpp
// Near the top of the file, after the other includes
#include <Adafruit_Sensor.h>
#include <DHT.h>

// ===== Pin Definitions =====
#define LED_PIN 2
#define DHT_PIN 26      // The GPIO pin connected to the DHT22 data pin
#define DHT_TYPE DHT22  // We are using the DHT22 sensor

// ... (WiFi Configuration remains the same) ...

// ===== MQTT Configuration =====
// ... (Existing MQTT config) ...
// --- Add New MQTT Topics for Sensors ---
const char* TEMPERATURE_STATE_TOPIC = "thaitechzone/v2_board/state/temperature";
const char* HUMIDITY_STATE_TOPIC = "thaitechzone/v2_board/state/humidity";
```

#### b. Add New Global Objects and Timers

Instantiate the DHT object and create a new timer for reading the sensor.

```cpp
// ===== Global Objects =====
// ... (Existing WiFi and MQTT objects) ...
DHT dht(DHT_PIN, DHT_TYPE);
unsigned long last_sensor_read_time = 0;
const long sensor_read_interval = 30000; // Read sensor every 30 seconds
```

#### c. Modify the `setup()` Function

Initialize the DHT sensor.

```cpp
// Inside the setup() function, after pinMode for the LED
Serial.println("Initializing DHT22 sensor...");
dht.begin();
```

#### d. Modify the `loop()` Function

Add a new non-blocking timer to read and publish sensor data.

```cpp
// Inside the loop() function, after the mqttClient.loop() call

// --- Periodically read and publish sensor data ---
unsigned long now = millis();
if (now - last_sensor_read_time > sensor_read_interval) {
    last_sensor_read_time = now;

    // Read temperature and humidity
    float humidity = dht.readHumidity();
    float temperature = dht.readTemperature(); // Read in Celsius

    // Check if any reads failed and exit early (to try again later)
    if (isnan(humidity) || isnan(temperature)) {
        Serial.println("Failed to read from DHT sensor!");
        return;
    }

    // Convert readings to a string format (char array)
    char tempString[8];
    dtostrf(temperature, 4, 1, tempString); // 4 is width, 1 is precision

    char humidString[8];
    dtostrf(humidity, 4, 1, humidString);

    // Publish to MQTT topics if connected
    if (mqttClient.connected()) {
        mqttClient.publish(TEMPERATURE_STATE_TOPIC, tempString, true);
        mqttClient.publish(HUMIDITY_STATE_TOPIC, humidString, true);
        Serial.printf("Published Temp: %s C, Humid: %s %%\n", tempString, humidString);
    }
}
```

````

---

### ## ส่วนที่ 2: 🐍 อัปเกรด Django Dashboard ให้แสดงผล Temp/Humid

ตอนนี้ ESP32 พร้อมส่งข้อมูลแล้ว เรามาปรับ Dashboard ให้พร้อมรับและแสดงผลกันครับ

#### **Prompt สำหรับ Django (คัดลอกทั้งหมดนี้ไปใช้ได้เลย)**

```markdown
# Prompt for Copilot: Display Temperature & Humidity on Django Dashboard

**Goal:** Update the Django project to receive, store, and display temperature and humidity data sent from the ESP32 via MQTT.

---

### 1. Update the Database Model (`iot_dashboard/models.py`)

Create a new model specifically for sensor readings. This is more flexible than adding fields to the `Device` model.

**Add this new model to `iot_dashboard/models.py`:**

```python
# In iot_dashboard/models.py

class SensorReading(models.Model):
    name = models.CharField(max_length=100, unique=True)
    value = models.FloatField(default=0.0)
    unit = models.CharField(max_length=20, default="")
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}: {self.value} {self.unit}"
````

After adding the model, create and run the database migrations.

**Provide the shell commands:**

```bash
python manage.py makemigrations iot_dashboard
python manage.py migrate
```

-----

### 2\. Update the MQTT Listener (`mqtt_listener.py`)

Modify the listener to subscribe to the new sensor topics and update the `SensorReading` model in the database.

**Modify `iot_dashboard/management/commands/mqtt_listener.py`:**

```python
# At the top, import the new model
from iot_dashboard.models import Device, SensorReading

# --- Configuration ---
# ... (existing MQTT config) ...
TEMPERATURE_STATE_TOPIC = "thaitechzone/v2_board/state/temperature"
HUMIDITY_STATE_TOPIC = "thaitechzone/v2_board/state/humidity"

# Update the list of topics to subscribe to
TOPICS_TO_SUBSCRIBE = [
    ("thaitechzone/v2_board/state/led", 0),
    ("thaitechzone/v2_board/state/relay1", 0),
    (TEMPERATURE_STATE_TOPIC, 0), # <<< Add this
    (HUMIDITY_STATE_TOPIC, 0)   # <<< Add this
]

# Modify the on_message function
def on_message(client, userdata, msg):
    # ... (existing logic for led and relay1) ...

    # --- Add logic for new sensor topics ---
    try:
        if msg.topic == TEMPERATURE_STATE_TOPIC:
            temp_value = float(msg.payload.decode('utf-8'))
            # update_or_create is perfect for this: it updates if exists, or creates if not.
            SensorReading.objects.update_or_create(
                name="Temperature",
                defaults={'value': temp_value, 'unit': '°C'}
            )
            print(f"✅ Updated Temperature: {temp_value}°C")

        elif msg.topic == HUMIDITY_STATE_TOPIC:
            humid_value = float(msg.payload.decode('utf-8'))
            SensorReading.objects.update_or_create(
                name="Humidity",
                defaults={'value': humid_value, 'unit': '%'}
            )
            print(f"✅ Updated Humidity: {humid_value}%")

    except Exception as e:
        print(f"❌ Error processing message on topic {msg.topic}: {e}")
```

-----

### 3\. Update the View (`iot_dashboard/views.py`)

Modify the main dashboard view to fetch the new sensor data and pass it to the template.

**Modify `dashboard_view` in `iot_dashboard/views.py`:**

```python
# At the top, import the new model
from .models import Device, SensorReading

def dashboard_view(request):
    # ... (existing logic for led_device and relay1_device) ...
    
    # Fetch sensor readings. Use get_or_create for safety on first run.
    temperature, _ = SensorReading.objects.get_or_create(
        name="Temperature", defaults={'value': 0.0, 'unit': '°C'}
    )
    humidity, _ = SensorReading.objects.get_or_create(
        name="Humidity", defaults={'value': 0.0, 'unit': '%'}
    )
    
    # Add the new data to the context
    context = {
        'led': led_device,
        'relay1': relay1_device,
        'temperature': temperature, # <<< Add this
        'humidity': humidity,       # <<< Add this
    }
    return render(request, 'iot_dashboard/dashboard.html', context)
```

-----

### 4\. Update the Template (`dashboard.html`)

Finally, add new display cards for the temperature and humidity data.

**Add these new blocks inside the `<body>` of `iot_dashboard/templates/iot_dashboard/dashboard.html`:**

```html
    <div class="device">
        <h2>🌡️ {{ temperature.name }}</h2>
        <p class="sensor-reading">
            {{ temperature.value|floatformat:1 }} {{ temperature.unit }}
        </p>
        <small>Last Updated: {{ temperature.last_updated|date:"H:i:s" }}</small>
    </div>

    <div class="device">
        <h2>💧 {{ humidity.name }}</h2>
        <p class="sensor-reading">
            {{ humidity.value|floatformat:1 }} {{ humidity.unit }}
        </p>
        <small>Last Updated: {{ humidity.last_updated|date:"H:i:s" }}</small>
    </div>
```

```

```