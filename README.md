# 🏠 IoTs Dashboard Monitoring - Django Framework

**ระบบควบคุมและติดตามอุปกรณ์ IoT ผ่านเว็บ Dashboard แบบ Real-time**  
**Django + ESP32 + MQTT + Chart.js**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.2.7-green.svg)](https://djangoproject.com)
[![ESP32](https://img.shields.io/badge/ESP32-Arduino-red.svg)](https://arduino.cc)
[![MQTT](https://img.shields.io/badge/MQTT-HiveMQ-orange.svg)](https://mqtt.org)
[![Chart.js](https://img.shields.io/badge/Chart.js-4.4.0-ff6384.svg)](https://www.chartjs.org/)

---

## 📋 สารบัญ

1. [ภาพรวมโปรเจกต์](#-ภาพรวมโปรเจกต์)
2. [ความสามารถของระบบ](#-ความสามารถของระบบ)
3. [สถาปัตยกรรมระบบ](#️-สถาปัตยกรรมระบบ)
4. [ความต้องการของระบบ](#-ความต้องการของระบบ)
5. [ขั้นตอนการติดตั้งระบบ](#-ขั้นตอนการติดตั้งระบบ)
6. [การตั้งค่าฐานข้อมูล](#️-การตั้งค่าฐานข้อมูล)
7. [การรันเซิร์ฟเวอร์](#️-การรันเซิร์ฟเวอร์)
8. [การโปรแกรม ESP32](#-การโปรแกรม-esp32)
9. [MQTT Topics และการสื่อสาร](#-mqtt-topics-และการสื่อสาร)
10. [การทดสอบระบบ](#-การทดสอบระบบ)
11. [การแก้ไขปัญหา](#️-การแก้ไขปัญหาที่พบบ่อย)
12. [การพัฒนาต่อยอด](#-การพัฒนาต่อยอด)
13. [เอกสารอ้างอิง](#-เอกสารอ้างอิง)

---

## 🎯 ภาพรวมโปรเจกต์

โปรเจกต์นี้เป็น **IoT Dashboard Framework ที่สมบูรณ์** สำหรับสร้างระบบควบคุมและติดตามอุปกรณ์ ESP32 แบบ Real-time ผ่านเว็บเบราว์เซอร์

### 🌟 จุดเด่นของระบบ:

- 🎛️ **ควบคุมได้หลากหลาย** - LED และ RELAY 3 ช่อง
- 🌡️ **ติดตามข้อมูล Sensor** - อุณหภูมิและความชื้นแบบ Real-time
- � **กราฟและการแสดงผล** - Chart.js สำหรับแสดงประวัติข้อมูล
- 🔄 **การสื่อสาร 2 ทาง** - Dashboard ↔ ESP32 ผ่าน MQTT
- ⏰ **เวลาไทย (UTC+7)** - แสดงเวลาไทยถูกต้องทุกจุด
- � **Responsive Design** - ใช้งานได้ทั้ง Desktop และ Mobile
- 🎨 **UI สวยงาม** - Gradient background และ animations

### 🛠️ เทคโนโลยีที่ใช้:

| ส่วน | เทคโนโลยี | รายละเอียด |
|------|-----------|-----------|
| **Backend** | Django 5.2.7 | Web Framework |
| **Frontend** | HTML5, CSS3, JavaScript | UI/UX |
| **Charts** | Chart.js 4.4.0 | Data Visualization |
| **Communication** | MQTT (Paho) | IoT Protocol |
| **Database** | SQLite | Data Storage |
| **Hardware** | ESP32 | IoT Device |
| **IDE** | Arduino IDE | ESP32 Programming |

---

## ✨ ความสามารถของระบบ

### 1. 💡 การควบคุม LED (Onboard LED)
- ✅ **เปิด/ปิด LED** บน ESP32 ผ่านปุ่มบนเว็บ
- ✅ **แสดงสถานะ Real-time** (🟢 ON / ⚫ OFF)
- ✅ **อัปเดตสถานะทันที** เมื่อมีการเปลี่ยนแปลง
- ✅ **ควบคุมจากหลายแหล่ง** (Web, MQTT Explorer, ESP32)

### 2. ⚡ การควบคุม RELAY (3 ช่อง)
- ✅ **ควบคุม RELAY 3 ช่อง** แยกอิสระ
- ✅ **ปุ่ม ON/OFF/Toggle** สำหรับแต่ละ relay
- ✅ **แสดงสถานะแต่ละ relay** แบบ Real-time
- ✅ **Layout แนวนอน** เหมาะสำหรับควบคุมหลายๆ relay
- ✅ **Responsive** - ปรับขนาดตามหน้าจอ (3 คอลัมน์ → 2 → 1)

### 3. 🌡️ การติดตามข้อมูล Sensor
- ✅ **แสดงอุณหภูมิ** (Temperature) แบบ Real-time
- ✅ **แสดงความชื้น** (Humidity) แบบ Real-time
- ✅ **กราฟ Temperature** แสดงประวัติ 20 ครั้งล่าสุด
- ✅ **กราฟ Humidity** แสดงประวัติ 20 ครั้งล่าสุด
- ✅ **ตาราง Recent Readings** แสดง 10 รายการล่าสุด
- ✅ **เวลาอัปเดตล่าสุด** สำหรับแต่ละ sensor

### 4. 🔄 การสื่อสารแบบ 2 ทาง (Bidirectional)

#### Dashboard → ESP32 (Control Commands):
```
User กดปุ่ม → Django ส่งคำสั่ง MQTT → ESP32 รับและทำงาน
```

#### ESP32 → Dashboard (State Updates):
```
ESP32 เปลี่ยนสถานะ → ส่ง MQTT กลับมา → Django อัปเดต Database → UI แสดงผล
```

### 5. ⏰ ระบบเวลา Thailand Timezone
- ✅ **แสดงเวลาไทย (UTC+7)** ทุกจุด
- ✅ **Current Time** อัปเดตทุกวินาที
- ✅ **Last Updated** ใน Temperature/Humidity cards
- ✅ **กราฟแกน X** แสดงเวลาไทย
- ✅ **Recent Readings Table** แสดงวันที่และเวลาไทย
- ✅ **Auto-refresh** ทุก 5 วินาที พร้อม timezone ที่ถูกต้อง

### 6. 🎨 ส่วนติดต่อผู้ใช้ (UI/UX)
- ✅ **Gradient Background** สีเขียวอ่อนพาสเทล
- ✅ **Cards Design** สวยงามพร้อม shadows
- ✅ **Button Animations** hover effects
- ✅ **Status Indicators** สีเขียว/แดง แสดงสถานะ
- ✅ **Loading Indicators** แสดงขณะกำลังทำงาน
- ✅ **Success Messages** แจ้งผลการทำงาน
- ✅ **Auto-update Indicator** แสดงสถานะการรีเฟรช

---

## 🏗️ สถาปัตยกรรมระบบ

### 📐 ภาพรวมการทำงาน:

```
┌──────────────────────────────────────────────────────────────┐
│                      ผู้ใช้งาน (User)                         │
│              Web Browser (Chrome/Firefox/Edge)                │
└────────────────────────┬─────────────────────────────────────┘
                         │ HTTP (Port 8000)
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                  Django Web Server                            │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Views (views_simple.py)                                │  │
│  │ - dashboard_simple()     ← แสดงหน้า Dashboard         │  │
│  │ - control_led()          ← ควบคุม LED                │  │
│  │ - control_relay()        ← ควบคุม RELAY              │  │
│  │ - api_sensor_data()      ← ส่งข้อมูล sensor          │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Models (models.py)                                     │  │
│  │ - Device              ← สถานะ LED                     │  │
│  │ - Relay               ← สถานะ RELAY 1,2,3             │  │
│  │ - SensorData          ← ข้อมูล Temperature/Humidity   │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ MQTT Manager (mqtt_manager.py)                         │  │
│  │ - Persistent Connection  ← เชื่อมต่อค้างไว้           │  │
│  │ - Auto-reconnect        ← เชื่อมต่อใหม่อัตโนมัติ      │  │
│  │ - send_led_command()    ← ส่งคำสั่ง LED              │  │
│  │ - send_relay_command()  ← ส่งคำสั่ง RELAY            │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ MQTT Callbacks (mqtt_callbacks.py)                     │  │
│  │ - handle_relay_state_message()     ← รับสถานะ RELAY  │  │
│  │ - handle_sensor_data_message()     ← รับข้อมูล Sensor│  │
│  │ - handle_led_status_message()      ← รับสถานะ LED    │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ SQLite Database (db.sqlite3)                           │  │
│  │ - iot_dashboard_device      ← ตาราง LED              │  │
│  │ - iot_dashboard_relay       ← ตาราง RELAY            │  │
│  │ - iot_dashboard_sensordata  ← ตาราง Sensor Data      │  │
│  └────────────────────────────────────────────────────────┘  │
└────────────────────────┬─────────────────────────────────────┘
                         │ MQTT Protocol (Port 1883)
                         ▼
┌──────────────────────────────────────────────────────────────┐
│              MQTT Broker (broker.hivemq.com)                  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Control Topics (Subscribe)                             │  │
│  │ • thaitechzone/v2_board/control/led                   │  │
│  │ • thaitechzone/v2_board/control/relay1                │  │
│  │ • thaitechzone/v2_board/control/relay2                │  │
│  │ • thaitechzone/v2_board/control/relay3                │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ State Topics (Publish)                                 │  │
│  │ • thaitechzone/v2_board/state/led                     │  │
│  │ • thaitechzone/v2_board/state/relay1                  │  │
│  │ • thaitechzone/v2_board/state/relay2                  │  │
│  │ • thaitechzone/v2_board/state/relay3                  │  │
│  │ • thaitechzone/v2_board/sensor/data                   │  │
│  └────────────────────────────────────────────────────────┘  │
└────────────────────────┬─────────────────────────────────────┘
                         │ WiFi + MQTT
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                      ESP32 Board                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Arduino Code (.ino)                                    │  │
│  │ - WiFi Connection        ← เชื่อมต่อ WiFi             │  │
│  │ - MQTT Client            ← เชื่อมต่อ MQTT Broker      │  │
│  │ - mqttCallback()         ← รับคำสั่งจาก Dashboard    │  │
│  │ - publishRelayState()    ← ส่งสถานะ RELAY กลับ       │  │
│  │ - publishSensorData()    ← ส่งข้อมูล Sensor          │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Hardware Components                                    │  │
│  │ - LED (GPIO 2)          ← หลอด LED ในตัว             │  │
│  │ - RELAY 1 (GPIO 25)     ← รีเลย์ช่องที่ 1            │  │
│  │ - RELAY 2 (GPIO 26)     ← รีเลย์ช่องที่ 2            │  │
│  │ - RELAY 3 (GPIO 27)     ← รีเลย์ช่องที่ 3            │  │
│  │ - DHT22 (GPIO 4)        ← เซนเซอร์อุณหภูมิ/ความชื้น  │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

### � ขั้นตอนการทำงาน:

#### 1. เมื่อผู้ใช้กดปุ่ม "Turn ON" บน Dashboard:
```
1. User กดปุ่ม → JavaScript ส่ง HTTP POST
2. Django รับ request → views_simple.control_relay()
3. Django เรียก send_relay_command(relay_num, 'ON')
4. MQTT Manager ส่งคำสั่ง → MQTT Broker
5. ESP32 รับคำสั่ง → mqttCallback()
6. ESP32 เปิด RELAY → digitalWrite(RELAY_PIN, HIGH)
7. ESP32 ส่ง State กลับ → publishRelayState()
8. Django รับ State → handle_relay_state_message()
9. อัปเดต Database → relay.relay1_status = True
10. Dashboard รีเฟรช → แสดงสถานะใหม่
```

#### 2. เมื่อ ESP32 ส่งข้อมูล Sensor:
```
1. DHT22 อ่านค่า → dht.readTemperature()
2. ESP32 ส่งข้อมูล → publishSensorData()
3. MQTT Broker รับข้อมูล
4. Django รับข้อมูล → handle_sensor_data_message()
5. สร้างข้อมูลใหม่ → SensorData.objects.create()
6. บันทึกลง Database
7. Dashboard รีเฟรช → ดึงข้อมูลใหม่
8. แสดงบนกราฟและตาราง
```

---

## 💻 ความต้องการของระบบ

### เพื่อการพัฒนา:
- **Python 3.8+** (แนะนำ 3.10 หรือใหม่กว่า)
- **Git** สำหรับ clone repository
- **Text Editor/IDE** (VS Code, PyCharm, หรืออื่นๆ)

### สำหรับ ESP32:
- **ESP32 Development Board** (รุ่นใดก็ได้)
- **Arduino IDE** หรือ **PlatformIO**
- **สาย USB** สำหรับเชื่อมต่อ ESP32
- **WiFi Network** สำหรับเชื่อมต่ออินเทอร์เน็ต

### การตรวจสอบ Python:
```bash
python --version  # ควรแสดง Python 3.8+
```

---

## 🚀 ขั้นตอนการติดตั้ง

### ขั้นตอนที่ 1: Clone Repository

```bash
# Clone โปรเจกต์จาก GitHub
git clone https://github.com/thaitechzone/DjangoDashboardFramework.git

# เข้าไปในโฟลเดอร์โปรเจกต์
cd DjangoDashboardFramework
```

### ขั้นตอนที่ 2: เข้าไปในโฟลเดอร์ Django

```bash
# เข้าไปในโฟลเดอร์ django_iot_dashboard
cd django_iot_dashboard
```

### ขั้นตอนที่ 3: สร้าง Virtual Environment

```bash
# สร้าง virtual environment
python -m venv venv

# สำหรับ macOS/Linux:
python3 -m venv venv
```

### ขั้นตอนที่ 4: เปิดใช้งาน Virtual Environment

**สำหรับ Windows:**
```powershell
# PowerShell
.\venv\Scripts\Activate.ps1

# หรือ CMD
.\venv\Scripts\activate.bat
```

**สำหรับ macOS/Linux:**
```bash
source venv/bin/activate
```

**📝 หมายเหตุ:** เมื่อเปิดใช้งานสำเร็จ จะเห็น `(venv)` ที่ด้านหน้า command prompt

### ขั้นตอนที่ 5: ติดตั้ง Dependencies

```bash
# ติดตั้ง packages ที่จำเป็น
pip install -r requirements.txt

# หรือติดตั้งทีละตัว
pip install django==5.2.7
pip install paho-mqtt==2.1.0
```

### ขั้นตอนที่ 6: ตรวจสอบการติดตั้ง

```bash
# ตรวจสอบว่าติดตั้งครบหรือไม่
pip list

# ควรเห็น:
# Django    5.2.7
# paho-mqtt 2.1.0
```

---

## 🗄️ การกำหนดค่าฐานข้อมูล

### ขั้นตอนที่ 1: สร้าง Migration Files

```bash
# สร้างไฟล์ migration สำหรับ app iot_dashboard
python manage.py makemigrations iot_dashboard
```

**ผลลัพธ์ที่คาดหวัง:**
```
Migrations for 'iot_dashboard':
  iot_dashboard\migrations\0001_initial.py
    - Create model Device
```

### ขั้นตอนที่ 2: ใช้งาน Migrations

```bash
# ใช้งาน migrations เพื่อสร้างตารางในฐานข้อมูล
python manage.py migrate
```

**ผลลัพธ์ที่คาดหวัง:**
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, iot_dashboard, sessions
Running migrations:
  Applying iot_dashboard.0001_initial... OK
```

### ขั้นตอนที่ 3: สร้าง Admin User (ทำหรือไม่ทำก็ได้)

```bash
# สร้าง superuser สำหรับเข้า Django Admin
python manage.py createsuperuser

# กรอกข้อมูล:
# Username: admin
# Email: admin@example.com
# Password: (รหัสผ่านที่ต้องการ)
```

---

## 🏃‍♂️ การรันระบบ

### 🎯 วิธีที่ 1: ใช้ Batch Scripts (Windows) - แนะนำ! ⭐

สำหรับผู้ใช้ Windows เราได้เตรียม **คำสั่งสำเร็จรูป** ที่ใช้งานง่าย **แค่ Double Click!**

#### 📂 ไฟล์ที่มีให้ใช้งาน:

| ไฟล์ | คำอธิบาย | การใช้งาน |
|------|----------|-----------|
| **`setup.bat`** | ติดตั้งระบบครั้งแรก | ใช้ครั้งเดียวตอนเริ่มต้น |
| **`start_all.bat`** | รันทุกอย่างพร้อมกัน | ✅ **ใช้อันนี้ทุกครั้ง** |
| **`start_server.bat`** | รัน Django Server อย่างเดียว | เมื่อต้องการแค่ Web |
| **`start_mqtt.bat`** | รัน MQTT Listener | ทดสอบ MQTT แยก |
| **`stop_all.bat`** | หยุดทุก process | หยุดระบบทั้งหมด |
| **`check_status.bat`** | ตรวจสอบสถานะ | ดูว่าติดตั้งครบหรือยัง |

#### 🚀 ขั้นตอนการใช้งาน:

**ครั้งแรก (First Time Setup):**
```cmd
1. Double Click:  setup.bat
   (รอติดตั้ง Virtual Environment + Django + paho-mqtt + Database)

2. Double Click:  start_all.bat
   (เปิด Django Server + MQTT Listener พร้อมกัน)

3. เปิด Browser ไปที่:
   http://127.0.0.1:8000/
```

**ใช้งานปกติ (Daily Use):**
```cmd
1. Double Click:  start_all.bat

2. เปิด Browser ไปที่:
   http://127.0.0.1:8000/
```

**หยุดการทำงาน:**
```cmd
กด Ctrl+C ใน window "Django Web Server"
หรือ Double Click:  stop_all.bat
```

#### ✨ Features ของ Batch Scripts:

- ✅ **Auto-check** ทุกอย่าง (Python, venv, Django, Database)
- ✅ **Auto-install** dependencies ถ้ายังไม่มี
- ✅ **Auto-migrate** database ถ้ายังไม่มี
- ✅ **Error handling** แจ้งเตือนชัดเจนเป็นภาษาไทย
- ✅ **เปิด Window แยก** สำหรับ Django Server
- ✅ **MQTT อัตโนมัติ** ทำงาน background ผ่าน Django Apps
- ✅ **ใช้งานง่าย** แค่ Double Click!

#### 📝 ตัวอย่างผลลัพธ์จาก start_all.bat:

```
================================================
  Django IoT Dashboard - Starting All Services
================================================

[INFO] กำลังเตรียมระบบ...

[1/2] เปิด Django Web Server...
[2/2] MQTT Listener จะเริ่มทำงานอัตโนมัติ
     (ผ่าน iot_dashboard/apps.py)

================================================
  ✓ ระบบพร้อมใช้งานแล้ว!
================================================

📌 เปิด Web Browser ไปที่:
   http://127.0.0.1:8000/
   http://localhost:8000/

📌 MQTT Listener:
   ทำงานใน Background อัตโนมัติ
   Broker: broker.hivemq.com:1883

📌 การหยุดระบบ:
   ปิด window "Django Web Server"
   หรือกด Ctrl+C ใน window นั้น
```

#### 🔍 ตรวจสอบสถานะด้วย check_status.bat:

```cmd
Double Click:  check_status.bat
```

**ผลลัพธ์:**
```
================================================
  Django IoT Dashboard - System Status
================================================

[1/5] Python Installation:
[✓] Python พร้อมใช้งาน
Python 3.11.5

[2/5] Virtual Environment:
[✓] Virtual Environment พร้อมใช้งาน
    Path: venv\

[3/5] Python Packages:
[✓] Django version: 5.2.7
[✓] paho-mqtt ติดตั้งแล้ว

[4/5] Database:
[✓] Database พร้อมใช้งาน
    File: db.sqlite3

[5/5] Django Server Status:
[✓] Django Server กำลังทำงาน
    URL: http://127.0.0.1:8000/
    PID: 12345
```

> 📖 **อ่านเอกสารเพิ่มเติม:** [QUICK_START_WINDOWS.md](QUICK_START_WINDOWS.md) - คู่มือการใช้งานแบบเต็ม

---

### 🎯 วิธีที่ 2: ใช้ Command Line (Windows/Linux/Mac)

เพื่อให้ระบบทำงานได้เต็มรูปแบบ คุณต้องเปิดใช้งาน **2 processes** พร้อมกัน:

#### Terminal 1: Django Web Server

**Windows CMD:**
```cmd
# เข้าไปในโฟลเดอร์โปรเจกต์
cd DjangoDashboardFramework\django_iot_dashboard

# เปิดใช้งาน virtual environment
.\venv\Scripts\activate.bat

# รัน Django server
python manage.py runserver
```

**Windows PowerShell:**
```powershell
# เข้าไปในโฟลเดอร์โปรเจกต์
cd DjangoDashboardFramework\django_iot_dashboard

# เปิดใช้งาน virtual environment
.\venv\Scripts\Activate.ps1

# ถ้าเจอ Error: Execution Policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# รัน Django server
python manage.py runserver
```

**Linux/Mac:**
```bash
# เข้าไปในโฟลเดอร์โปรเจกต์
cd DjangoDashboardFramework/django_iot_dashboard

# เปิดใช้งาน virtual environment
source venv/bin/activate

# รัน Django server
python manage.py runserver
```

**✅ ผลลัพธ์ที่คาดหวัง:**
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
October 19, 2025 - 17:48:45
Django version 5.2.7, using settings 'dashboard_project.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

#### Terminal 2: MQTT Listener (Optional - สำหรับ Debug)

> 💡 **หมายเหตุ:** MQTT จะทำงาน**อัตโนมัติ**ผ่าน Django Server แล้ว  
> ใช้ตัวเลือกนี้**เฉพาะเมื่อต้องการ debug** และดู log แบบละเอียด

**เปิด Terminal/Command Prompt ใหม่:**

**Windows (ใช้ Batch Script - แนะนำ):**
```cmd
Double Click:  start_mqtt.bat
```

**Windows (Command Line):**
```cmd
# เข้าไปในโฟลเดอร์โปรเจกต์
cd DjangoDashboardFramework\django_iot_dashboard

# เปิดใช้งาน virtual environment
.\venv\Scripts\activate.bat

# รัน MQTT Listener
python manage.py mqtt_listener

# หรือแบบ verbose (แสดง debug ละเอียด)
python manage.py mqtt_listener --verbose
```

**Linux/Mac:**
```bash
# เข้าไปในโฟลเดอร์โปรเจกต์
cd DjangoDashboardFramework/django_iot_dashboard

# เปิดใช้งาน virtual environment
source venv/bin/activate

# รัน MQTT Listener
python manage.py mqtt_listener

# หรือแบบ verbose
python manage.py mqtt_listener --verbose
```

**✅ ผลลัพธ์ที่คาดหวัง (start_mqtt.bat หรือ management command):**
```
========================================
  MQTT Listener กำลังทำงาน
  Broker: broker.hivemq.com:1883
========================================

🚀 Starting MQTT Listener for IoT Dashboard...
🌐 Broker: broker.hivemq.com:1883
==================================================
🔄 Connecting to broker.hivemq.com...
✅ Connected to MQTT Broker successfully!
📡 Subscribed to topics:
   • thaitechzone/v2_board/state/led
   • thaitechzone/v2_board/feedback/led
   • thaitechzone/v2_board/sensor/data          ← รับข้อมูล Temp/Hum
   • thaitechzone/v2_board/state/relay1
   • thaitechzone/v2_board/state/relay2
   • thaitechzone/v2_board/state/relay3

✅ MQTT listener started successfully!
📱 Ready to receive messages from ESP32...
🛑 Press Ctrl+C to stop
```

**เมื่อรับข้อมูล Sensor จะแสดง:**
```
[2025-10-19 20:15:30] 📨 Message Received:
  Topic: thaitechzone/v2_board/sensor/data
  Payload: {"temperature": 28.5, "humidity": 65.2}
  
  📊 Parsed JSON data:
     Temperature: 28.5°C
     Humidity: 65.2%
     
🌡️  Temperature: 28.5°C
💧 Humidity: 65.2%
✅ Sensor data saved to database (ID: 45)
📊 Total sensor records in database: 45
```

**🧪 ทดสอบการรับข้อมูล:**

หากต้องการทดสอบว่า MQTT Listener รับข้อมูลได้:

```cmd
# Terminal 1: รัน MQTT Listener
start_mqtt.bat

# Terminal 2: ส่งข้อมูลทดสอบ
test_send_sensor.bat

# หรือใช้ Python script
python test_mqtt_sender.py
```

> 📖 **อ่านเพิ่มเติม:**  
> - [MQTT_LISTENER_QUICK_GUIDE.md](MQTT_LISTENER_QUICK_GUIDE.md) - คู่มือ MQTT Listener  
> - [FIX_MQTT_LISTENER_SENSOR_DATA.md](FIX_MQTT_LISTENER_SENSOR_DATA.md) - แก้ปัญหา MQTT

---

#### การเลือกใช้งาน MQTT:

| วิธี | เมื่อไหร่ใช้ | ข้อดี | ข้อเสี่ย |
|------|-------------|-------|---------|
| **Django Server อย่างเดียว**<br>`start_server.bat` | ใช้งานปกติ ⭐ | • ง่าย แค่ 1 window<br>• MQTT ทำงานอัตโนมัติ | • ไม่เห็น MQTT log |
| **MQTT Listener แยก**<br>`start_mqtt.bat` | Debug/ทดสอบ 🔍 | • เห็น log ทุกข้อความ<br>• Debug ได้ละเอียด | • ต้องเปิด 2 windows |
| **ทั้งสองพร้อมกัน**<br>`start_all.bat` | พัฒนา/ดู log 🛠️ | • Server + Log ครบ<br>• เหมาะ development | • ใช้ resource มาก |

**📝 สรุป:**
- **ใช้งานทั่วไป:** รัน `start_server.bat` หรือ `start_all.bat` เท่านั้น
- **Debug MQTT:** รัน `start_mqtt.bat` แยกเพื่อดู log
- **ทดสอบ:** ใช้ `test_send_sensor.bat` หรือ `test_mqtt_sender.py`

---

#### การทดสอบ MQTT (ถ้าไม่ใช้ management command):

**Test MQTT Connection:**
```cmd
# Windows:
python -c "from iot_dashboard.mqtt_manager import MQTTManager; m = MQTTManager(); print('MQTT Status:', m.get_status())"

# Linux/Mac:
python -c "from iot_dashboard.mqtt_manager import MQTTManager; m = MQTTManager(); print('MQTT Status:', m.get_status())"
```

**📝 หมายเหตุ:**
- MQTT Listener จะทำงาน **อัตโนมัติใน background** ผ่าน `iot_dashboard/apps.py`
- ไม่จำเป็นต้องรัน Terminal แยก สำหรับการใช้งานปกติ
- Django Server เดียวจัดการทุกอย่างได้

#### เมื่อ Django Server ทำงาน (MQTT อัตโนมัติ):

จะเห็นข้อความในคอนโซล:
```
System check identified no issues (0 silenced).
October 19, 2025 - 17:48:45
Django version 5.2.7, using settings 'dashboard_project.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.

[INFO] MQTT Manager initialized
[INFO] Connecting to MQTT Broker: broker.hivemq.com:1883
[INFO] MQTT Connected successfully!
[INFO] Subscribed to topics:
  - thaitechzone/v2_board/control/led
  - thaitechzone/v2_board/control/relay1
  - thaitechzone/v2_board/control/relay2
  - thaitechzone/v2_board/control/relay3
  - thaitechzone/v2_board/state/led
  - thaitechzone/v2_board/state/relay1
  - thaitechzone/v2_board/state/relay2
  - thaitechzone/v2_board/state/relay3
  - thaitechzone/v2_board/sensor/data
```

---

### 📱 เปิด Dashboard

1. **เปิดเบราว์เซอร์** (Chrome, Firefox, Edge)
2. **ไปที่ URL:**
   - http://127.0.0.1:8000/
   - http://localhost:8000/

3. **ควรเห็นหน้า Dashboard ประกอบด้วย:**
   - ✅ **Current Time** - เวลาไทยปัจจุบัน (UTC+7)
   - ✅ **LED Control Card** - ปุ่มเปิด/ปิด LED
   - ✅ **RELAY Control (3 ช่อง)** - ปุ่มควบคุม RELAY แยกอิสระ
   - ✅ **Temperature Card** - แสดงอุณหภูมิล่าสุด
   - ✅ **Humidity Card** - แสดงความชื้นล่าสุด
   - ✅ **Temperature Chart** - กราฟอุณหภูมิ
   - ✅ **Humidity Chart** - กราฟความชื้น
   - ✅ **Recent Readings Table** - ตารางข้อมูล 10 รายการล่าสุด

4. **ทดสอบการทำงาน:**
   - กดปุ่ม "Turn ON" หรือ "Turn OFF" → ควรเห็นข้อความ Success
   - รอ 2-5 วินาที → Dashboard จะ auto-refresh แสดงสถานะใหม่
   - ถ้ามี ESP32 เชื่อมต่อ → LED/RELAY จะทำงานตามคำสั่ง

---

### 🔴 การหยุดระบบ

**Windows (Batch Scripts):**
```cmd
Double Click:  stop_all.bat
```

**Command Line (ทุก OS):**
```cmd
# ใน Terminal ที่รัน Django Server
กด Ctrl + C

# หรือดู Port และหยุด process
# Windows:
netstat -ano | findstr :8000
taskkill /F /PID <process_id>

# Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

**หยุดแบบปกติ:**
- กด `Ctrl + C` ใน Terminal ที่รัน Django
- ปิดหน้าต่าง Terminal/CMD
- ปิด Browser Tab

1. เปิดเบราว์เซอร์ (Chrome, Firefox, Edge)
2. ไปที่: `http://127.0.0.1:8000/` หรือ `http://localhost:8000/`
3. ควรเห็นหน้า Dashboard พร้อมปุ่มควบคุม LED

---

## 🔧 การเขียนโปรแกรม ESP32

### ขั้นตอนที่ 1: ติดตั้ง Arduino IDE

1. ดาวน์โหลด **Arduino IDE** จาก [arduino.cc](https://www.arduino.cc/en/software)
2. ติดตั้งและเปิด Arduino IDE
3. ไปที่ **File → Preferences**
4. ในช่อง **Additional Board Manager URLs** ใส่:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
5. ไปที่ **Tools → Board → Boards Manager**
6. ค้นหา "esp32" และติดตั้ง **esp32 by Espressif Systems**

### ขั้นตอนที่ 2: ติดตั้ง Library ที่จำเป็น

1. ไปที่ **Sketch → Include Library → Manage Libraries**
2. ค้นหาและติดตั้ง:
   - **PubSubClient** by Nick O'Leary (สำหรับ MQTT)

### ขั้นตอนที่ 3: โค้ด ESP32

สร้างไฟล์ใหม่ใน Arduino IDE และคัดลอกโค้ดด้านล่าง:

```cpp
#include <WiFi.h>
#include <PubSubClient.h>

// ===== การตั้งค่า WiFi =====
// ⚠️ สำคัญ: เปลี่ยนเป็นชื่อและรหัสผ่าน WiFi ของคุณ
const char* ssid = "YOUR_WIFI_NAME";           // ชื่อ WiFi
const char* password = "YOUR_WIFI_PASSWORD";   // รหัสผ่าน WiFi

// ===== การตั้งค่า MQTT =====
const char* mqtt_server = "broker.hivemq.com";
const int mqtt_port = 1883;
const char* mqtt_client_id = "ESP32_ThaiTechZone_LED_01";  // ID เฉพาะของคุณ

// ===== MQTT Topics =====
const char* control_topic = "thaitechzone/v2_board/control/led";    // รับคำสั่ง
const char* state_topic = "thaitechzone/v2_board/state/led";        // ส่งสถานะ
const char* feedback_topic = "thaitechzone/v2_board/feedback/led";  // ส่งการตอบกลับ

// ===== การตั้งค่า Hardware =====
const int LED_PIN = 2;  // LED ใน ESP32 อยู่ที่ GPIO 2

// ===== ตัวแปรสำหรับการทำงาน =====
WiFiClient espClient;
PubSubClient client(espClient);
unsigned long lastHeartbeat = 0;

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
    
    // สร้าง Client ID เฉพาะเพื่อไม่ให้ซ้ำกับคนอื่น
    String clientId = mqtt_client_id;
    clientId += String(random(0xffff), HEX);
    
    if (client.connect(clientId.c_str())) {
      Serial.println(" สำเร็จ! ✅");
      
      // Subscribe เพื่อรับคำสั่งควบคุม
      if (client.subscribe(control_topic)) {
        Serial.print("📡 Subscribe สำเร็จ: ");
        Serial.println(control_topic);
      }
      
      // ส่งสถานะเริ่มต้น
      sendCurrentStatus();
      
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
  // แปลงข้อความเป็น String
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  message.toUpperCase();  // แปลงเป็นตัวพิมพ์ใหญ่
  
  Serial.print("📨 ได้รับข้อความ: [");
  Serial.print(topic);
  Serial.print("] ");
  Serial.println(message);
  
  // ตรวจสอบว่าเป็นคำสั่งควบคุม LED หรือไม่
  if (String(topic) == control_topic) {
    if (message == "ON") {
      digitalWrite(LED_PIN, HIGH);  // เปิด LED
      Serial.println("💡 LED เปิด (ON)");
      
      // ส่งการตอบกลับ
      client.publish(feedback_topic, "ON", true);
      client.publish(state_topic, "ON", true);
      
    } else if (message == "OFF") {
      digitalWrite(LED_PIN, LOW);   // ปิด LED
      Serial.println("🌑 LED ปิด (OFF)");
      
      // ส่งการตอบกลับ
      client.publish(feedback_topic, "OFF", true);
      client.publish(state_topic, "OFF", true);
      
    } else {
      Serial.print("❓ คำสั่งไม่รู้จัก: ");
      Serial.println(message);
    }
  }
}

// ===== ฟังก์ชันส่งสถานะปัจจุบัน =====
void sendCurrentStatus() {
  bool isOn = digitalRead(LED_PIN);
  String status = isOn ? "ON" : "OFF";
  
  if (client.publish(state_topic, status.c_str(), true)) {
    Serial.print("📤 ส่งสถานะ: ");
    Serial.println(status);
  }
}

// ===== ฟังก์ชัน Setup (รันครั้งเดียวตอนเริ่มต้น) =====
void setup() {
  // เริ่มต้น Serial Monitor
  Serial.begin(115200);
  delay(1000);
  
  Serial.println();
  Serial.println("🚀 เริ่มต้นระบบ ESP32 LED Controller");
  Serial.println("=====================================");
  
  // ตั้งค่า LED pin
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);  // เริ่มต้นด้วยการปิด LED
  Serial.println("💡 ตั้งค่า LED เสร็จสิ้น (เริ่มต้น: OFF)");
  
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

// ===== ฟังก์ชัน Loop (รันต่อเนื่อง) =====
void loop() {
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
  
  // ส่งสถานะทุกๆ 30 วินาที (Heartbeat)
  unsigned long now = millis();
  if (now - lastHeartbeat > 30000) {  // 30,000 ms = 30 วินาที
    sendCurrentStatus();
    lastHeartbeat = now;
    Serial.println("💓 ส่ง heartbeat");
  }
  
  delay(100);  // หน่วงเวลาเล็กน้อยเพื่อให้ CPU พัก
}
```

### ขั้นตอนที่ 4: การ Upload โค้ด

1. **เปลี่ยนการตั้งค่า WiFi:**
   ```cpp
   const char* ssid = "ชื่อ_WiFi_ของคุณ";
   const char* password = "รหัสผ่าน_WiFi_ของคุณ";
   ```

2. **เชื่อมต่อ ESP32 กับคอมพิวเตอร์** ด้วยสาย USB

3. **เลือก Board และ Port:**
   - **Tools → Board → ESP32 Arduino → ESP32 Dev Module**
   - **Tools → Port → COMx** (Windows) หรือ **/dev/ttyUSBx** (Linux)

4. **Upload โค้ด:**
   - กดปุ่ม **Upload** (ลูกศรชี้ขวา)
   - รอจนกว่าจะแสดง "Done uploading"

5. **เปิด Serial Monitor:**
   - **Tools → Serial Monitor**
   - ตั้งค่า Baud rate เป็น **115200**
   - ควรเห็นข้อความการเชื่อมต่อ WiFi และ MQTT

---

## 🧪 การทดสอบระบบ

### Test Case 1: ทดสอบ Web Dashboard

1. **เปิดเบราว์เซอร์** ไปที่ `http://127.0.0.1:8000/`
2. **ดู LED Status** ควรแสดงสถานะปัจจุบัน
3. **กดปุ่ม "🟢 Turn ON"**
   - LED บน ESP32 ควรเปิด
   - หน้าเว็บควรอัปเดตเป็น "ON"
   - Terminal MQTT Listener ควรแสดงการส่งคำสั่ง
4. **กดปุ่ม "⚫ Turn OFF"**
   - LED บน ESP32 ควรปิด
   - หน้าเว็บควรอัปเดตเป็น "OFF"

### Test Case 2: ทดสอบ Auto-refresh

1. ดู **indicator สีเขียวมุมขวาบน** ของหน้าเว็บ
2. หน้าเว็บควรอัปเดตทุก 2 วินาที
3. เวลาการอัปเดตล่าสุดควรเปลี่ยนไป

### Test Case 3: ทดสอบ MQTT Listener

1. **รัน MQTT Listener แยก:**
   ```cmd
   Double Click: start_mqtt.bat
   ```

2. **ส่งข้อมูลทดสอบ:**
   ```cmd
   Double Click: test_send_sensor.bat
   ```

3. **ควรเห็นใน MQTT Listener:**
   ```
   [2025-10-19 20:15:30] 📨 Message Received:
     Topic: thaitechzone/v2_board/sensor/data
     Payload: {"temperature": 28.5, "humidity": 65.2}
   
   🌡️  Temperature: 28.5°C
   💧 Humidity: 65.2%
   ✅ Sensor data saved to database (ID: 45)
   ```

4. **เช็ค Dashboard:**
   - Temperature Card ควรแสดง 28.5°C
   - Humidity Card ควรแสดง 65.2%
   - กราฟควรอัปเดต
   - Recent Readings Table ควรมีข้อมูลใหม่

### Test Case 4: ทดสอบ RELAY Control

1. **กดปุ่ม RELAY 1 "Turn ON"**
   - RELAY 1 บน ESP32 ควรทำงาน
   - สถานะบนหน้าเว็บเป็น "🟢 ON"
   - ถ้ารัน MQTT Listener จะเห็น log

2. **ทดสอบ RELAY 2 และ 3** เหมือนกัน

3. **ทดสอบปุ่ม Toggle:**
   - กดปุ่ม "Toggle" หลายครั้ง
   - สถานะควรสลับ ON/OFF

### Test Case 5: ทดสอบด้วย MQTT Explorer (Advanced)

1. **ดาวน์โหลด MQTT Explorer** จาก [mqtt-explorer.com](http://mqtt-explorer.com/)
2. **เชื่อมต่อ** ไปที่ `broker.hivemq.com:1883`
3. **ส่งคำสั่ง LED:**
   - Topic: `thaitechzone/v2_board/control/led`
   - Message: `ON` หรือ `OFF`
4. **ส่งคำสั่ง RELAY:**
   - Topic: `thaitechzone/v2_board/control/relay1`
   - Message: `ON`, `OFF`, หรือ `TOGGLE`
5. **ส่งข้อมูล Sensor:**
   - Topic: `thaitechzone/v2_board/sensor/data`
   - Message: `{"temperature": 30.5, "humidity": 70.2}`
6. **ดูการตอบกลับ:**
   - Topic: `thaitechzone/v2_board/state/led`
   - Topic: `thaitechzone/v2_board/state/relay[1,2,3]`

---

## ⚠️ การแก้ไขปัญหาที่พบบ่อย

### 🐍 ปัญหา Python และ Dependencies

#### ❌ "ModuleNotFoundError: No module named 'django'"

**สาเหตุ:** ไม่ได้เปิดใช้งาน virtual environment

**วิธีแก้:**
```bash
# Windows:
.\venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate

# ตรวจสอบ:
pip list | grep -i django
```

#### ❌ "ModuleNotFoundError: No module named 'paho'"

**สาเหตุ:** ไม่ได้ติดตั้ง paho-mqtt

**วิธีแก้:**
```bash
pip install paho-mqtt==2.1.0
```

#### ❌ "manage.py: command not found"

**สาเหตุ:** อยู่ในโฟลเดอร์ผิด

**วิธีแก้:**
```bash
# ตรวจสอบว่ามีไฟล์ manage.py หรือไม่
ls manage.py     # macOS/Linux
dir manage.py    # Windows

# ถ้าไม่พบ ให้เข้าไปในโฟลเดอร์ที่ถูกต้อง
cd DjangoDashboardFramework/django_iot_dashboard
```

#### ❌ "python ไม่เป็นที่รู้จักคำสั่ง"

**วิธีแก้:**
```cmd
# ลอง py แทน python
py --version
py -m venv venv
py manage.py runserver

# หรือเพิ่ม Python เข้า PATH
# ติดตั้ง Python ใหม่ และติ๊กถูก "Add Python to PATH"
```

---

### 🌐 ปัญหา ESP32 และการเชื่อมต่อ

#### ❌ ESP32 ไม่เชื่อมต่อ WiFi

**ตรวจสอบ:**
1. ชื่อและรหัสผ่าน WiFi ถูกต้องหรือไม่
2. WiFi เป็น 2.4GHz หรือไม่ (ESP32 ไม่รองรับ 5GHz)
3. Signal แรงพอหรือไม่

**วิธีแก้:**
```cpp
// เพิ่มการ debug ใน ESP32 code
Serial.println("WiFi SSID: " + String(ssid));
Serial.println("WiFi Status: " + String(WiFi.status()));
Serial.print("Signal Strength: ");
Serial.println(WiFi.RSSI());
```

#### ❌ ESP32 เชื่อมต่อ WiFi ได้แต่ MQTT ไม่ได้

**ตรวจสอบ:**
1. อินเทอร์เน็ตทำงานหรือไม่
2. MQTT broker address ถูกต้องหรือไม่
3. Port 1883 ถูกบล็อกหรือไม่

**วิธีแก้:**
```cpp
// ตรวจสอบการเชื่อมต่อ MQTT
Serial.print("Connecting to MQTT broker: ");
Serial.println(mqtt_server);
if (client.connect(mqtt_client_id)) {
    Serial.println("✓ MQTT Connected!");
} else {
    Serial.print("✗ MQTT Failed, rc=");
    Serial.println(client.state());
}
```

---

### 📡 ปัญหา MQTT Listener

#### ❌ start_mqtt.bat รันแล้วไม่รับข้อมูล Sensor

**สาเหตุ:** Topic ไม่ตรงกัน

**วิธีแก้:**
1. **ตรวจสอบ Topic ใน ESP32:**
   ```cpp
   const char* SENSOR_DATA_TOPIC = "thaitechzone/v2_board/sensor/data";
   // ไม่ใช่ "sensors/data" (ต้องไม่มี s)
   ```

2. **ทดสอบส่งข้อมูล:**
   ```cmd
   test_send_sensor.bat
   ```

3. **ดู Log แบบละเอียด:**
   ```cmd
   python manage.py mqtt_listener --verbose
   ```

4. **อ่านเอกสาร:**
   - [FIX_MQTT_LISTENER_SENSOR_DATA.md](FIX_MQTT_LISTENER_SENSOR_DATA.md)
   - [MQTT_LISTENER_QUICK_GUIDE.md](MQTT_LISTENER_QUICK_GUIDE.md)

#### ❌ MQTT Listener ขึ้น "Connection Refused"

**วิธีแก้:**
```cmd
# ตรวจสอบ Internet
ping broker.hivemq.com

# ตรวจสอบ Firewall
# ปิด Firewall ชั่วคราว หรือ อนุญาต port 1883

# ลองใช้ MQTT Broker อื่น (ถ้า HiveMQ ล่ม)
# แก้ไขใน mqtt_manager.py:
# MQTT_BROKER = "test.mosquitto.org"
```

---

### 🖥️ ปัญหา Django Server

#### ❌ Port 8000 ถูกใช้งานอยู่

**วิธีแก้:**
```cmd
# Windows: ดู process ที่ใช้ port 8000
netstat -ano | findstr :8000

# ฆ่า process (แทน 12345 ด้วย PID จริง)
taskkill /F /PID 12345

# หรือใช้ port อื่น
python manage.py runserver 8001

# Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

#### ❌ Database ไม่อัปเดต

**วิธีแก้:**
```cmd
# ลบ database และสร้างใหม่
del db.sqlite3   # Windows
rm db.sqlite3    # Linux/Mac

# Migrate ใหม่
python manage.py makemigrations
python manage.py migrate
```

---

### 🔧 ปัญหา Batch Scripts (Windows)

#### ❌ setup.bat ไม่ทำงาน

**วิธีแก้:**
```cmd
# เปิด Command Prompt แบบ Administrator
# คลิกขวา cmd.exe → Run as Administrator

# หรือรันคำสั่งเอง:
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
```

#### ❌ "Execution Policy" Error (PowerShell)

**วิธีแก้:**
```powershell
# เปิด PowerShell แบบ Admin
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# หรือใช้ CMD แทน PowerShell
```

---

### 🎨 ปัญหา Dashboard

#### ❌ Dashboard ไม่แสดงข้อมูล Sensor

**ตรวจสอบ:**
1. ESP32 ส่งข้อมูลแล้วหรือยัง (ดูใน Serial Monitor)
2. MQTT Listener รับข้อมูลหรือไม่ (รัน start_mqtt.bat)
3. Database มีข้อมูลหรือไม่

**วิธีแก้:**
```cmd
# ดูข้อมูลใน Database
python manage.py shell

>>> from iot_dashboard.models import SensorData
>>> SensorData.objects.all().count()
>>> SensorData.objects.latest('timestamp')
>>> exit()

# ถ้าไม่มีข้อมูล ส่งทดสอบ
test_send_sensor.bat
```

#### ❌ เวลาไม่ถูกต้อง (ไม่ใช่เวลาไทย)

**ตรวจสอบ:**
```python
# ใน settings.py
TIME_ZONE = 'Asia/Bangkok'  # ต้องเป็น Asia/Bangkok
USE_TZ = True                # ต้องเป็น True
```

**Clear cache:**
```cmd
# Restart Django Server
Ctrl + C
python manage.py runserver
```

---

## 📚 เอกสารอ้างอิงและไฟล์สำคัญ

### 📂 โครงสร้างโปรเจกต์

```
DjangoDashboardFramework/
├── django_iot_dashboard/              ← โฟลเดอร์หลัก Django
│   ├── manage.py                      ← Django management script
│   ├── requirements.txt               ← Python dependencies
│   ├── db.sqlite3                     ← Database (สร้างหลัง migrate)
│   │
│   ├── setup.bat                      ⭐ ติดตั้งระบบครั้งแรก
│   ├── start_all.bat                  ⭐ รันทุกอย่างพร้อมกัน
│   ├── start_server.bat               ⭐ รัน Django Server
│   ├── start_mqtt.bat                 ⭐ รัน MQTT Listener (debug)
│   ├── stop_all.bat                   ⭐ หยุดระบบ
│   ├── check_status.bat               ⭐ ตรวจสอบสถานะ
│   ├── test_send_sensor.bat           🧪 ทดสอบส่งข้อมูล sensor
│   ├── test_mqtt_sender.py            🧪 ทดสอบ MQTT แบบละเอียด
│   │
│   ├── dashboard_project/             ← Django project settings
│   │   ├── settings.py                ← การตั้งค่าหลัก
│   │   ├── urls.py                    ← URL routing
│   │   └── wsgi.py                    ← WSGI config
│   │
│   └── iot_dashboard/                 ← Django app หลัก
│       ├── models.py                  ← Database models
│       ├── views.py                   ← Views (complex)
│       ├── views_simple.py            ⭐ Views (simple - ใช้งานจริง)
│       ├── urls.py                    ← App URLs
│       ├── apps.py                    ⭐ Auto-start MQTT
│       ├── mqtt_manager.py            ⭐ MQTT Manager (Singleton)
│       ├── mqtt_callbacks.py          ⭐ MQTT Callbacks
│       │
│       ├── templates/
│       │   └── dashboard_simple.html  ⭐ Dashboard UI (ใช้งานจริง)
│       │
│       ├── management/                ← Django management commands
│       │   └── commands/
│       │       └── mqtt_listener.py   ⭐ MQTT Listener command
│       │
│       └── migrations/                ← Database migrations
│
├── QUICK_START_WINDOWS.md             📖 คู่มือเริ่มต้นฉบับเต็ม
├── MQTT_LISTENER_QUICK_GUIDE.md       📖 คู่มือ MQTT Listener
├── FIX_MQTT_LISTENER_SENSOR_DATA.md   📖 แก้ปัญหา MQTT
├── RELAY_QUICK_START_GUIDE.md         📖 คู่มือ RELAY
├── ESP32_RELAY_COMPLETE_CODE.ino      📝 โค้ด ESP32 ฉบับสมบูรณ์
├── TIMEZONE_FIX_COMPLETE.md           📖 แก้ไขเวลาไทย
└── README.md                          📖 เอกสารหลัก (ไฟล์นี้)
```

---

### 🎯 ไฟล์ Batch Scripts สำหรับ Windows

| ไฟล์ | วิธีใช้ | คำอธิบาย | ใช้เมื่อไหร่ |
|------|---------|----------|-------------|
| **setup.bat** | Double Click | ติดตั้ง venv + dependencies + database | ครั้งแรกที่โคลนโปรเจกต์ |
| **start_all.bat** | Double Click | รัน Django + MQTT พร้อมกัน | ✅ แนะนำใช้ทุกครั้ง |
| **start_server.bat** | Double Click | รัน Django Server อย่างเดียว | ใช้งาน Web อย่างเดียว |
| **start_mqtt.bat** | Double Click | รัน MQTT Listener แยก | Debug/ดู MQTT log |
| **stop_all.bat** | Double Click | หยุดทุก process | หยุดระบบทั้งหมด |
| **check_status.bat** | Double Click | ตรวจสอบสถานะระบบ | เช็คว่าติดตั้งครบหรือยัง |
| **test_send_sensor.bat** | Double Click | ส่งข้อมูล sensor ทดสอบ | ทดสอบว่า MQTT รับได้ |

---

### 📖 เอกสารประกอบ

| เอกสาร | เนื้อหา | อ่านเมื่อไหร่ |
|--------|---------|--------------|
| **README.md** | เอกสารหลักแบบเต็ม | อ่านก่อนเริ่มโปรเจกต์ |
| **QUICK_START_WINDOWS.md** | คู่มือใช้ Batch Scripts | ผู้ใช้ Windows |
| **MQTT_LISTENER_QUICK_GUIDE.md** | คู่มือ MQTT Listener | เมื่อรัน MQTT แยก |
| **FIX_MQTT_LISTENER_SENSOR_DATA.md** | แก้ปัญหา MQTT ไม่รับข้อมูล | มีปัญหา sensor data |
| **RELAY_QUICK_START_GUIDE.md** | คู่มือใช้งาน RELAY | ควบคุม RELAY 3 ช่อง |
| **TIMEZONE_FIX_COMPLETE.md** | แก้ไขเวลาไทย (UTC+7) | เวลาไม่ถูกต้อง |
| **ESP32_RELAY_COMPLETE_CODE.ino** | โค้ด ESP32 ฉบับสมบูรณ์ | อัปโหลดลง ESP32 |

---

### 🔑 ไฟล์ Python สำคัญ

| ไฟล์ | หน้าที่ | สำคัญ |
|------|---------|-------|
| **mqtt_manager.py** | MQTT Manager (Singleton pattern) | ⭐⭐⭐ |
| **mqtt_callbacks.py** | Callback functions สำหรับ MQTT | ⭐⭐⭐ |
| **views_simple.py** | Views สำหรับ Dashboard (ใช้งานจริง) | ⭐⭐⭐ |
| **apps.py** | Auto-start MQTT เมื่อ Django เริ่มต้น | ⭐⭐⭐ |
| **models.py** | Database models (Device, Relay, SensorData) | ⭐⭐ |
| **mqtt_listener.py** | Management command สำหรับ MQTT | ⭐⭐ |
| **dashboard_simple.html** | Template หน้า Dashboard | ⭐⭐ |

---

### 🎓 MQTT Topics ที่ใช้งาน

#### Control Topics (ส่งคำสั่งจาก Dashboard → ESP32):
```
thaitechzone/v2_board/control/led       → เปิด/ปิด LED
thaitechzone/v2_board/control/relay1    → ควบคุม RELAY 1
thaitechzone/v2_board/control/relay2    → ควบคุม RELAY 2
thaitechzone/v2_board/control/relay3    → ควบคุม RELAY 3
```

**Payload:** `ON`, `OFF`, หรือ `TOGGLE`

#### State Topics (รับสถานะจาก ESP32 → Dashboard):
```
thaitechzone/v2_board/state/led         → สถานะ LED
thaitechzone/v2_board/state/relay1      → สถานะ RELAY 1
thaitechzone/v2_board/state/relay2      → สถานะ RELAY 2
thaitechzone/v2_board/state/relay3      → สถานะ RELAY 3
```

**Payload:** `ON` หรือ `OFF`

#### Sensor Topics (รับข้อมูลจาก ESP32 → Dashboard):
```
thaitechzone/v2_board/sensor/data       → ข้อมูล Temperature/Humidity
```

**Payload (JSON):**
```json
{
  "temperature": 28.5,
  "humidity": 65.2,
  "device_name": "ESP32_DHT22"
}
```

**หรือ Payload (CSV):**
```
28.5,65.2
```

---

### 🔧 คำสั่ง Django Management ที่สำคัญ

```bash
# รัน Django Server
python manage.py runserver

# รัน MQTT Listener แยก (debug)
python manage.py mqtt_listener
python manage.py mqtt_listener --verbose

# สร้าง migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# สร้าง superuser (admin)
python manage.py createsuperuser

# เปิด Django shell
python manage.py shell

# ดูข้อมูลใน Database
python manage.py shell
>>> from iot_dashboard.models import SensorData, Device, Relay
>>> SensorData.objects.all().count()
>>> SensorData.objects.latest('timestamp')
>>> Device.objects.all()
>>> Relay.objects.all()
```

---

### 🌐 URLs ที่สำคัญ

| URL | คำอธิบาย |
|-----|----------|
| http://127.0.0.1:8000/ | Dashboard หลัก |
| http://127.0.0.1:8000/admin/ | Django Admin Panel |
| http://127.0.0.1:8000/api/sensor-data/ | API ข้อมูล sensor (JSON) |
| http://localhost:8000/ | เหมือนกับ 127.0.0.1:8000 |

---

### 📊 Database Models

#### 1. Device (LED Control)
```python
name        : CharField (ชื่ออุปกรณ์)
is_on       : BooleanField (สถานะเปิด/ปิด)
last_updated: DateTimeField (เวลาอัปเดตล่าสุด)
```

#### 2. Relay (RELAY Control - 3 ช่อง)
```python
name            : CharField (ชื่อ controller)
relay1_status   : BooleanField (สถานะ RELAY 1)
relay2_status   : BooleanField (สถานะ RELAY 2)
relay3_status   : BooleanField (สถานะ RELAY 3)
last_updated    : DateTimeField (เวลาอัปเดตล่าสุด)
```

#### 3. SensorData (ข้อมูล Sensor)
```python
device_name : CharField (ชื่ออุปกรณ์)
temperature : FloatField (อุณหภูมิ °C)
humidity    : FloatField (ความชื้น %)
timestamp   : DateTimeField (เวลาบันทึก - timezone aware)
```

---

### 🎯 Quick Commands สำหรับ Windows

#### ครั้งแรก (First Time Setup):
```cmd
git clone https://github.com/thaitechzone/DjangoDashboardFramework.git
cd DjangoDashboardFramework\django_iot_dashboard
setup.bat
start_all.bat
```

#### ใช้งานปกติ (Daily Use):
```cmd
cd DjangoDashboardFramework\django_iot_dashboard
start_all.bat
```

#### Debug MQTT:
```cmd
# Terminal 1
start_mqtt.bat

# Terminal 2
test_send_sensor.bat
```

#### หยุดระบบ:
```cmd
Ctrl + C
```
หรือ
```cmd
stop_all.bat
```

---

### 🔗 Links และ Resources

#### เอกสารภายนอก:
- 🐍 [Django Documentation](https://docs.djangoproject.com/)
- 📡 [MQTT Protocol](https://mqtt.org/)
- 🔌 [Paho MQTT Python](https://pypi.org/project/paho-mqtt/)
- 🎨 [Chart.js Documentation](https://www.chartjs.org/docs/)
- 🛠️ [ESP32 Arduino Core](https://docs.espressif.com/projects/arduino-esp32/)

#### Tools:
- 📊 [MQTT Explorer](http://mqtt-explorer.com/) - MQTT Client สำหรับ debug
- 🔧 [Arduino IDE](https://www.arduino.cc/en/software) - โปรแกรม ESP32
- 🐍 [Python Downloads](https://www.python.org/downloads/) - Python 3.8+
- 📝 [VS Code](https://code.visualstudio.com/) - Code Editor (แนะนำ)

#### MQTT Brokers (Public):
- 🌐 **broker.hivemq.com** (ใช้ในโปรเจกต์นี้)
- 🌐 test.mosquitto.org
- 🌐 mqtt.eclipseprojects.io

---

### 💡 Tips และ Best Practices

#### 1. การใช้งาน MQTT Listener:
- ✅ **ใช้งานปกติ:** รัน Django Server เดียว (MQTT auto-start)
- 🔍 **Debug:** รัน `start_mqtt.bat` แยกเพื่อดู log
- 🧪 **ทดสอบ:** ใช้ `test_send_sensor.bat` ส่งข้อมูลทดสอบ

#### 2. การจัดการ Virtual Environment:
- ✅ เปิด venv ทุกครั้งก่อนรันคำสั่ง Python
- ✅ ใช้ `setup.bat` ติดตั้งครั้งแรก
- ✅ ใช้ `pip list` ตรวจสอบ packages

#### 3. การ Debug:
- 🔍 ดู Serial Monitor บน ESP32 (Baud: 115200)
- 🔍 รัน `python manage.py mqtt_listener --verbose`
- 🔍 เช็ค Database: `python manage.py shell`
- 🔍 ใช้ MQTT Explorer ดู message flow

#### 4. Security (Production):
- ⚠️ เปลี่ยน SECRET_KEY ใน settings.py
- ⚠️ ตั้ง DEBUG = False
- ⚠️ ใช้ MQTT Broker ที่มี authentication
- ⚠️ ใช้ HTTPS แทน HTTP

---

## 🚀 การพัฒนาต่อ

### 🔧 ฟีเจอร์ที่สามารถเพิ่ม:

#### 1. 🔐 Authentication และ Authorization
<canvas id="sensorChart"></canvas>
```

#### ⏰ การตั้งเวลา
```python
# ใน Django models.py
class Schedule(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    turn_on_time = models.TimeField()
    turn_off_time = models.TimeField()
    is_active = models.BooleanField(default=True)
```

#### 🔔 การแจ้งเตือน
```python
# ใช้ Django Channels สำหรับ WebSocket
pip install channels
pip install channels-redis
```

### 🛡️ การเพิ่มความปลอดภัย

#### 🔐 Authentication
```python
# ใน views.py
from django.contrib.auth.decorators import login_required

@login_required
def dashboard_view(request):
    # ...
```

#### 🔒 MQTT over SSL
```cpp
// ใช้ WiFiClientSecure แทน WiFiClient
#include <WiFiClientSecure.h>
WiFiClientSecure espClient;
```

### 📱 การทำ Mobile App

#### React Native
```javascript
import { Client } from 'react-native-mqtt';

const client = new Client({
  uri: 'mqtt://broker.hivemq.com:1883',
  clientId: 'ReactNativeClient'
});
```

#### Flutter
```dart
import 'package:mqtt_client/mqtt_client.dart';

final client = MqttServerClient('broker.hivemq.com', '');
```

---

## 📚 เอกสารอ้างอิง

### 🔗 ลิงก์ที่มีประโยชน์:
- **Django Documentation**: [docs.djangoproject.com](https://docs.djangoproject.com/)
- **ESP32 Arduino Reference**: [docs.espressif.com](https://docs.espressif.com/projects/arduino-esp32/)
- **MQTT Protocol**: [mqtt.org](https://mqtt.org/)
- **PubSubClient Library**: [github.com/knolleary/pubsubclient](https://github.com/knolleary/pubsubclient)

### 📖 หนังสือและบทเรียน:
- **Django for Beginners** by William S. Vincent
- **ESP32 เบื้องต้น** - ThaiTechZone
- **MQTT Essentials** - HiveMQ

---

## 🤝 การสนับสนุน

### 🐛 รายงานปัญหา:
หากพบปัญหาหรือ bug กรุณารายงานที่:
- **GitHub Issues**: [github.com/thaitechzone/DjangoDashboardFramework/issues](https://github.com/thaitechzone/DjangoDashboardFramework/issues)

### 💡 ข้อเสนอแนะ:
- **Email**: thaitechzone@gmail.com
- **Facebook**: ThaiTechZone Community

### 🎯 การพัฒนาร่วมกัน:
1. Fork โปรเจกต์
2. สร้าง feature branch
3. Commit การเปลี่ยนแปลง
4. Push ไปยัง branch
5. สร้าง Pull Request

---

## 📄 สัญญาอนุญาต

โปรเจกต์นี้ใช้สัญญาอนุญาต **MIT License** - ดูรายละเอียดในไฟล์ `LICENSE`

คุณสามารถ:
- ✅ ใช้งานเชิงพาณิชย์
- ✅ แก้ไขและปรับปรุง
- ✅ แจกจ่ายต่อ
- ✅ ใช้งานส่วนตัว

เงื่อนไข:
- 📄 ต้องระบุผู้สร้างต้นฉบับ
- 📄 ต้องใส่ลิขสิทธิ์เดิม

---

## 🎉 ขอบคุณ

### 👨‍💻 ผู้พัฒนา:
- **ThaiTechZone Team**
- **Community Contributors**

### 🙏 Special Thanks:
- **Django Software Foundation**
- **Espressif Systems**
- **Eclipse Paho Project**
- **HiveMQ Public Broker**

---

## 🏆 สรุป

ยินดีด้วย! ตอนนี้คุณมีระบบ **IoT Dashboard** ที่สมบูรณ์แล้ว ซึ่งสามารถ:

✅ **ควบคุม ESP32 ผ่านเว็บ**  
✅ **รับสถานะแบบ Real-time**  
✅ **ใช้งานง่าย UI สวยงาม**  
✅ **ขยายระบบได้ในอนาคต**  

### 🎯 ขั้นตอนถัดไป:
1. **ทดสอบกับอุปกรณ์จริง**
2. **เพิ่มเซนเซอร์ตัวอื่นๆ**
3. **สร้างกราฟแสดงข้อมูล**
4. **เพิ่มระบบแจ้งเตือน**
5. **พัฒนา Mobile App**

### 🚀 **สนุกกับการพัฒนา IoT!**

---

**📞 ติดต่อ:** nattapholj@gmail.com  
**🌐 Website:** www.facebook.com/ThaiTechZone  
**📺 YouTube:** ThaiTechZone Channel  

**⭐ ถ้าชอบโปรเจกต์นี้ กรุณาให้ Star บน GitHub ด้วยนะครับ!**