# 📘 DashboardFramework — เอกสารโครงสร้างระบบ

> **โปรเจกต์:** IoT Dashboard สำหรับ ESP32 + Django  
> **Branch ปัจจุบัน:** `Step10_Edit_Topic_MQTT_IDBOARD`  
> **อัปเดตล่าสุด:** 2026-02-23

---

## 🗂️ โครงสร้างไฟล์ทั้งหมด

```
DjangoDashboardFramework/
├── ESP32_RELAY_CONTROL_FULL_CODE.ino   ← Firmware ESP32
├── mqtt_topic_id.md                    ← เอกสาร MQTT Topics อ้างอิง
├── DashboardFramework.md               ← ไฟล์นี้
└── django_iot_dashboard/               ← ตัวโปรเจกต์ Django
    ├── manage.py                       ← Django CLI
    ├── db.sqlite3                      ← Database (SQLite)
    ├── requirements.txt                ← Python dependencies
    ├── dashboard_project/              ← Project Config
    │   ├── settings.py                 ← ตั้งค่า Django, Database, Apps
    │   ├── urls.py                     ← URL root (include iot_dashboard.urls)
    │   ├── wsgi.py / asgi.py           ← Entry point สำหรับ deploy
    └── iot_dashboard/                  ← แอปหลัก
        ├── models.py                   ← Database Models
        ├── views.py                    ← Views ชุดเก่า (complex)
        ├── views_simple.py             ← Views หลัก + API Endpoints ทั้งหมด
        ├── urls.py                     ← URL routing ทั้งหมดของแอป
        ├── mqtt_manager.py             ← MQTT Client (Singleton)
        ├── mqtt_callbacks.py           ← ฟังก์ชันรับข้อมูลจาก ESP32
        ├── admin.py                    ← Django Admin
        ├── apps.py                     ← App config (เริ่ม MQTT ตอน startup)
        ├── ai_agent/
        │   ├── gemini_agent.py         ← Gemini AI วิเคราะห์ข้อมูล sensor
        │   ├── scheduler.py            ← Scheduled tasks (AI รันอัตโนมัติ)
        │   └── weather_service.py      ← ดึงข้อมูลสภาพอากาศ (ถ้ามี)
        ├── management/commands/
        │   ├── mqtt_listener.py        ← Command: python manage.py mqtt_listener
        │   ├── generate_sample_data.py ← Command: สร้างข้อมูลทดสอบ
        │   └── generate_fresh_data.py
        ├── migrations/                 ← Database migrations
        │   ├── 0001–0007_...           ← Migrations เดิม
        │   ├── 0008_deviceconfig.py    ← เพิ่ม DeviceConfig model
        │   └── 0009_deviceconfig_ds18b20.py ← เพิ่ม DS18B20 fields
        ├── static/iot_dashboard/
        │   └── dashboard.css           ← CSS เพิ่มเติม (static file)
        ├── templates/iot_dashboard/
        │   ├── dashboard_simple.html   ← หน้าหลัก Dashboard (ใช้งานจริง)
        │   ├── dashboard.html          ← Dashboard ชุดเก่า
        │   └── ai_dashboard.html       ← หน้า AI Agent
        └── templatetags/
            └── timezone_filters.py     ← Custom template filter แปลง timezone
```

---

## 🏗️ สถาปัตยกรรมระบบ (Architecture)

