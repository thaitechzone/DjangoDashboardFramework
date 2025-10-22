# 📋 คู่มือการใช้งาน ESP32 Board ID System

## 🎯 ภาพรวม

ระบบ Board ID ช่วยให้คุณสามารถควบคุม ESP32 หลายตัวพร้อมกันได้โดยไม่เกิดการชนกันของ MQTT Topics

### ✨ ฟีเจอร์หลัก

- 🔧 **รองรับหลายบอร์ด**: สามารถใช้งาน ESP32 หลายตัวพร้อมกัน
- 🆔 **Board ID แบบยืดหยุ่น**: กำหนด ID เองได้ตามต้องการ
- 🔄 **Backward Compatible**: ยังใช้งานกับโค้ดเดิมได้
- 📊 **แยกข้อมูลต่างบอร์ด**: ข้อมูล sensor แยกตาม board_id
- 🎛️ **ควบคุมแยกอิสระ**: แต่ละบอร์ดควบคุมได้อิสระ

---

## 📐 โครงสร้าง MQTT Topics

### รูปแบบ Topic ใหม่

```
thaitechzone/{board_id}/{category}/{type}
```

**ตัวอย่าง:**
```
thaitechzone/board_01/control/led      # ส่งคำสั่งควบคุม LED ของ board_01
thaitechzone/board_01/state/relay1     # รับสถานะ relay1 จาก board_01
thaitechzone/board_02/sensor/data      # รับข้อมูล sensor จาก board_02
```

### หมวดหมู่ (Categories)

| Category | ทิศทาง | คำอธิบาย |
|----------|--------|----------|
| `control` | Dashboard → ESP32 | ส่งคำสั่งควบคุม |
| `state` | ESP32 → Dashboard | รับสถานะปัจจุบัน |
| `status` | ESP32 → Dashboard | รับสถานะ (LED) |
| `sensor` | ESP32 → Dashboard | รับข้อมูล sensor |

### ประเภท (Types)

| Type | คำอธิบาย |
|------|----------|
| `led` | หลอด LED onboard |
| `relay1` | รีเลย์ช่องที่ 1 |
| `relay2` | รีเลย์ช่องที่ 2 |
| `relay3` | รีเลย์ช่องที่ 3 |
| `data` | ข้อมูล sensor (temperature, humidity) |

---

## 🔧 การตั้งค่า ESP32

### 1. แก้ไขโค้ด Arduino

เปิดไฟล์ `.ino` และเพิ่มการกำหนด Board ID:

```cpp
// ===== Board Configuration =====
const char* BOARD_ID = "board_01";  // 🔥 เปลี่ยนให้แตกต่างกันในแต่ละบอร์ด

// ===== MQTT Topics (Dynamic with Board ID) =====
String LED_CONTROL_TOPIC;
String LED_STATE_TOPIC;
String RELAY1_CONTROL_TOPIC;
String RELAY2_CONTROL_TOPIC;
String RELAY3_CONTROL_TOPIC;
String RELAY1_STATE_TOPIC;
String RELAY2_STATE_TOPIC;
String RELAY3_STATE_TOPIC;
String SENSOR_DATA_TOPIC;

void setupTopics() {
  // สร้าง topics แบบ dynamic
  String base = String("thaitechzone/") + BOARD_ID;
  
  LED_CONTROL_TOPIC = base + "/control/led";
  LED_STATE_TOPIC = base + "/status/led";
  
  RELAY1_CONTROL_TOPIC = base + "/control/relay1";
  RELAY2_CONTROL_TOPIC = base + "/control/relay2";
  RELAY3_CONTROL_TOPIC = base + "/control/relay3";
  
  RELAY1_STATE_TOPIC = base + "/state/relay1";
  RELAY2_STATE_TOPIC = base + "/state/relay2";
  RELAY3_STATE_TOPIC = base + "/state/relay3";
  
  SENSOR_DATA_TOPIC = base + "/sensor/data";
  
  Serial.println("📋 Topics configured for board: " + String(BOARD_ID));
}
```

### 2. อัปเดต setup()

```cpp
void setup() {
  Serial.begin(115200);
  delay(1000);
  
  // Initialize topics
  setupTopics();
  
  // ... (rest of setup code)
}
```

### 3. อัปเดต callback()

```cpp
void callback(char* topic, byte* payload, unsigned int length) {
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  message.toUpperCase();
  
  Serial.print("📨 Message received [");
  Serial.print(topic);
  Serial.print("]: ");
  Serial.println(message);

  // LED Control
  if (String(topic) == LED_CONTROL_TOPIC) {
    if (message == "ON") {
      digitalWrite(LED_PIN, HIGH);
      Serial.println("💡 LED turned ON");
    } else if (message == "OFF") {
      digitalWrite(LED_PIN, LOW);
      Serial.println("🌑 LED turned OFF");
    }
    publishLedState();
  }
  // Relay 1 Control
  else if (String(topic) == RELAY1_CONTROL_TOPIC) {
    if (message == "ON") {
      digitalWrite(RELAY1_PIN, LOW);
      Serial.println("🔌 Relay 1 turned ON");
    } else if (message == "OFF") {
      digitalWrite(RELAY1_PIN, HIGH);
      Serial.println("🔌 Relay 1 turned OFF");
    }
    publishRelayState(1);
  }
  // ... (ทำเช่นเดียวกันกับ relay2 และ relay3)
}
```

