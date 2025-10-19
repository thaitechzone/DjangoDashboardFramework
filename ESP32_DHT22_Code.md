# ESP32 + DHT22 Sensor Code สำหรับ Django Dashboard

โค้ดนี้เป็นการพัฒนาต่อยอดจากโค้ด LED Control เพื่อเพิ่มการอ่านค่า Temperature และ Humidity จาก DHT22 Sensor

## 🔧 อุปกรณ์ที่ต้องใช้

### Hardware:
- **ESP32 Development Board**
- **DHT22 (AM2302) Temperature & Humidity Sensor**
- **สาย Jumper Wire** (3 เส้น)
- **Resistor 10kΩ** (1 ตัว - สำหรับ Pull-up)
- **Breadboard** (ทำหรือไม่ทำก็ได้)

### Software:
- **Arduino IDE** พร้อม ESP32 Board Package
- **DHT sensor library** by Adafruit

---

## 🔌 การเชื่อมต่อ Hardware

```
DHT22 Sensor -> ESP32
============================
VCC   (Pin 1) -> 3.3V
DATA  (Pin 2) -> GPIO 4
      (ใส่ Pull-up resistor 10kΩ ระหว่าง VCC และ DATA)
GND   (Pin 4) -> GND

Built-in LED  -> GPIO 2 (ไม่ต้องต่อเพิ่ม)
```

### 📐 Pinout Diagram:
```
DHT22           ESP32
                 
  1 2 3 4       
  │ │ │ │       3.3V ── VCC (1)
  │ │ │ └────── GND  ── GND (4)
  │ │ └──────── ไม่ใช้   (3)
  │ └────┬───── GPIO4 ── DATA (2)
  │      │
  │     10kΩ
  │      │
  └──────┴───── 3.3V (Pull-up)
```

---

## 📚 การติดตั้ง Library

### 1. เปิด Arduino IDE
### 2. ไปที่ Sketch → Include Library → Manage Libraries
### 3. ค้นหาและติดตั้ง:
- **DHT sensor library** by Adafruit
- **Adafruit Unified Sensor** (จะติดตั้งอัตโนมัติ)

---

## 💻 ESP32 Code ที่สมบูรณ์