```
┌─────────────────────────────────────────────────────────┐
│                      ESP32 Board                         │
│  Firmware: ESP32_RELAY_CONTROL_FULL_CODE.ino             │
│  Sensors: XY-MD03 (Temp/Hum), DS18B20 (Temp)            │
│  Outputs: Onboard LED, Relay 1/2/3                       │
└─────────────────────┬───────────────────────────────────┘
                      │ MQTT Publish/Subscribe
                      │ broker.hivemq.com:1883
                      │
┌─────────────────────▼───────────────────────────────────┐
│              Django Backend (Port 8000)                  │
│                                                          │
│  ┌──────────────────┐    ┌─────────────────────────┐    │
│  │  MQTTManager     │    │  Django Views / API      │    │
│  │  (Singleton)     │    │  views_simple.py         │    │
│  │  mqtt_manager.py │    │                          │    │
│  └────────┬─────────┘    └──────────────┬──────────┘    │
│           │                             │                │
│  ┌────────▼─────────┐    ┌──────────────▼──────────┐    │
│  │  mqtt_callbacks  │    │  SQLite Database          │    │
│  │  รับข้อมูล ESP32 │◄──►│  db.sqlite3              │    │
│  └──────────────────┘    └─────────────────────────┘    │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  AI Agent (Gemini)  │  Scheduler                 │   │
│  │  gemini_agent.py    │  scheduler.py              │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP / Django Template
                      │
┌─────────────────────▼───────────────────────────────────┐
│              Browser (Frontend)                          │
│  dashboard_simple.html                                   │
│  - Chart.js (กราฟ Temperature & Humidity)               │
│  - Vanilla JS (poll API ทุก 5 วินาที)                   │
│  - CSS Gradient, Responsive Grid                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🗄️ Database Models (`models.py`)

| Model | ตาราง DB | คำอธิบาย |
|---|---|---|
| `Device` | `iot_dashboard_device` | เก็บสถานะ Onboard LED (ON/OFF) |
| `Relay` | `iot_dashboard_relay` | สถานะ Relay 1/2/3 (ON/OFF) |
| `SensorData` | `iot_dashboard_sensordata` | ข้อมูล Temperature & Humidity จาก XY-MD03 |
| `ThresholdSetting` | `iot_dashboard_thresholdsetting` | ค่า Threshold และโหมด AUTO/MANUAL |
| `AIDecisionLog` | `iot_dashboard_aidecisionlog` | บันทึกการตัดสินใจของ AI Agent |
| `DeviceConfig` | `iot_dashboard_deviceconfig` | ตั้งค่า Device Identity (Singleton) |

### DeviceConfig (Singleton)
```python
device_name          = "ttz_board_001"       # ตรงกับ DEVICE_NAME ใน Firmware
mqtt_broker          = "broker.hivemq.com"
mqtt_port            = 1883
mqtt_client_id_prefix = "ThaiTechZone"
ds18b20_temperature  = FloatField (nullable) # ค่าล่าสุดจาก DS18B20
ds18b20_updated_at   = DateTimeField         # เวลาอัปเดตล่าสุด
```

---

## 🔌 MQTT Topics (`mqtt_manager.py` + `mqtt_callbacks.py`)

### Pattern
```
thaitechzone/v2/<DEVICE_ID>/<direction>/<property>
```
> `DEVICE_ID` = ค่าจาก `DeviceConfig.device_name` (เปลี่ยนได้แบบ Dynamic)

### Topics ทั้งหมด

| Topic | ทิศทาง | Payload | ฟังก์ชัน Callback |
|---|---|---|---|
| `thaitechzone/v2/{id}/control/led` | ▶ SUB (ESP32 รับ) | `ON` / `OFF` | `send_led_command()` |
| `thaitechzone/v2/{id}/state/led` | ◀ PUB (ESP32 ส่ง) | `ON` / `OFF` | `handle_led_message()` |
| `thaitechzone/v2/{id}/control/relay1` | ▶ SUB | `ON` / `OFF` | `send_relay_command()` |
| `thaitechzone/v2/{id}/control/relay2` | ▶ SUB | `ON` / `OFF` | `send_relay_command()` |
| `thaitechzone/v2/{id}/control/relay3` | ▶ SUB | `ON` / `OFF` | `send_relay_command()` |
| `thaitechzone/v2/{id}/state/relay1` | ◀ PUB | `ON` / `OFF` | `handle_relay_message()` |
| `thaitechzone/v2/{id}/state/relay2` | ◀ PUB | `ON` / `OFF` | `handle_relay_message()` |
| `thaitechzone/v2/{id}/state/relay3` | ◀ PUB | `ON` / `OFF` | `handle_relay_message()` |
| `thaitechzone/v2/{id}/sensor/data` | ◀ PUB | `{"temperature":27.5,"humidity":65.3}` | `handle_sensor_message()` |
| `thaitechzone/v2/{id}/sensor/temperature` | ◀ PUB | `"27.5"` (string) | `handle_sensor_message()` |
| `thaitechzone/v2/{id}/sensor/humidity` | ◀ PUB | `"65.3"` (string) | `handle_sensor_message()` |
| `thaitechzone/v2/{id}/sensor/ds18b20` | ◀ PUB | `"27.5"` (string, retain=true) | `handle_ds18b20_message()` |

> **▶ SUB** = Django **ส่ง** → ESP32 รับคำสั่ง  
> **◀ PUB** = ESP32 **ส่ง** → Django รับและบันทึก DB

### Data Flow — การรับข้อมูล Sensor

```
ESP32 Publish  →  MQTT Broker  →  MQTTManager.on_message()
     →  mqtt_callbacks.py (parse + validate)
     →  SensorData.objects.create()  ← บันทึก DB
     →  Browser poll /api/sensor-data/ ทุก 5s  ← แสดงผล