### 4. อัปเดตการ Subscribe

```cpp
void reconnectMQTT() {
  while (!mqttClient.connected()) {
    Serial.print("🔄 Connecting to MQTT Broker...");
    
    String clientId = String("ESP32_") + BOARD_ID + "_" + String(random(0xffff), HEX);
    
    if (mqttClient.connect(clientId.c_str())) {
      Serial.println(" Connected! ✅");
      
      // Subscribe to control topics
      mqttClient.subscribe(LED_CONTROL_TOPIC.c_str());
      mqttClient.subscribe(RELAY1_CONTROL_TOPIC.c_str());
      mqttClient.subscribe(RELAY2_CONTROL_TOPIC.c_str());
      mqttClient.subscribe(RELAY3_CONTROL_TOPIC.c_str());
      
      Serial.println("📥 Subscribed to all control topics");
      
      // Publish initial states
      publishLedState();
      publishRelayState(1);
      publishRelayState(2);
      publishRelayState(3);
      
    } else {
      Serial.print(" Failed ❌ Error code: ");
      Serial.println(mqttClient.state());
      delay(5000);
    }
  }
}
```

### 5. อัปเดตการส่ง Sensor Data

```cpp
void publishSensorDataJSON(float temperature, float humidity) {
  if (!mqttClient.connected()) return;
  
  // สร้าง JSON payload
  StaticJsonDocument<200> doc;
  doc["device"] = BOARD_ID;
  doc["temperature"] = temperature;
  doc["humidity"] = humidity;
  doc["timestamp"] = millis();
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  // Publish to sensor data topic
  if (mqttClient.publish(SENSOR_DATA_TOPIC.c_str(), jsonString.c_str())) {
    Serial.print("📤 Sensor data published: ");
    Serial.println(jsonString);
  }
}
```

---

## 🌐 การใช้งานบน Dashboard

### 1. เข้าถึง Dashboard พร้อม Board ID

```
http://localhost:8000/?board_id=board_01
```

### 2. เลือกบอร์ดจาก Dropdown (Coming Soon)

Dashboard จะมี dropdown สำหรับเลือกบอร์ดที่ต้องการควบคุม

### 3. ควบคุมอุปกรณ์

ปุ่มควบคุมทั้งหมดจะทำงานกับบอร์ดที่เลือกไว้

---

## 💾 โครงสร้างฐานข้อมูล

### Device Model

```python
class Device(models.Model):
    board_id = models.CharField(max_length=50, default="v2_board")
    name = models.CharField(max_length=100)
    is_on = models.BooleanField(default=False)
    last_updated = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ['board_id', 'name']
```

### Relay Model

```python
class Relay(models.Model):
    board_id = models.CharField(max_length=50, default="v2_board")
    name = models.CharField(max_length=100, default="Relay Control")
    relay1_status = models.BooleanField(default=False)
    relay2_status = models.BooleanField(default=False)
    relay3_status = models.BooleanField(default=False)
    last_updated = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ['board_id', 'name']
```

### SensorData Model

```python
class SensorData(models.Model):
    board_id = models.CharField(max_length=50, default="v2_board")
    device_name = models.CharField(max_length=100, default="ESP32_DHT22")
    temperature = models.FloatField(null=True, blank=True)
    humidity = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['board_id', '-timestamp']),
        ]
```

---

## 🔄 Migration Guide

### สำหรับ Installation เดิม

1. **Backup ฐานข้อมูล**
   ```bash
   cp db.sqlite3 db.sqlite3.backup
   ```

2. **รัน Migration**
   ```bash
   python manage.py migrate
   ```

3. **อัปเดต Board ID** (ถ้าต้องการ)
   ```bash
   python manage.py shell
   ```
   ```python
   from iot_dashboard.models import Device, Relay, SensorData
   
   # อัปเดต Device
   Device.objects.all().update(board_id='v2_board')
   
   # อัปเดต Relay
   Relay.objects.all().update(board_id='v2_board')
   
   # อัปเดต SensorData
   SensorData.objects.all().update(board_id='v2_board')
   ```

4. **อัปเดต ESP32 Code**
   - ใช้โค้ดตัวอย่างด้านบน
   - เปลี่ยน `BOARD_ID` ให้แตกต่างกันในแต่ละบอร์ด

---

## 📝 ตัวอย่างการใช้งาน

### Scenario 1: ห้องนั่งเล่นและห้องนอน

```cpp
// ESP32 ห้องนั่งเล่น
const char* BOARD_ID = "living_room";

// ESP32 ห้องนอน
const char* BOARD_ID = "bedroom";
```