```cpp
#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

// ===== การตั้งค่า WiFi =====
const char* ssid = "YOUR_WIFI_NAME";           // ⚠️ เปลี่ยนชื่อ WiFi
const char* password = "YOUR_WIFI_PASSWORD";   // ⚠️ เปลี่ยนรหัสผ่าน WiFi

// ===== การตั้งค่า MQTT =====
const char* mqtt_server = "broker.hivemq.com";
const int mqtt_port = 1883;
const char* mqtt_client_id = "ESP32_DHT22_ThaiTechZone_01";

// ===== MQTT Topics =====
const char* led_control_topic = "thaitechzone/v2_board/control/led";
const char* led_state_topic = "thaitechzone/v2_board/state/led";
const char* led_feedback_topic = "thaitechzone/v2_board/feedback/led";
const char* sensor_data_topic = "thaitechzone/v2_board/sensors/data";

// ===== การตั้งค่า Hardware =====
const int LED_PIN = 2;    // Built-in LED
const int DHT_PIN = 4;    // DHT22 Data pin
const int DHT_TYPE = DHT22;

// ===== ตัวแปรสำหรับการทำงาน =====
WiFiClient espClient;
PubSubClient client(espClient);
DHT dht(DHT_PIN, DHT_TYPE);

unsigned long lastSensorRead = 0;
unsigned long lastHeartbeat = 0;
const unsigned long SENSOR_INTERVAL = 10000;  // อ่าน sensor ทุก 10 วินาที
const unsigned long HEARTBEAT_INTERVAL = 30000; // ส่ง heartbeat ทุก 30 วินาที

// ===== ฟังก์ชันเชื่อมต่อ WiFi =====
void connectWiFi() {
  Serial.print("🔄 กำลังเชื่อมต่อ WiFi: ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.println("✅ เชื่อมต่อ WiFi สำเร็จ!");
    Serial.print("📶 IP Address: ");
    Serial.println(WiFi.localIP());
    Serial.print("📡 Signal Strength: ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
  } else {
    Serial.println();
    Serial.println("❌ ไม่สามารถเชื่อมต่อ WiFi ได้!");
  }
}

// ===== ฟังก์ชันเชื่อมต่อ MQTT =====
void connectMQTT() {
  while (!client.connected()) {
    Serial.print("🔄 กำลังเชื่อมต่อ MQTT Broker...");
    
    String clientId = mqtt_client_id;
    clientId += String(random(0xffff), HEX);
    
    if (client.connect(clientId.c_str())) {
      Serial.println(" สำเร็จ! ✅");
      
      // Subscribe เพื่อรับคำสั่งควบคุม LED
      if (client.subscribe(led_control_topic)) {
        Serial.print("📡 Subscribe สำเร็จ: ");
        Serial.println(led_control_topic);
      }
      
      // ส่งสถานะเริ่มต้น
      sendLEDStatus();
      
    } else {
      Serial.print(" ล้มเหลว ❌ Error code: ");
      Serial.println(client.state());
      Serial.println("⏳ ลองใหม่ในอีก 5 วินาที...");
      delay(5000);
    }
  }
}

// ===== ฟังก์ชันจัดการข้อความ MQTT ที่ได้รับ =====
void onMqttMessage(char* topic, byte* payload, unsigned int length) {
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  message.toUpperCase();
  
  Serial.print("📨 ได้รับข้อความ: [");
  Serial.print(topic);
  Serial.print("] ");
  Serial.println(message);
  
  // ตรวจสอบว่าเป็นคำสั่งควบคุม LED หรือไม่
  if (String(topic) == led_control_topic) {
    if (message == "ON") {
      digitalWrite(LED_PIN, HIGH);
      Serial.println("💡 LED เปิด (ON)");
      
      // ส่งการตอบกลับ
      client.publish(led_feedback_topic, "ON", true);
      client.publish(led_state_topic, "ON", true);
      
    } else if (message == "OFF") {
      digitalWrite(LED_PIN, LOW);
      Serial.println("🌑 LED ปิด (OFF)");
      
      // ส่งการตอบกลับ
      client.publish(led_feedback_topic, "OFF", true);
      client.publish(led_state_topic, "OFF", true);
      
    } else {
      Serial.print("❓ คำสั่งไม่รู้จัก: ");
      Serial.println(message);
    }
  }
}

// ===== ฟังก์ชันส่งสถานะ LED =====
void sendLEDStatus() {
  bool isOn = digitalRead(LED_PIN);
  String status = isOn ? "ON" : "OFF";
  
  if (client.publish(led_state_topic, status.c_str(), true)) {
    Serial.print("📤 ส่งสถานะ LED: ");
    Serial.println(status);
  }
}

// ===== ฟังก์ชันอ่านและส่งข้อมูล Sensor =====
void readAndSendSensorData() {
  // อ่านค่าจาก DHT22
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();
  
  // ตรวจสอบว่าอ่านค่าได้หรือไม่
  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("❌ ไม่สามารถอ่านค่าจาก DHT22 Sensor ได้!");
    return;
  }
  
  // แสดงค่าที่อ่านได้
  Serial.println("📊 ข้อมูล Sensor:");
  Serial.print("🌡️  อุณหภูมิ: ");
  Serial.print(temperature);
  Serial.println("°C");
  Serial.print("💧 ความชื้น: ");
  Serial.print(humidity);
  Serial.println("%");
  
  // สร้าง JSON payload
  DynamicJsonDocument doc(200);
  doc["device_name"] = "ESP32_DHT22";
  doc["temperature"] = temperature;
  doc["humidity"] = humidity;
  doc["timestamp"] = millis();
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  // ส่งข้อมูลผ่าน MQTT
  if (client.publish(sensor_data_topic, jsonString.c_str(), true)) {
    Serial.print("📤 ส่งข้อมูล Sensor สำเร็จ: ");
    Serial.println(jsonString);
  } else {
    Serial.println("❌ ไม่สามารถส่งข้อมูล Sensor ได้!");
  }
  
  Serial.println("────────────────────────");
}

// ===== ฟังก์ชัน Setup =====
void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println();
  Serial.println("🚀 เริ่มต้นระบบ ESP32 + DHT22 Sensor");
  Serial.println("=====================================");
  
  // ตั้งค่า LED pin
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  Serial.println("💡 ตั้งค่า LED เสร็จสิ้น (เริ่มต้น: OFF)");
  
  // เริ่มต้น DHT22 sensor
  dht.begin();
  Serial.println("🌡️  เริ่มต้น DHT22 sensor เสร็จสิ้น");
  
  // ทดสอบอ่านค่า sensor ครั้งแรก
  delay(2000); // รอให้ sensor พร้อม
  float testTemp = dht.readTemperature();
  float testHum = dht.readHumidity();
  
  if (!isnan(testTemp) && !isnan(testHum)) {
    Serial.println("✅ DHT22 Sensor ทำงานปกติ");
    Serial.print("🌡️  อุณหภูมิเริ่มต้น: ");
    Serial.print(testTemp);
    Serial.println("°C");
    Serial.print("💧 ความชื้นเริ่มต้น: ");
    Serial.print(testHum);
    Serial.println("%");
  } else {
    Serial.println("⚠️  DHT22 Sensor ยังไม่พร้อม (ลองอีกครั้งหลังจากเชื่อมต่อ WiFi)");
  }
  
  // เชื่อมต่อ WiFi
  connectWiFi();
  
  // ตั้งค่า MQTT
  if (WiFi.status() == WL_CONNECTED) {
    client.setServer(mqtt_server, mqtt_port);
    client.setCallback(onMqttMessage);
    Serial.println("⚙️ ตั้งค่า MQTT เสร็จสิ้น");
  }
  
  Serial.println("✅ Setup เสร็จสิ้น!");
  Serial.println();
}

// ===== ฟังก์ชัน Loop =====
void loop() {
  unsigned long now = millis();
  
  // ตรวจสอบการเชื่อมต่อ WiFi
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("⚠️ WiFi หลุด กำลังเชื่อมต่อใหม่...");
    connectWiFi();
  }
  
  // ตรวจสอบการเชื่อมต่อ MQTT
  if (!client.connected()) {
    connectMQTT();
  }
  
  // ประมวลผลข้อความ MQTT
  client.loop();
  
  // อ่านและส่งข้อมูล Sensor ทุกๆ 10 วินาที
  if (now - lastSensorRead >= SENSOR_INTERVAL) {
    readAndSendSensorData();
    lastSensorRead = now;
  }
  
  // ส่ง LED heartbeat ทุกๆ 30 วินาที
  if (now - lastHeartbeat >= HEARTBEAT_INTERVAL) {
    sendLEDStatus();
    lastHeartbeat = now;
    Serial.println("💓 ส่ง LED heartbeat");
  }
  
  delay(100);
}
```