```

---

## 🌐 URL & API Endpoints (`urls.py`)

### หน้า Dashboard (Page Routes)

| URL | View | คำอธิบาย |
|---|---|---|
| `/` | `dashboard_simple` | **หน้าหลัก Dashboard** |
| `/ai/` | `ai_dashboard` | หน้า AI Agent Dashboard |
| `/complex/` | `views.dashboard_view` | Dashboard ชุดเก่า (สำรอง) |

---

### API เดิม (Legacy)

| URL | Method | คำอธิบาย |
|---|---|---|
| `/api/control-led/` | POST | ควบคุม LED (แบบ form) |
| `/api/control-relay/` | POST | ควบคุม Relay (แบบ form) |
| `/api/sensor-data/` | GET | ข้อมูล sensor ล่าสุด + chart |
| `/api/chart-data/` | GET | ข้อมูลสำหรับกราฟ |
| `/api/mqtt-status/` | GET | สถานะการเชื่อมต่อ MQTT |

---

### REST API v1 (หลัก)

#### 💡 LED
| URL | Method | Body/Params | Response |
|---|---|---|---|
| `/api/v1/led/` | GET | — | `{status, is_on, last_updated}` |
| `/api/v1/led/` | POST | `{"action": "ON"\|"OFF"}` | `{success, message}` |

#### 🔌 Relay
| URL | Method | Body/Params | Response |
|---|---|---|---|
| `/api/v1/relay/` | GET | — | `{relay1, relay2, relay3, last_updated}` |
| `/api/v1/relay/` | POST | `{"relay": 1, "action": "ON"\|"OFF"}` | `{success, message}` |

#### 🌡️ Sensor Data
| URL | Method | คำอธิบาย |
|---|---|---|
| `/api/v1/sensors/` | GET | รายการ sensor ทั้งหมด (paginated) |
| `/api/v1/sensors/latest/` | GET | ค่า sensor ล่าสุด |
| `/api/v1/sensors/stats/` | GET | สถิติ avg/min/max |
| `/api/v1/sensors/<id>/` | GET | รายละเอียด sensor ตาม ID |
| `/api/v1/sensors/ds18b20/` | GET | ค่า DS18B20 ล่าสุด จาก `DeviceConfig` |

#### ⚙️ Threshold
| URL | Method | คำอธิบาย |
|---|---|---|
| `/api/v1/threshold/` | GET/POST | อ่าน/บันทึกค่า Threshold + โหมด AUTO/MANUAL |
| `/api/v1/threshold/check/` | GET | ตรวจสอบว่าเกิน Threshold หรือไม่ |
| `/api/v1/threshold/reset/` | POST | Reset alarm |

#### 🤖 AI Agent
| URL | Method | คำอธิบาย |
|---|---|---|
| `/api/v1/ai/status/` | GET | สถานะ AI Agent |
| `/api/v1/ai/decisions/` | GET | ประวัติการตัดสินใจ |
| `/api/v1/ai/analyze-now/` | POST | สั่ง AI วิเคราะห์ทันที |
| `/api/v1/ai/stats/` | GET | สถิติการทำงานของ AI |

#### 📟 Device Config
| URL | Method | Body | คำอธิบาย |
|---|---|---|---|
| `/api/v1/device-config/` | GET | — | อ่านค่า DeviceConfig ปัจจุบัน |
| `/api/v1/device-config/` | POST | `{"device_name": "ttz_board_001", ...}` | บันทึกและ Reload MQTT Topics |

#### 🔎 System
| URL | Method | คำอธิบาย |
|---|---|---|
| `/api/v1/system/status/` | GET | สถานะรวม MQTT + DB + AI |

---

## 🖥️ Frontend (`dashboard_simple.html`)

### Layout ลำดับจากบนลงล่าง

```
┌─────────────────────────────────────────────┐
│  Header — ชื่อระบบ + เวลาปัจจุบัน           │
├──────────────┬──────────────┬───────────────┤
│  🌡️ Temp     │  💧 Humidity │  🌡️ DS18B20   │
│  XY-MD03     │  XY-MD03     │  Real Sensor  │
├──────────────┴──────────────┴───────────────┤
│  💡 Onboard LED (ON/OFF)                    │
├─────────────────────────────────────────────┤
│  🔌 Relay Control (1/2/3 + AUTO/MANUAL)    │
├─────────────────────────────────────────────┤
│  🤖 AI Agent + Threshold Settings           │
├─────────────────────────────────────────────┤
│  📈💧 Temperature & Humidity Chart          │
│     (Dual Y-axis, Gradient, Auto/Fixed)     │
├──────────────────┬──────────────────────────┤
│  📋 Recent       │  📟 Device Identity      │
│  Readings        │  Configuration            │
│  (Last 10)       │  + Active MQTT Topics    │
└──────────────────┴──────────────────────────┘
```

### JavaScript Polling

| ฟังก์ชัน | Interval | API ที่เรียก |
|---|---|---|
| `loadSensorData()` | ทุก 5 วินาที | `/api/sensor-data/` |
| `loadDS18B20()` | ทุก 5 วินาที | `/api/v1/sensors/ds18b20/` |
| `loadThresholdSettings()` | ทุก 10 วินาที | `/api/v1/threshold/` |
| `updateTime()` | ทุก 1 วินาที | (local JS) |

### Libraries ที่ใช้ใน Frontend

| Library | Version | ใช้ทำอะไร |
|---|---|---|
| **Chart.js** | CDN | กราฟ Temperature & Humidity (dual axis + gradient) |
| **Vanilla JS** | — | Fetch API, DOM manipulation, polling |
| **CSS Grid/Flexbox** | — | Layout responsive |

---

## ⚙️ การเริ่มต้นระบบ (Startup Flow)

```
python manage.py runserver
        │
        ▼
