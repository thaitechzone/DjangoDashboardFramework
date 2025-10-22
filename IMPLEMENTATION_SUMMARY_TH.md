# 📖 สรุปการพัฒนา: ระบบ Board ID สำหรับ ESP32

## 🎯 คำถามเดิม
"ช่วยฉันวิเคราะห์ project นี้ หากต้องการให้มีการกำหนด ID ของบอร์ด ESP32 ที่รับส่งผ่าน topic ต่างๆต้องทำอย่างไร"

## ✅ คำตอบและการแก้ปัญหา

### ปัญหาที่พบในระบบเดิม
ระบบเดิมใช้ MQTT Topics แบบคงที่ เช่น:
```
thaitechzone/v2_board/control/led
thaitechzone/v2_board/state/relay1
```

**ปัญหา:** หากมี ESP32 หลายตัวจะใช้ topic เดียวกัน ทำให้:
- ควบคุมทุกบอร์ดพร้อมกัน (ไม่สามารถควบคุมแยกได้)
- ข้อมูล sensor จากหลายบอร์ดรวมกัน (แยกไม่ออก)
- เกิด conflict เมื่อส่งคำสั่ง

### วิธีแก้ปัญหา: ระบบ Board ID

เพิ่มระบบ Board ID เพื่อแยก topic ของแต่ละบอร์ด:
```
thaitechzone/{board_id}/control/led
thaitechzone/{board_id}/state/relay1
```

**ตัวอย่าง:**
- Board 1: `thaitechzone/board_01/control/led`
- Board 2: `thaitechzone/board_02/control/led`
- Board 3: `thaitechzone/living_room/control/led`

---

## 🔧 สิ่งที่ได้ทำการพัฒนา

### 1. ฐานข้อมูล (Database)

เพิ่มฟิลด์ `board_id` ใน 3 ตาราง:

**Device (LED)**
```python
class Device(models.Model):
    board_id = models.CharField(max_length=50, default="v2_board")
    name = models.CharField(max_length=100)
    is_on = models.BooleanField(default=False)
    # ...
```

**Relay (รีเลย์ 3 ช่อง)**
```python
class Relay(models.Model):
    board_id = models.CharField(max_length=50, default="v2_board")
    name = models.CharField(max_length=100)
    relay1_status = models.BooleanField(default=False)
    relay2_status = models.BooleanField(default=False)
    relay3_status = models.BooleanField(default=False)
    # ...
```

**SensorData (ข้อมูล Sensor)**
```python
class SensorData(models.Model):
    board_id = models.CharField(max_length=50, default="v2_board")
    device_name = models.CharField(max_length=100)
    temperature = models.FloatField()
    humidity = models.FloatField()
    # ...
```

### 2. MQTT Manager

เพิ่มฟังก์ชันจัดการ Board ID:

**สร้าง Topic แบบ Dynamic**
```python
def get_topic(self, board_id, category, topic_type):
    """
    สร้าง topic ตาม board_id
    
    ตัวอย่าง:
    get_topic("board_01", "control", "led")
    => "thaitechzone/board_01/control/led"
    """
    return f"{self.TOPIC_PREFIX}/{board_id}/{category}/{topic_type}"
```

**เพิ่ม/ลบ Board**
```python
def add_board(self, board_id):
    """เพิ่มบอร์ดเข้าระบบและ subscribe topics"""
    self.tracked_boards.add(board_id)
    # Subscribe to all topics for this board
    self._subscribe_board_topics(board_id)

def remove_board(self, board_id):
    """ลบบอร์ดออกจากระบบ"""
    self.tracked_boards.discard(board_id)
```

**ส่งคำสั่งไปยังบอร์ดเฉพาะ**
```python
def send_led_command(self, command, board_id=None):
    """ส่งคำสั่ง LED ไปยังบอร์ดที่ระบุ"""
    if board_id is None:
        board_id = self.DEFAULT_BOARD_ID  # "v2_board"
    
    topic = self.get_topic(board_id, "control", "led")
    return self.send_message(topic, command)
```