---

## 🎯 วิธีการใช้งาน

### 1. **เตรียม Hardware:**
   - เชื่อมต่อ DHT22 ตาม Pinout diagram
   - ตรวจสอบการต่อสายให้ถูกต้อง

### 2. **เตรียม Software:**
   - ติดตั้ง DHT sensor library
   - ติดตั้ง ArduinoJson library (Sketch → Include Library → Manage Libraries → ค้นหา "ArduinoJson")

### 3. **แก้ไขการตั้งค่า:**
   - เปลี่ยน WiFi SSID และ Password
   - เปลี่ยน MQTT Client ID ให้เป็นเฉพาะ

### 4. **Upload และทดสอบ:**
   - Upload โค้ดลง ESP32
   - เปิด Serial Monitor (115200 baud)
   - ตรวจสอบการเชื่อมต่อ WiFi และ MQTT

### 5. **ดูผลลัพธ์ใน Dashboard:**
   - เปิด `http://127.0.0.1:8000/`
   - ควรเห็นข้อมูล Temperature และ Humidity

---

## 📊 MQTT Topics ที่ใช้

| Topic | Direction | ความหมาย | Format |
|-------|-----------|----------|---------|
| `thaitechzone/v2_board/control/led` | Dashboard → ESP32 | คำสั่งควบคุม LED | `ON` หรือ `OFF` |
| `thaitechzone/v2_board/state/led` | ESP32 → Dashboard | สถานะ LED | `ON` หรือ `OFF` |
| `thaitechzone/v2_board/feedback/led` | ESP32 → Dashboard | การตอบกลับ | `ON` หรือ `OFF` |
| `thaitechzone/v2_board/sensors/data` | ESP32 → Dashboard | ข้อมูล Sensor | JSON format |

