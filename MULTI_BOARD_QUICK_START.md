# 🚀 คู่มือเริ่มต้นใช้งานแบบหลายบอร์ด (Multi-Board Quick Start)

## 📋 สิ่งที่ต้องเตรียม

### อุปกรณ์
- ESP32 Development Board (2 ตัวขึ้นไป)
- สาย USB สำหรับเชื่อมต่อ ESP32
- DHT22 Sensor (ถ้าต้องการวัดอุณหภูมิและความชื้น)
- Relay Module 3 ช่อง (ถ้าต้องการควบคุมอุปกรณ์ไฟฟ้า)

### ซอฟต์แวร์
- Python 3.8+
- Arduino IDE
- Django IoT Dashboard (Clone จาก GitHub)

---

## 🎯 ขั้นตอนที่ 1: ติดตั้ง Dashboard

### 1.1 Clone Repository
```bash
git clone https://github.com/thaitechzone/DjangoDashboardFramework.git
cd DjangoDashboardFramework/django_iot_dashboard
```

### 1.2 สร้าง Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# หรือ
venv\Scripts\activate  # Windows
```

### 1.3 ติดตั้ง Dependencies
```bash
pip install django==5.2.7 paho-mqtt==2.1.0 pytz
```

### 1.4 รัน Migration
```bash
python manage.py makemigrations
python manage.py migrate
```

### 1.5 เริ่ม Server
```bash
python manage.py runserver
```

เปิดเบราว์เซอร์ไปที่: `http://localhost:8000/`

---

## 🔧 ขั้นตอนที่ 2: ตั้งค่า ESP32 ตัวที่ 1

### 2.1 เปิด Arduino IDE

### 2.2 สร้างไฟล์ใหม่และคัดลอกโค้ด
- ใช้ไฟล์ `ESP32_WITH_BOARD_ID.ino`

### 2.3 แก้ไขการตั้งค่า

```cpp
// กำหนด Board ID (ต้องไม่ซ้ำกัน)
const char* BOARD_ID = "board_01";

// กำหนด WiFi
const char* WIFI_SSID = "YOUR_WIFI_NAME";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
```

### 2.4 ตั้งค่า Pin (ตามการต่อฮาร์ดแวร์จริง)

```cpp
#define LED_PIN 2           // หลอด LED บนบอร์ด
#define DHT_PIN 15          // เซนเซอร์ DHT22
#define RELAY1_PIN 17       // รีเลย์ 1
#define RELAY2_PIN 16       // รีเลย์ 2
#define RELAY3_PIN 4        // รีเลย์ 3
```

### 2.5 Upload โค้ด
1. เชื่อมต่อ ESP32 เข้ากับคอมพิวเตอร์
2. เลือก Board: **Tools → Board → ESP32 Dev Module**
3. เลือก Port: **Tools → Port → COM** (Windows) หรือ **/dev/ttyUSB0** (Linux)
4. กดปุ่ม Upload

### 2.6 ตรวจสอบ Serial Monitor
- เปิด Serial Monitor (Baud rate: 115200)
- ควรเห็นข้อความ:
```
========================================
  ESP32 IoT Dashboard Controller v2.0
  with Board ID Support
========================================
Board ID: board_01

✅ WiFi connected successfully!
📶 IP Address: 192.168.1.xxx
✅ MQTT Connected!
```

---

## 🔧 ขั้นตอนที่ 3: ตั้งค่า ESP32 ตัวที่ 2

### 3.1 ทำซ้ำขั้นตอนที่ 2 แต่เปลี่ยน Board ID

```cpp
const char* BOARD_ID = "board_02";  // ต้องแตกต่างจากตัวแรก
```

### 3.2 Upload และตรวจสอบ

ดู Serial Monitor ต้องเห็นข้อความคล้ายกับตัวแรก แต่ Board ID เป็น "board_02"

---

## 🌐 ขั้นตอนที่ 4: ทดสอบบน Dashboard

### 4.1 เข้าถึง Board ตัวที่ 1
```
http://localhost:8000/?board_id=board_01
```