### 3. MQTT Callbacks

อัปเดตการรับข้อความเพื่อแยก board_id:

**ดึง Board ID จาก Topic**
```python
def extract_board_id_from_topic(topic):
    """
    แยก board_id จาก topic
    
    Input: "thaitechzone/board_01/state/relay1"
    Output: "board_01"
    """
    parts = topic.split('/')
    if len(parts) >= 2:
        return parts[1]  # board_id อยู่ตำแหน่งที่ 2
    return None
```

**จัดการข้อความตาม Board ID**
```python
def handle_relay_state_message(topic, message):
    """รับสถานะ relay จาก ESP32"""
    board_id = extract_board_id_from_topic(topic)
    
    # อัปเดตฐานข้อมูลตาม board_id
    relay, created = Relay.objects.get_or_create(
        board_id=board_id,
        name="ESP32 Relay Controller"
    )
    # ...
```

### 4. Django Views

อัปเดต views ให้รองรับการเลือกบอร์ด:

**Dashboard View**
```python
def dashboard_simple(request):
    # รับ board_id จาก URL query parameter
    selected_board = request.GET.get('board_id', 'v2_board')
    
    # ดึงข้อมูลเฉพาะบอร์ดที่เลือก
    led_device = Device.objects.get_or_create(
        board_id=selected_board,
        name="Onboard LED"
    )
    
    relay = Relay.objects.get_or_create(
        board_id=selected_board,
        name="ESP32 Relay Controller"
    )
    
    sensors = SensorData.objects.filter(
        board_id=selected_board
    ).order_by('-timestamp')[:20]
    
    # ส่งข้อมูลไปยัง template
    context = {
        'led': led_device,
        'relay': relay,
        'sensors': sensors,
        'selected_board': selected_board,
        # ...
    }
```

**Control Views**
```python
def control_led(request):
    board_id = request.POST.get('board_id', 'v2_board')
    action = request.POST.get('action')  # 'on' or 'off'
    
    # ส่งคำสั่งไปยังบอร์ดที่ระบุ
    success = send_led_command(action.upper(), board_id)
    
    # Redirect กลับไปหน้า dashboard ของบอร์ดนั้น
    return redirect(f'dashboard_simple?board_id={board_id}')
```

### 5. ESP32 Arduino Code

สร้างโค้ด ESP32 ใหม่ที่รองรับ Board ID:

**กำหนด Board ID**
```cpp
// กำหนด ID เฉพาะของบอร์ด (ต้องไม่ซ้ำกัน)
const char* BOARD_ID = "board_01";
```

**สร้าง Topics แบบ Dynamic**
```cpp
void setupTopics() {
  String base = String("thaitechzone/") + BOARD_ID;
  
  LED_CONTROL_TOPIC = base + "/control/led";
  LED_STATE_TOPIC = base + "/status/led";
  
  RELAY1_CONTROL_TOPIC = base + "/control/relay1";
  RELAY1_STATE_TOPIC = base + "/state/relay1";
  // ...
}
```

**Subscribe Topics ของบอร์ดเฉพาะ**
```cpp
void reconnectMQTT() {
  if (mqttClient.connect(clientId.c_str())) {
    // Subscribe เฉพาะ topics ของบอร์ดนี้
    mqttClient.subscribe(LED_CONTROL_TOPIC.c_str());
    mqttClient.subscribe(RELAY1_CONTROL_TOPIC.c_str());
    // ...
  }
}
```

**ส่งข้อมูล Sensor พร้อม Board ID**
```cpp
void publishSensorData() {
  StaticJsonDocument<200> doc;
  doc["device"] = BOARD_ID;  // ระบุ board_id
  doc["temperature"] = temperature;
  doc["humidity"] = humidity;
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  mqttClient.publish(SENSOR_DATA_TOPIC.c_str(), jsonString.c_str());
}
```

---

