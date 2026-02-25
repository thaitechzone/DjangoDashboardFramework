# 🏠 Django IoT Dashboard — ESP32 + MQTT + AI

> ระบบ Dashboard สำหรับควบคุมและติดตาม IoT Device (ESP32) แบบ Real-time  
> พัฒนาด้วย Django + MQTT + Chart.js + Gemini AI

---

## 📋 สารบัญ

1. [ภาพรวมระบบ](#1-ภาพรวมระบบ)
2. [โครงสร้างโปรเจกต์](#2-โครงสร้างโปรเจกต์)
3. [ESP32 (Firmware)](#3-esp32-firmware)
4. [Backend (Django)](#4-backend-django)
5. [Frontend (Dashboard)](#5-frontend-dashboard)
6. [MQTT Topics](#6-mqtt-topics)
7. [รันโปรเจกต์บนเครื่องใหม่](#7-รันโปรเจกต์บนเครื่องใหม่)

---

## 1. ภาพรวมระบบ

ระบบนี้แบ่งออกเป็น 3 ส่วนหลักที่ทำงานร่วมกัน:

```
┌─────────────────┐        MQTT        ┌──────────────────┐       HTTP       ┌─────────────┐
│   ESP32 Board   │ ◄────────────────► │  Django Backend  │ ◄──────────────► │   Browser   │
│  (Firmware)     │  broker.hivemq.com │   (Port 8000)    │   Dashboard UI   │  (Frontend) │
└─────────────────┘                    └──────────────────┘                  └─────────────┘
     ส่ง Sensor                          รับ + บันทึก DB                       แสดงกราฟ
     รับคำสั่ง Relay                      REST API                             ควบคุม Relay
```

| ส่วน | เทคโนโลยี | หน้าที่ |
|------|-----------|---------|
| **ESP32** | Arduino / PlatformIO (C++) | อ่าน Sensor, ควบคุม Relay/LED, สื่อสารผ่าน MQTT |
| **Backend** | Django 5 + paho-mqtt | รับข้อมูล MQTT, บันทึก DB, ให้ REST API |
| **Frontend** | HTML + Chart.js + Vanilla JS | แสดงกราฟ, ควบคุม Device แบบ Real-time |

---

## 2. โครงสร้างโปรเจกต์

```
DjangoDashboardFramework/
├── ESP32_RELAY_CONTROL_FULL_CODE.ino   ← Firmware สำหรับ ESP32
├── mqtt_topic_id.md                    ← เอกสาร MQTT Topics
├── DashboardFramework.md               ← เอกสารโครงสร้างระบบ (ฉบับเต็ม)
├── VPS.md                              ← คู่มือ Deploy บน VPS
├── run_backend.bat                     ← Script รัน Backend (Windows)
└── django_iot_dashboard/               ← โปรเจกต์ Django หลัก
    ├── manage.py
    ├── db.sqlite3                      ← ฐานข้อมูล SQLite
    ├── requirements.txt                ← Python packages
    ├── dashboard_project/              ← Django Project Config
    │   ├── settings.py                 ← ตั้งค่าระบบ
    │   └── urls.py                     ← URL หลัก
    └── iot_dashboard/                  ← Django App หลัก
        ├── models.py                   ← โครงสร้าง Database
        ├── views_simple.py             ← Views + REST API ทั้งหมด
        ├── urls.py                     ← URL routing
        ├── mqtt_manager.py             ← MQTT Client (Singleton)
        ├── mqtt_callbacks.py           ← รับข้อมูลจาก ESP32
        ├── ai_agent/
        │   ├── gemini_agent.py         ← Gemini AI วิเคราะห์ Sensor
        │   └── scheduler.py            ← AI รันตามตาราง
        ├── templates/iot_dashboard/
        │   ├── dashboard_simple.html   ← หน้า Dashboard หลัก ✅
        │   └── ai_dashboard.html       ← หน้า AI Agent
        └── management/commands/
            ├── generate_sample_data.py ← สร้างข้อมูลทดสอบ
            └── mqtt_listener.py        ← รัน MQTT แยก process
```

---

## 3. ESP32 (Firmware)

**Repository ESP32:** [thaitechzone/ESP32TestDashbordDjango](https://github.com/thaitechzone/ESP32TestDashbordDjango)

### Hardware ที่รองรับ

| ส่วนประกอบ | GPIO | รายละเอียด |
|-----------|------|-----------|
| **MCU** | — | ESP32 |
| **Onboard LED** | GPIO 2 | Active High (HIGH = เปิด) |
| **DHT22 Sensor** | GPIO 15 | อ่าน Temperature & Humidity (ตอนนี้ใช้ random placeholder) |
| **Relay 1** | GPIO 17 | Active Low (LOW = เปิด, HIGH = ปิด) |
| **Relay 2** | GPIO 16 | Active Low |
| **Relay 3** | GPIO 4 | Active Low |
| **ปุ่ม SW1** | GPIO 34 | Toggle Relay 1 (External Pull-up 10kΩ) |
| **ปุ่ม SW2** | GPIO 35 | Toggle Relay 2 (External Pull-up 10kΩ) |
| **ปุ่ม SW3** | GPIO 32 | Toggle Relay 3 (Internal Pull-up) |
| **OLED Display** | GPIO 21 (SDA), GPIO 22 (SCL) | SSD1306 128×64, I2C (optional) |

### การต่อสาย

```
DHT22          ESP32
──────────────────────
VCC   →  3.3V
DATA  →  GPIO 15  (+ Resistor Pull-up 10kΩ ไป 3.3V)
GND   →  GND

Relay Module   ESP32
──────────────────────
VCC   →  5V
GND   →  GND
IN1   →  GPIO 17  (Relay 1)
IN2   →  GPIO 16  (Relay 2)
IN3   →  GPIO 4   (Relay 3)

OLED SSD1306   ESP32
──────────────────────
VCC   →  3.3V
GND   →  GND
SDA   →  GPIO 21
SCL   →  GPIO 22
```

### การตั้งค่า Firmware

เปิดไฟล์ `src/main.cpp` แล้วแก้ค่าตามนี้:

```cpp
// WiFi
const char* WIFI_SSID     = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// MQTT Broker (ใช้ HiveMQ Public ฟรี)
const char* MQTT_BROKER = "broker.hivemq.com";
const int   MQTT_PORT   = 1883;
const char* MQTT_CLIENT_ID = "ESP_ThaiTechZone_LED_Controller_01";
```

### การทำงานของ Firmware

- **เชื่อมต่อ WiFi** → เชื่อมต่อ MQTT Broker อัตโนมัติ
- **ส่งข้อมูล Sensor** ทุก 5 วินาที (Temperature, Humidity)
- **รับคำสั่ง** จาก Django เพื่อเปิด/ปิด LED และ Relay 1/2/3
- **ส่งสถานะ** กลับเมื่อมีการเปลี่ยนแปลง (retain=true)
- **ปุ่ม Physical** SW1/SW2/SW3 toggle Relay ได้โดยตรง (ไม่ต้องผ่าน Dashboard)
- **OLED Display** แสดงสถานะ WiFi, MQTT, Relay, Temperature/Humidity แบบ Real-time

> ⚠️ ตอนนี้ค่า Temperature/Humidity เป็น **random values** (placeholder)  
> แก้ได้ใน `readAndPublishSensorData()` โดย uncomment บรรทัดที่ใช้ `dht.readTemperature()`

---

## 4. Backend (Django)

### โครงสร้าง Database

| Model | หน้าที่ |
|-------|---------|
| `Device` | เก็บสถานะ Onboard LED (ON/OFF) |
| `Relay` | สถานะ Relay 1/2/3 |
| `SensorData` | ข้อมูล Temperature & Humidity ที่รับมาจาก ESP32 |
| `ThresholdSetting` | ค่า Threshold + โหมด AUTO/MANUAL |
| `AIDecisionLog` | บันทึกการตัดสินใจของ AI |
| `DeviceConfig` | ชื่อ Device, ที่อยู่ MQTT Broker (เปลี่ยนได้ใน Dashboard) |

### REST API Endpoints

#### หน้า Dashboard
| URL | คำอธิบาย |
|-----|---------|
| `/` | **หน้าหลัก Dashboard** |
| `/ai/` | หน้า AI Agent |
| `/admin/` | Django Admin |

#### API สำหรับ Frontend
| URL | Method | คำอธิบาย |
|-----|--------|---------|
| `/api/v1/led/` | GET/POST | อ่าน/ควบคุม LED |
| `/api/v1/relay/` | GET/POST | อ่าน/ควบคุม Relay |
| `/api/v1/sensors/latest/` | GET | ค่า Sensor ล่าสุด |
| `/api/v1/sensors/ds18b20/` | GET | ค่า DS18B20 ล่าสุด |
| `/api/v1/threshold/` | GET/POST | ตั้งค่า Threshold |
| `/api/v1/device-config/` | GET/POST | ตั้งค่า Device + Reload MQTT |
| `/api/v1/system/status/` | GET | สถานะระบบรวม (MQTT + DB + AI) |

### MQTT Manager

Backend ใช้ `MQTTManager` (Singleton) ที่เริ่มทำงานอัตโนมัติเมื่อ `runserver`:

```
runserver → apps.py → MQTTManager เชื่อมต่อ broker.hivemq.com → Subscribe topics → พร้อมรับข้อมูล
```

> ✅ เมื่อเปลี่ยน `device_name` ใน Dashboard → ระบบจะ Unsubscribe topics เดิม แล้ว Subscribe topics ใหม่โดยอัตโนมัติ ไม่ต้อง restart

---

## 5. Frontend (Dashboard)

**ไฟล์:** `dashboard_simple.html`

### Layout ของหน้า Dashboard

```
┌──────────────────────────────────────────────┐
│  IoT Dashboard — ชื่อระบบ + เวลาปัจจุบัน   │
├──────────────┬──────────────┬────────────────┤
│ 🌡️ Temp      │ 💧 Humidity  │  🌡️ DS18B20   │
│  XY-MD03     │  XY-MD03     │  Real Sensor   │
├──────────────┴──────────────┴────────────────┤
│  💡 Onboard LED — ปุ่ม ON / OFF             │
├──────────────────────────────────────────────┤
│  🔌 Relay 1 / 2 / 3 — ปุ่ม ON/OFF + AUTO   │
├──────────────────────────────────────────────┤
│  🤖 AI Agent + ตั้งค่า Threshold            │
├──────────────────────────────────────────────┤
│  📈 กราฟ Temperature & Humidity (Chart.js)  │
├────────────────────┬─────────────────────────┤
│  📋 ข้อมูลล่าสุด   │  📟 ตั้งค่า Device      │
│  (10 รายการ)       │  + MQTT Topics ที่ใช้   │
└────────────────────┴─────────────────────────┘
```

### การอัปเดตข้อมูลอัตโนมัติ (Polling)

| ข้อมูล | ความถี่ | API |
|--------|---------|-----|
| Temperature & Humidity | ทุก 5 วินาที | `/api/sensor-data/` |
| DS18B20 | ทุก 5 วินาที | `/api/v1/sensors/ds18b20/` |
| Threshold | ทุก 10 วินาที | `/api/v1/threshold/` |
| เวลาปัจจุบัน | ทุก 1 วินาที | (JavaScript local) |

> Frontend ใช้ **Vanilla JS** พร้อม `fetch()` เพื่อ poll API ไม่ต้องใช้ Library เพิ่มเติม

---

## 6. MQTT Topics

### รูปแบบ Topic

```
thaitechzone/v2_board/<direction>/<property>
```

- `direction` = `control` (Django ส่งคำสั่ง → ESP32 รับ)
- `direction` = `state` หรือ `sensor` (ESP32 ส่งสถานะ/ข้อมูล → Django รับ)

> 📌 Topic ในโปรเจกต์นี้ **ไม่มี Device ID** ใน path — ใช้ `v2_board` คงที่

### Topics ทั้งหมด

#### 💡 LED

| Topic | ทิศทาง | Payload |
|-------|--------|---------|
| `thaitechzone/v2_board/control/led` | Django **ส่ง** → ESP32 รับ | `ON` หรือ `OFF` |
| `thaitechzone/v2_board/state/led` | ESP32 **ส่ง** → Django รับ | `ON` หรือ `OFF` (retain=true) |

#### 🔌 Relay

| Topic | ทิศทาง | Payload |
|-------|--------|---------|
| `thaitechzone/v2_board/control/relay1` | Django → ESP32 | `ON` / `OFF` |
| `thaitechzone/v2_board/control/relay2` | Django → ESP32 | `ON` / `OFF` |
| `thaitechzone/v2_board/control/relay3` | Django → ESP32 | `ON` / `OFF` |
| `thaitechzone/v2_board/state/relay1` | ESP32 → Django | `ON` / `OFF` (retain=true) |
| `thaitechzone/v2_board/state/relay2` | ESP32 → Django | `ON` / `OFF` (retain=true) |
| `thaitechzone/v2_board/state/relay3` | ESP32 → Django | `ON` / `OFF` (retain=true) |

> ⚙️ Relay เป็น **Active Low** (LOW = เปิด, HIGH = ปิด) แต่ Firmware แปลง `ON`/`OFF` ให้อัตโนมัติ  
> ปุ่ม Physical SW1/SW2/SW3 ก็ toggle Relay และส่งสถานะกลับ MQTT ด้วย

#### 🌡️ Sensor (DHT22)

| Topic | ทิศทาง | Payload | หมายเหตุ |
|-------|--------|---------|----------|
| `thaitechzone/v2_board/sensor/temperature` | ESP32 → Django | `"27.5"` (°C) | Random placeholder |
| `thaitechzone/v2_board/sensor/humidity` | ESP32 → Django | `"65.3"` (%) | Random placeholder |
| `thaitechzone/v2_board/sensor/data` | ESP32 → Django | JSON (ดูด้านล่าง) | ส่งทุก 5 วินาที |

```json
// Payload ของ sensor/data
{
  "temperature": 27.5,
  "humidity": 65.3,
  "device_name": "ESP_01"
}
```

> ⚠️ ค่า `temperature` และ `humidity` ยังเป็น **random values**  
> แก้ได้ใน `readAndPublishSensorData()` ใน `src/main.cpp`

### MQTT Broker
- **Broker:** `broker.hivemq.com`
- **Port:** `1883` (TCP)
- **ประเภท:** Public Broker (ฟรี ไม่ต้องสมัคร)

---

## 7. รันโปรเจกต์บนเครื่องใหม่

### สิ่งที่ต้องมี
- Python 3.10 ขึ้นไป
- Git
- อินเทอร์เน็ต (สำหรับ MQTT Broker + ดึง packages)

---

### ขั้นตอนที่ 1 — Clone โปรเจกต์

```bash
git clone https://github.com/thaitechzone/DjangoDashboardFramework.git
cd DjangoDashboardFramework
```

---

### ขั้นตอนที่ 2 — สร้าง Virtual Environment

```bash
# สร้าง venv
python -m venv venv

# เปิดใช้งาน (Windows)
venv\Scripts\activate

# เปิดใช้งาน (Mac/Linux)
source venv/bin/activate
```

---

### ขั้นตอนที่ 3 — ติดตั้ง Dependencies

```bash
cd django_iot_dashboard
pip install -r requirements.txt
```

packages หลักที่จะติดตั้ง:

| Package | ใช้ทำอะไร |
|---------|-----------|
| `Django` | Web Framework หลัก |
| `paho-mqtt` | MQTT Client |
| `pytz` | จัดการ Timezone (Asia/Bangkok) |
| `google-genai` | Gemini AI Agent |
| `apscheduler` | Scheduler สำหรับ AI |
| `requests` | HTTP Client |

---

### ขั้นตอนที่ 4 — Setup Database

```bash
# รัน Migration (สร้างตาราง DB)
python manage.py migrate

# (ไม่บังคับ) สร้างข้อมูลทดสอบ
python manage.py generate_sample_data
```

---

### ขั้นตอนที่ 5 — รัน Server

```bash
python manage.py runserver
```

เปิด Browser: **http://localhost:8000/**

> ✅ ระบบจะเชื่อมต่อ MQTT Broker อัตโนมัติเมื่อ `runserver` ทำงาน

---

### ขั้นตอนที่ 6 — (ไม่บังคับ) ตั้งค่า AI Agent

หากต้องการใช้ฟีเจอร์ Gemini AI ให้สร้างไฟล์ `.env` ใน `django_iot_dashboard/`:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

> สมัครรับ API Key ฟรีได้ที่ [aistudio.google.com](https://aistudio.google.com)

---

### ขั้นตอนที่ 7 — (ไม่บังคับ) สร้าง Admin Account

```bash
python manage.py createsuperuser
```

เข้าใช้ที่: **http://localhost:8000/admin/**

---

### สรุปคำสั่งทั้งหมด (One-liner)

```bash
git clone https://github.com/thaitechzone/DjangoDashboardFramework.git
cd DjangoDashboardFramework
python -m venv venv && venv\Scripts\activate
cd django_iot_dashboard
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

### ปัญหาที่พบบ่อย

| ปัญหา | วิธีแก้ |
|-------|---------|
| `ModuleNotFoundError: No module named 'django'` | ลืมเปิด venv — รัน `venv\Scripts\activate` ก่อน |
| Dashboard แสดงข้อมูลแต่ไม่อัปเดต | ตรวจสอบว่า ESP32 เชื่อมต่อ WiFi และ MQTT ได้ |
| MQTT ไม่ Connected | ตรวจสอบ Internet — ใช้ Public Broker `broker.hivemq.com` |
| ข้อมูล Sensor เป็น 0 ทั้งหมด | รัน `python manage.py generate_sample_data` เพื่อสร้างข้อมูลจำลอง |
| Port 8000 ถูกใช้งานอยู่ | รัน `python manage.py runserver 8001` เพื่อเปลี่ยน Port |

---

## 📄 License

MIT License — ใช้ฟรี แก้ไขได้ เผยแพร่ได้ โดยระบุเครดิต

---

> **ThaiTechZone** — IoT Dashboard Framework

| Repository | Link |
|-----------|------|
| **Django Backend** | [thaitechzone/DjangoDashboardFramework](https://github.com/thaitechzone/DjangoDashboardFramework) |
| **ESP32 Firmware** | [thaitechzone/ESP32TestDashbordDjango](https://github.com/thaitechzone/ESP32TestDashbordDjango) |