- ทดสอบปุ่มควบคุม LED
- ทดสอบปุ่มควบคุม Relay
- ดูข้อมูล Sensor

### 4.2 เข้าถึง Board ตัวที่ 2
```
http://localhost:8000/?board_id=board_02
```

- ควบคุมอุปกรณ์ของ board_02 แยกอิสระ
- ข้อมูลแสดงเฉพาะของ board_02

### 4.3 ทดสอบความเป็นอิสระ
- เปิดสองหน้าต่างพร้อมกัน:
  - หน้าต่างที่ 1: `?board_id=board_01`
  - หน้าต่างที่ 2: `?board_id=board_02`
- ควบคุม LED ของแต่ละบอร์ดแยกกัน
- สังเกตว่าไม่มีผลกระทบข้ามบอร์ด

---

## 📊 ตัวอย่างการใช้งานจริง

### Scenario 1: ควบคุม 2 ห้อง

**ESP32 Board 1 - ห้องนั่งเล่น**
```cpp
const char* BOARD_ID = "living_room";
```
- URL: `http://localhost:8000/?board_id=living_room`
- ควบคุม: ไฟห้องนั่งเล่น, พัดลม, เครื่องปรับอากาศ

**ESP32 Board 2 - ห้องนอน**
```cpp
const char* BOARD_ID = "bedroom";
```
- URL: `http://localhost:8000/?board_id=bedroom`
- ควบคุม: ไฟห้องนอน, พัดลม
- ติดตาม: อุณหภูมิ, ความชื้น

### Scenario 2: โรงเรือนอัจฉริยะ (3 แปลง)

**แปลงที่ 1**
```cpp
const char* BOARD_ID = "greenhouse_1";
```

**แปลงที่ 2**
```cpp
const char* BOARD_ID = "greenhouse_2";
```

**แปลงที่ 3**
```cpp
const char* BOARD_ID = "greenhouse_3";
```

จัดการแต่ละแปลงแยกกัน:
- ระบบน้ำ (Relay 1)
- พัดลม (Relay 2)
- ไฟ (Relay 3)
- ติดตามอุณหภูมิและความชื้น

---

## 🔍 การตรวจสอบและ Debug

### ตรวจสอบ Topics บน MQTT