## 📚 เอกสารที่สร้าง

### 1. ESP32_BOARD_ID_GUIDE.md
- คู่มือการใช้งานระบบ Board ID แบบสมบูรณ์
- โครงสร้าง MQTT Topics
- วิธีการตั้งค่า ESP32
- Troubleshooting และ Best Practices
- API Reference

### 2. ESP32_WITH_BOARD_ID.ino
- โค้ด Arduino สำหรับ ESP32 พร้อม Board ID
- รองรับ LED, Relay 3 ช่อง, DHT22 Sensor
- มี comment อธิบายละเอียด
- พร้อมใช้งานจริง

### 3. MULTI_BOARD_QUICK_START.md
- คู่มือเริ่มต้นแบบรวดเร็ว
- ขั้นตอนติดตั้งและตั้งค่า
- ตัวอย่างการใช้งานจริง
- Checklist สำหรับแต่ละบอร์ด

---

## 🎓 วิธีใช้งาน

### สำหรับผู้ใช้งานทั่วไป

**1. ติดตั้งระบบ**
```bash
cd django_iot_dashboard
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install django==5.2.7 paho-mqtt==2.1.0 pytz
python manage.py migrate
python manage.py runserver
```

**2. ตั้งค่า ESP32 ตัวที่ 1**
- เปิดไฟล์ `ESP32_WITH_BOARD_ID.ino`
- เปลี่ยน `BOARD_ID = "board_01"`
- เปลี่ยน WiFi SSID และ Password
- Upload ไปยัง ESP32

**3. ตั้งค่า ESP32 ตัวที่ 2**
- ใช้โค้ดเดียวกัน
- เปลี่ยน `BOARD_ID = "board_02"`  (ต้องไม่ซ้ำกับตัวแรก)
- Upload ไปยัง ESP32 ตัวที่ 2

**4. เข้าใช้งาน Dashboard**
```
Board 1: http://localhost:8000/?board_id=board_01
Board 2: http://localhost:8000/?board_id=board_02
```

### สำหรับนักพัฒนา

**เพิ่มบอร์ดใหม่ใน MQTT Manager**
```python
from iot_dashboard.mqtt_manager import get_mqtt_manager

manager = get_mqtt_manager()
manager.add_board('board_03')  # เพิ่มบอร์ดใหม่
```

**Query ข้อมูลตาม Board ID**
```python
from iot_dashboard.models import SensorData

# ข้อมูล sensor ของ board_01
data = SensorData.objects.filter(board_id='board_01').order_by('-timestamp')[:20]

# บอร์ดทั้งหมดในระบบ
all_boards = SensorData.objects.values_list('board_id', flat=True).distinct()
```

**ส่งคำสั่งไปยังบอร์ดเฉพาะ**
```python
from iot_dashboard.mqtt_manager import send_led_command, send_relay_command

# เปิด LED ของ board_01
send_led_command('ON', board_id='board_01')

# เปิด Relay 1 ของ board_02
send_relay_command(1, 'ON', board_id='board_02')
```

---

## 🌟 ข้อดีของระบบใหม่

### 1. รองรับหลายบอร์ด
- ใช้ ESP32 หลายตัวพร้อมกันได้
- แต่ละบอร์ดมี topics เฉพาะตัว
- ไม่มี conflict ระหว่างบอร์ด

### 2. ความยืดหยุ่นสูง
- กำหนด Board ID ได้ตามต้องการ
- เช่น: `living_room`, `bedroom`, `greenhouse_1`
- ทำให้จำและจัดการง่าย

### 3. แยกข้อมูลชัดเจน
- ข้อมูล sensor แยกตามบอร์ด
- สถานะอุปกรณ์แยกตามบอร์ด
- Query และวิเคราะห์ข้อมูลง่าย

### 4. Backward Compatible
- ระบบเดิมยังใช้งานได้ปกติ
- Default Board ID คือ "v2_board"
- Migration อัตโนมัติ