### 📝 ตัวอย่าง JSON สำหรับ Sensor Data:
```json
{
  "device_name": "ESP32_DHT22",
  "temperature": 28.5,
  "humidity": 65.2,
  "timestamp": 123456789
}
```

---

## 🔧 การแก้ไขปัญหา

### ❌ **ปัญหา: DHT22 อ่านค่าไม่ได้**
**ตรวจสอบ:**
- การเชื่อมต่อสายถูกต้องหรือไม่
- ใส่ Pull-up resistor หรือยัง
- DHT22 ใช้ GPIO pin ที่รองรับหรือไม่

**วิธีแก้:**
```cpp
// เพิ่มการ debug
Serial.print("DHT22 Temperature: ");
Serial.println(dht.readTemperature());
Serial.print("DHT22 Humidity: ");
Serial.println(dht.readHumidity());
```

### ❌ **ปัญหา: ข้อมูลไม่ปรากฏใน Dashboard**
**ตรวจสอบ:**
- MQTT Listener ทำงานหรือไม่
- MQTT Topic ถูกต้องหรือไม่
- JSON format ถูกต้องหรือไม่

**วิธีแก้:**
- ดู Serial Monitor ของ ESP32
- ดู Terminal ของ MQTT Listener
- ใช้ MQTT Explorer ตรวจสอบ

### ❌ **ปัญหา: ค่า Sensor ผิดปกติ**
**สาเหตุ:**
- DHT22 ต้องการเวลาในการอ่านค่า
- การอ่านถี่เกินไป

**วิธีแก้:**
```cpp
// เพิ่มเวลารอระหว่างการอ่าน
const unsigned long SENSOR_INTERVAL = 5000; // 5 วินาที
```

---

## 🎊 สรุป

ตอนนี้คุณมีระบบ **IoT Dashboard** ที่สมบูรณ์ที่สุด ซึ่งสามารถ:

✅ **ควบคุม LED** ผ่าน Web Dashboard  
✅ **อ่านค่า Temperature** จาก DHT22  
✅ **อ่านค่า Humidity** จาก DHT22  
✅ **แสดงข้อมูลแบบ Real-time**  
✅ **เก็บประวัติการอ่านค่า**  
✅ **UI สวยงามพร้อม Auto-refresh**  

### 🚀 **ขั้นตอนถัดไป:**
- เพิ่มเซนเซอร์ตัวอื่นๆ (เช่น Light sensor, Motion sensor)
- สร้างกราฟแสดงแนวโน้ม
- เพิ่มระบบแจ้งเตือน
- ทำ Mobile Application

**🎉 ยินดีด้วย! ระบบ IoT แบบครบครันพร้อมใช้งานแล้ว!** 🎊

---

**Created by:** ThaiTechZone  
**Date:** 2025-10-19  
**Version:** 2.0  
**GitHub:** [DjangoDashboardFramework](https://github.com/thaitechzone/DjangoDashboardFramework)