ใช้ MQTT Explorer:
1. ดาวน์โหลด: [mqtt-explorer.com](http://mqtt-explorer.com/)
2. เชื่อมต่อไปที่: `broker.hivemq.com:1883`
3. ดู Topics:
```
thaitechzone/
├── board_01/
│   ├── control/
│   │   ├── led
│   │   ├── relay1
│   │   ├── relay2
│   │   └── relay3
│   ├── state/
│   │   ├── relay1
│   │   ├── relay2
│   │   └── relay3
│   ├── status/
│   │   └── led
│   └── sensor/
│       └── data
└── board_02/
    └── ... (เหมือนกับ board_01)
```

### ตรวจสอบฐานข้อมูล

```bash
python manage.py shell
```

```python
from iot_dashboard.models import Device, Relay, SensorData

# ดูบอร์ดทั้งหมด
print("Devices:", Device.objects.values_list('board_id', flat=True).distinct())
print("Relays:", Relay.objects.values_list('board_id', flat=True).distinct())

# ดูข้อมูลของ board_01
board1_sensors = SensorData.objects.filter(board_id='board_01').order_by('-timestamp')[:5]
for s in board1_sensors:
    print(f"{s.timestamp}: Temp={s.temperature}°C, Hum={s.humidity}%")
```

---

## 🐛 แก้ปัญหาที่พบบ่อย

### ปัญหา: ESP32 เชื่อมต่อ WiFi ไม่ได้

**วิธีแก้:**
1. ตรวจสอบ SSID และ Password
2. ตรวจสอบว่า WiFi เป็น 2.4GHz (ESP32 ไม่รองรับ 5GHz)
3. ตรวจสอบสัญญาณ WiFi

### ปัญหา: ESP32 เชื่อมต่อ MQTT ไม่ได้

**วิธีแก้:**
1. ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต
2. ตรวจสอบ firewall
3. ทดสอบด้วย MQTT Explorer

### ปัญหา: Dashboard ไม่แสดงข้อมูล

**วิธีแก้:**
1. ตรวจสอบ URL มี `board_id` ที่ถูกต้อง
2. ตรวจสอบ Django Server ทำงานอยู่
3. เปิด Browser Console ดู error

### ปัญหา: สองบอร์ดทำงานพร้อมกัน

**สาเหตุ:** Board ID ซ้ำกัน

**วิธีแก้:**
1. ตรวจสอบ `BOARD_ID` ในโค้ด ESP32 แต่ละตัว
2. ต้องไม่ซ้ำกัน
3. Upload ใหม่

---

## 📝 Checklist สำหรับแต่ละบอร์ด

ก่อน Deploy จริง ตรวจสอบ:

- [ ] `BOARD_ID` ไม่ซ้ำกันกับบอร์ดอื่น
- [ ] `WIFI_SSID` และ `WIFI_PASSWORD` ถูกต้อง
- [ ] Pin definitions ตรงกับฮาร์ดแวร์
- [ ] Serial Monitor แสดงการเชื่อมต่อสำเร็จ
- [ ] MQTT Topics ถูกต้อง
- [ ] Dashboard แสดงข้อมูลได้
- [ ] ควบคุมอุปกรณ์ได้ปกติ
- [ ] Sensor ส่งข้อมูลได้ปกติ

---

## 🎓 Tips สำหรับ Production

### 1. ตั้งชื่อ Board ID ให้มีความหมาย
```cpp
// ❌ ไม่ดี
const char* BOARD_ID = "b1";

// ✅ ดี
const char* BOARD_ID = "living_room_esp32";
```

### 2. เพิ่ม LED Status Indicator

```cpp
// กระพริบเมื่อกำลัง connect
void indicateConnecting() {
  digitalWrite(LED_PIN, !digitalRead(LED_PIN));
}

// ค้างเมื่อ connect สำเร็จ
void indicateConnected() {
  digitalWrite(LED_PIN, HIGH);
}
```

### 3. เก็บ Board ID ใน EEPROM

```cpp
#include <EEPROM.h>

void saveBoardID(String id) {
  EEPROM.begin(64);
  for(int i = 0; i < id.length(); i++) {
    EEPROM.write(i, id[i]);
  }
  EEPROM.write(id.length(), '\0');
  EEPROM.commit();
}

String loadBoardID() {
  EEPROM.begin(64);
  String id = "";
  char c;
  int i = 0;
  while((c = EEPROM.read(i++)) != '\0' && i < 64) {
    id += c;
  }
  return id;
}
```

### 4. เพิ่ม Watchdog Timer

```cpp
#include <esp_task_wdt.h>

void setup() {
  // Enable watchdog (60 seconds)
  esp_task_wdt_init(60, true);
  esp_task_wdt_add(NULL);
}

void loop() {
  // Reset watchdog
  esp_task_wdt_reset();
  
  // Your code here
}
```

---

## 🔗 ลิงก์ที่เป็นประโยชน์

- 📚 เอกสารเต็ม: [ESP32_BOARD_ID_GUIDE.md](ESP32_BOARD_ID_GUIDE.md)
- 💻 GitHub Repository: [github.com/thaitechzone/DjangoDashboardFramework](https://github.com/thaitechzone/DjangoDashboardFramework)
- 🎥 YouTube Tutorial: ThaiTechZone Channel
- 💬 Facebook Group: ThaiTechZone Community

---

## 📞 ติดต่อและสนับสนุน

- 📧 Email: thaitechzone@gmail.com
- 💬 Facebook: facebook.com/ThaiTechZone
- 🐛 GitHub Issues: [Report a Bug](https://github.com/thaitechzone/DjangoDashboardFramework/issues)

---

**สนุกกับการพัฒนา IoT! 🚀**

_Updated: October 2025_