**Topics ที่ใช้:**
```
thaitechzone/living_room/control/led
thaitechzone/living_room/state/relay1
thaitechzone/bedroom/control/led
thaitechzone/bedroom/sensor/data
```

### Scenario 2: โรงเรือน 3 แปลง

```cpp
// โรงเรือนที่ 1
const char* BOARD_ID = "greenhouse_1";

// โรงเรือนที่ 2
const char* BOARD_ID = "greenhouse_2";

// โรงเรือนที่ 3
const char* BOARD_ID = "greenhouse_3";
```

---

## 🐛 Troubleshooting

### ปัญหา: ESP32 ไม่ได้รับคำสั่ง

**ตรวจสอบ:**
1. `BOARD_ID` ตรงกันระหว่าง ESP32 และ Dashboard หรือไม่
2. ESP32 subscribe topics ที่ถูกต้องหรือไม่
3. ตรวจสอบ Serial Monitor ว่ามีข้อความ error หรือไม่

**วิธีแก้:**
```cpp
// เพิ่มการ debug
Serial.print("Board ID: ");
Serial.println(BOARD_ID);
Serial.print("LED Control Topic: ");
Serial.println(LED_CONTROL_TOPIC);
```

### ปัญหา: Dashboard ไม่แสดงข้อมูล

**ตรวจสอบ:**
1. เปิด Dashboard ด้วย URL ที่มี `board_id` ที่ถูกต้อง
2. ตรวจสอบฐานข้อมูลว่ามีข้อมูลของ board นั้นหรือไม่

**วิธีแก้:**
```bash
python manage.py shell
```
```python
from iot_dashboard.models import SensorData
SensorData.objects.filter(board_id='board_01').count()
```

### ปัญหา: หลายบอร์ดทำงานพร้อมกัน

**สาเหตุ:** `BOARD_ID` ซ้ำกัน

**วิธีแก้:**
- ตรวจสอบว่าแต่ละบอร์ดมี `BOARD_ID` ที่ไม่ซ้ำกัน
- ใช้รูปแบบ: `board_01`, `board_02`, `board_03` เป็นต้น

---

## 🎓 Best Practices

### 1. ตั้งชื่อ Board ID

✅ **ดี:**
- `living_room`
- `bedroom_1`
- `greenhouse_a`
- `office_floor2`

❌ **ไม่ดี:**
- `board` (ไม่มีความหมาย)
- `123` (ไม่ชัดเจน)
- `test` (สำหรับทดสอบเท่านั้น)

### 2. จัดการ Topics

- ใช้ตัวพิมพ์เล็กสำหรับ Board ID
- หลีกเลี่ยงอักขระพิเศษ (ใช้ `_` แทน space)
- เก็บ Board ID ไว้ใน EEPROM สำหรับ production

### 3. Monitoring

- เก็บ log ของแต่ละบอร์ด
- ตรวจสอบ heartbeat จากแต่ละบอร์ด
- ตั้งเตือนเมื่อบอร์ดขาดการเชื่อมต่อ

---

## 📚 API Reference

### MQTT Manager

```python
from iot_dashboard.mqtt_manager import get_mqtt_manager

manager = get_mqtt_manager()

# Add board to track
manager.add_board('board_01')

# Send LED command
manager.send_led_command('ON', board_id='board_01')

# Send relay command
manager.send_relay_command(1, 'ON', board_id='board_01')

# Get topic
topic = manager.get_topic('board_01', 'control', 'led')
# Returns: "thaitechzone/board_01/control/led"

# Get tracked boards
boards = manager.get_tracked_boards()
```

### Django Views

```python
# Get data for specific board
from iot_dashboard.models import SensorData

# Latest sensor data
latest = SensorData.objects.filter(board_id='board_01').order_by('-timestamp').first()

# Recent readings
recent = SensorData.objects.filter(board_id='board_01').order_by('-timestamp')[:20]

# All boards
all_boards = SensorData.objects.values_list('board_id', flat=True).distinct()
```

---

## 🔮 Future Enhancements

- [ ] Board management UI (เพิ่ม/ลบ/แก้ไข board)
- [ ] Board status monitoring (online/offline)
- [ ] Multi-board dashboard view (แสดงหลายบอร์ดพร้อมกัน)
- [ ] Board grouping (จัดกลุ่มบอร์ด)
- [ ] Permission system (จำกัดการเข้าถึงแต่ละบอร์ด)
- [ ] Board activity history
- [ ] Alert system per board

---

## 📞 การสนับสนุน

หากมีปัญหาหรือข้อสงสัย:
- 📧 Email: thaitechzone@gmail.com
- 💬 Facebook: ThaiTechZone Community
- 🐛 GitHub Issues: [github.com/thaitechzone/DjangoDashboardFramework/issues](https://github.com/thaitechzone/DjangoDashboardFramework/issues)

---

**📌 หมายเหตุ:** คู่มือนี้สำหรับ Django IoT Dashboard Framework พร้อม Board ID Support

**เวอร์ชัน:** 2.0  
**อัปเดตล่าสุด:** October 2025
