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
| **ESP32** | Arduino (C++) | อ่าน Sensor, ควบคุม Relay/LED, สื่อสารผ่าน MQTT |
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

**ไฟล์:** `ESP32_RELAY_CONTROL_FULL_CODE.ino`

### Hardware ที่รองรับ

| ส่วนประกอบ | รายละเอียด |
|-----------|-----------|
| **MCU** | ESP32 |
| **Sensor 1** | XY-MD03 — อ่าน Temperature & Humidity (placeholder/random) |
| **Sensor 2** | DS18B20 — อ่าน Temperature จริง (GPIO 13, 1-Wire) |
| **Output** | Onboard LED (ควบคุมผ่าน MQTT) |
| **Output** | Relay 1, 2, 3 (Active Low) |
| **Input** | Digital Input แบบ Isolated 2 ช่อง (DI1, DI2) |

### การตั้งค่า Firmware

เปิดไฟล์ `.ino` แล้วแก้ค่าตามนี้:

```cpp
// ชื่อ Device (ต้องตรงกับที่ตั้งใน Django Dashboard)
#define DEVICE_NAME "ttz_board_001"

// WiFi
const char* ssid     = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// MQTT Broker (ใช้ HiveMQ Public ฟรี)
const char* mqtt_server = "broker.hivemq.com";
const int   mqtt_port   = 1883;
```

> ⚠️ **หากมีหลายบอร์ด** ให้เปลี่ยน `DEVICE_NAME` ก่อน Flash แต่ละบอร์ด
> ```
> ttz_board_001  →  Board 1
> ttz_board_002  →  Board 2
> ```

### การทำงานของ Firmware

- **เชื่อมต่อ WiFi** → เชื่อมต่อ MQTT Broker
- **ส่งข้อมูล Sensor** ทุก 5 วินาที (Temperature, Humidity, DS18B20)
- **รับคำสั่ง** จาก Django เพื่อเปิด/ปิด LED และ Relay
- **ส่งสถานะ** กลับมาเพื่อให้ Dashboard แสดงผลถูกต้อง

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
thaitechzone/v2/<DEVICE_ID>/<direction>/<property>
```

- `DEVICE_ID` = ชื่อบอร์ด เช่น `ttz_board_001`
- `direction` = `control` (Django → ESP32) หรือ `state`/`sensor` (ESP32 → Django)

### Topics ทั้งหมด

#### 💡 LED

| Topic | ทิศทาง | Payload |
|-------|--------|---------|
| `thaitechzone/v2/ttz_board_001/control/led` | Django **ส่ง** → ESP32 รับ | `ON` หรือ `OFF` |
| `thaitechzone/v2/ttz_board_001/state/led` | ESP32 **ส่ง** → Django รับ | `ON` หรือ `OFF` |

#### 🔌 Relay

| Topic | ทิศทาง | Payload |
|-------|--------|---------|
| `thaitechzone/v2/ttz_board_001/control/relay1` | Django → ESP32 | `ON` / `OFF` |
| `thaitechzone/v2/ttz_board_001/control/relay2` | Django → ESP32 | `ON` / `OFF` |
| `thaitechzone/v2/ttz_board_001/control/relay3` | Django → ESP32 | `ON` / `OFF` |
| `thaitechzone/v2/ttz_board_001/state/relay1` | ESP32 → Django | `ON` / `OFF` |
| `thaitechzone/v2/ttz_board_001/state/relay2` | ESP32 → Django | `ON` / `OFF` |
| `thaitechzone/v2/ttz_board_001/state/relay3` | ESP32 → Django | `ON` / `OFF` |

> ⚙️ Relay บนบอร์ดเป็น **Active Low** (LOW = เปิด, HIGH = ปิด) แต่ Firmware แปลง `ON`/`OFF` ให้อัตโนมัติ

#### 🌡️ Sensor

| Topic | ทิศทาง | Payload | หมายเหตุ |
|-------|--------|---------|----------|
| `thaitechzone/v2/ttz_board_001/sensor/temperature` | ESP32 → Django | `"27.5"` (°C) | Random placeholder |
| `thaitechzone/v2/ttz_board_001/sensor/humidity` | ESP32 → Django | `"65.3"` (%) | Random placeholder |
| `thaitechzone/v2/ttz_board_001/sensor/data` | ESP32 → Django | JSON (ดูด้านล่าง) | ส่งทุก 5 วินาที |
| `thaitechzone/v2/ttz_board_001/sensor/ds18b20` | ESP32 → Django | `"27.5"` (°C) | ค่าจริงจาก DS18B20 |

```json
// Payload ของ sensor/data
{
  "temperature": 27.5,
  "humidity": 65.3,
  "device_name": "ttz_board_001"
}
```

#### 📥 Digital Input (DI)

| Topic | ทิศทาง | Payload |
|-------|--------|---------|
| `thaitechzone/v2/ttz_board_001/state/isolate_in1` | ESP32 → Django | `ON` / `OFF` |
| `thaitechzone/v2/ttz_board_001/state/isolate_in2` | ESP32 → Django | `ON` / `OFF` |

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
> GitHub: [thaitechzone/DjangoDashboardFramework](https://github.com/thaitechzone/DjangoDashboardFramework)