apps.py → AppConfig.ready()
        │
        ▼
MQTTManager.__init__()
        │
        ├── _load_topics_from_config()  ← โหลด DeviceConfig จาก DB
        ├── connect(broker.hivemq.com)
        ├── _subscribe_to_topics()      ← Subscribe 8 topics
        └── register_mqtt_callbacks()   ← ลงทะเบียน callback แต่ละ topic
```

---

## 🔄 Device Identity — Dynamic Topics

เมื่อ User กด **Save & Apply** ใน Dashboard:

```
Browser POST /api/v1/device-config/
        │  {"device_name": "ttz_board_002"}
        ▼
api_device_config() → DeviceConfig.save()
        │
        ▼
reload_mqtt_topics()
        │
        ├── Unsubscribe topics เดิม (ttz_board_001/...)
        ├── _load_topics_from_config()  ← โหลด device_name ใหม่
        ├── Subscribe topics ใหม่ (ttz_board_002/...)
        └── _reregister_callbacks()     ← ลงทะเบียน callbacks ใหม่
```

> ✅ ไม่ต้อง restart server เมื่อเปลี่ยน `device_name`

---

## 🗃️ Migrations ลำดับ

| Migration | สิ่งที่เพิ่ม |
|---|---|
| `0001_initial` | `Device` model |
| `0002` | `created_at`, `last_updated` |
| `0003_sensordata` | `SensorData` model |
| `0004_relay` | `Relay` model |
| `0005_thresholdsetting` | `ThresholdSetting` model |
| `0006_aidecisionlog` | `AIDecisionLog` model |
| `0007` | แก้ไข fields `AIDecisionLog` |
| `0008_deviceconfig` | `DeviceConfig` Singleton model |
| `0009_deviceconfig_ds18b20` | เพิ่ม `ds18b20_temperature`, `ds18b20_updated_at` |

---

## 🚀 คำสั่งที่ใช้บ่อย

```bash
# เริ่ม Development Server
cd django_iot_dashboard
python manage.py runserver

# Run Migrations
python manage.py migrate

# สร้างข้อมูลทดสอบ
python manage.py generate_sample_data

# รัน MQTT Listener แยก process
python manage.py mqtt_listener

# Django Admin
python manage.py createsuperuser
# เข้าที่ http://localhost:8000/admin/
```

---

## 📦 Dependencies หลัก (`requirements.txt`)

| Package | ใช้ทำอะไร |
|---|---|
| `django` | Web Framework หลัก |
| `paho-mqtt` | MQTT Client |
| `pytz` | Timezone conversion (Asia/Bangkok) |
| `google-generativeai` | Gemini AI Agent |
| `requests` | HTTP client (weather service) |