### 5. Production Ready
- มี error handling
- มี logging
- มี documentation ครบถ้วน

---

## 📊 ตัวอย่างการใช้งานจริง

### Scenario 1: Smart Home (2 ห้อง)

**ESP32 Board 1 - ห้องนั่งเล่น**
```cpp
const char* BOARD_ID = "living_room";
```
- ควบคุม: ไฟห้องนั่งเล่น, พัดลม, เครื่องปรับอากาศ
- URL: `http://localhost:8000/?board_id=living_room`

**ESP32 Board 2 - ห้องนอน**
```cpp
const char* BOARD_ID = "bedroom";
```
- ควบคุม: ไฟห้องนอน, พัดลม
- ติดตาม: อุณหภูมิ, ความชื้น
- URL: `http://localhost:8000/?board_id=bedroom`

### Scenario 2: โรงเรือนอัจฉริยะ (3 แปลง)

```cpp
// แปลงที่ 1
const char* BOARD_ID = "greenhouse_1";

// แปลงที่ 2
const char* BOARD_ID = "greenhouse_2";

// แปลงที่ 3
const char* BOARD_ID = "greenhouse_3";
```

แต่ละแปลงควบคุม:
- Relay 1: ระบบน้ำ
- Relay 2: พัดลม
- Relay 3: ไฟ
- Sensor: อุณหภูมิและความชื้น

---

## 🔍 การทดสอบ

### ตรวจสอบ Topics บน MQTT Explorer

```
thaitechzone/
├── board_01/
│   ├── control/
│   │   ├── led
│   │   └── relay1-3
│   ├── state/
│   │   └── relay1-3
│   ├── status/
│   │   └── led
│   └── sensor/
│       └── data
│
├── board_02/
│   └── ... (เหมือนกับ board_01)
│
└── living_room/
    └── ... (เหมือนกับ board_01)
```

### ทดสอบการทำงาน

1. **ควบคุม LED แยกบอร์ด**
   - เปิด `?board_id=board_01` → กด ON LED
   - เปิด `?board_id=board_02` → LED ตัวที่ 2 ไม่เปลี่ยน ✓

2. **ข้อมูล Sensor แยกบอร์ด**
   - Board 1 ส่งข้อมูล → แสดงใน `?board_id=board_01` เท่านั้น
   - Board 2 ส่งข้อมูล → แสดงใน `?board_id=board_02` เท่านั้น

3. **Relay ทำงานอิสระ**
   - ควบคุม Relay 1 ของ board_01 → ไม่กระทบ board_02

---

## 🎯 สรุป

### สิ่งที่ได้ทำ ✓
1. เพิ่มฟิลด์ `board_id` ในทุก model
2. สร้าง migration และ apply สำเร็จ
3. อัปเดต MQTT Manager ให้รองรับหลายบอร์ด
4. อัปเดต Callbacks ให้แยก board_id จาก topics
5. อัปเดต Views ให้รองรับการเลือกบอร์ด
6. สร้างโค้ด ESP32 พร้อม Board ID
7. สร้างเอกสารครบถ้วน 3 ฉบับ

### วิธีใช้งาน
1. Upload โค้ด ESP32 พร้อมกำหนด Board ID ที่ไม่ซ้ำกัน
2. เข้า Dashboard ด้วย URL: `?board_id=your_board_id`
3. ควบคุมและติดตามแต่ละบอร์ดแยกอิสระ

### ข้อดี
- รองรับหลายบอร์ด ✓
- แยก topics ชัดเจน ✓
- Backward compatible ✓
- มีเอกสารครบถ้วน ✓
- พร้อมใช้งานจริง ✓

---

**📞 ติดต่อ:** thaitechzone@gmail.com  
**🔗 Repository:** [github.com/thaitechzone/DjangoDashboardFramework](https://github.com/thaitechzone/DjangoDashboardFramework)

**เวอร์ชัน:** 2.0  
**วันที่อัปเดต:** October 2025
