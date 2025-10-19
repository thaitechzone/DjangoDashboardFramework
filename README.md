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
venv\Scripts\activate

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

#### Terminal 2: MQTT Listener (Optional)

**เปิด Terminal/Command Prompt ใหม่:**

**Windows CMD:**
```cmd
# เข้าไปในโฟลเดอร์โปรเจกต์
cd DjangoDashboardFramework\django_iot_dashboard

# เปิดใช้งาน virtual environment
venv\Scripts\activate

# Test MQTT Connection (Optional)
python -c "from iot_dashboard.mqtt_manager import MQTTManager; m = MQTTManager(); print('MQTT Status:', m.get_status())"
```

**Linux/Mac:**
```bash
# เข้าไปในโฟลเดอร์โปรเจกต์
cd DjangoDashboardFramework/django_iot_dashboard

# เปิดใช้งาน virtual environment
source venv/bin/activate

# Test MQTT Connection (Optional)
python -c "from iot_dashboard.mqtt_manager import MQTTManager; m = MQTTManager(); print('MQTT Status:', m.get_status())"
```

**📝 หมายเหตุ:**
- MQTT Listener จะทำงาน **อัตโนมัติใน background** ผ่าน `iot_dashboard/apps.py`
- ไม่จำเป็นต้องรัน Terminal แยก สำหรับ MQTT
- Django Server เดียวจัดการทุกอย่างได้

#### การทดสอบ MQTT:

เมื่อ Django Server ทำงาน จะเห็นข้อความในคอนโซล:
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

### Test Case 3: ทดสอบด้วย MQTT Explorer (ถ้ามี)

1. **ดาวน์โหลด MQTT Explorer** จาก [mqtt-explorer.com](http://mqtt-explorer.com/)
2. **เชื่อมต่อ** ไปที่ `broker.hivemq.com:1883`
3. **ส่งคำสั่ง:**
   - Topic: `thaitechzone/v2_board/control/led`
   - Message: `ON` หรือ `OFF`
4. **ดูการตอบกลับ:**
   - Topic: `thaitechzone/v2_board/state/led`
   - Topic: `thaitechzone/v2_board/feedback/led`

---

## ⚠️ การแก้ไขปัญหาที่พบบ่อย

### ❌ ปัญหา: "ModuleNotFoundError: No module named 'django'"

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

### ❌ ปัญหา: "ModuleNotFoundError: No module named 'paho'"

**สาเหตุ:** ไม่ได้ติดตั้ง paho-mqtt

**วิธีแก้:**
```bash
pip install paho-mqtt
```

### ❌ ปัญหา: "manage.py: command not found"

**สาเหตุ:** อยู่ในโฟลเดอร์ผิด

**วิธีแก้:**
```bash
# ตรวจสอบว่ามีไฟล์ manage.py หรือไม่
ls manage.py     # macOS/Linux
dir manage.py    # Windows

# ถ้าไม่พบ ให้เข้าไปในโฟลเดอร์ที่ถูกต้อง
cd DjangoDashboardFramework/django_iot_dashboard
```

### ❌ ปัญหา: ESP32 ไม่เชื่อมต่อ WiFi

**ตรวจสอบ:**
1. ชื่อและรหัสผ่าน WiFi ถูกต้องหรือไม่
2. WiFi เป็น 2.4GHz หรือไม่ (ESP32 ไม่รองรับ 5GHz)
3. Signal แรงพอหรือไม่

**วิธีแก้:**
```cpp
// เพิ่มการ debug
Serial.println("WiFi SSID: " + String(ssid));
Serial.println("WiFi Status: " + String(WiFi.status()));
```

### ❌ ปัญหา: ESP32 เชื่อมต่อ WiFi ได้แต่ MQTT ไม่ได้

**ตรวจสอบ:**
1. อินเทอร์เน็ตทำงานหรือไม่
2. MQTT broker address ถูกต้องหรือไม่
3. Port 1883 ถูกบล็อกหรือไม่

**วิธีแก้:**
```cpp
// ทดสอบการ ping
Serial.println("Testing internet connection...");
WiFiClient testClient;
if (testClient.connect("google.com", 80)) {
  Serial.println("Internet OK");
  testClient.stop();
}
```

### ❌ ปัญหา: Dashboard ไม่อัปเดต

**ตรวจสอบ:**
1. MQTT Listener ทำงานหรือไม่
2. Database มีการอัปเดตหรือไม่
3. MQTT topics ถูกต้องหรือไม่

**วิธีแก้:**
```bash
# ตรวจสอบ database
python manage.py shell
>>> from iot_dashboard.models import Device
>>> Device.objects.all()
```

### ❌ ปัญหา: Port 8000 ถูกใช้งานอยู่

**วิธีแก้:**
```bash
# ใช้ port อื่น
python manage.py runserver 8080

# หรือหา process ที่ใช้ port 8000
# Windows:
netstat -ano | findstr :8000

# macOS/Linux:
lsof -i :8000
```

---

## 🚀 การพัฒนาต่อ

### 🔧 ฟีเจอร์ที่สามารถเพิ่ม:

#### 🌡️ การเพิ่มเซนเซอร์
```cpp
// เพิ่มเซนเซอร์อุณหภูมิ
#include "DHT.h"
DHT dht(4, DHT22);

void sendSensorData() {
  float temp = dht.readTemperature();
  float humidity = dht.readHumidity();
  
  String payload = String(temp) + "," + String(humidity);
  client.publish("thaitechzone/v2_board/sensors", payload.c_str());
}
```

#### 📊 การเพิ่มกราฟ
```html
<!-- ใช้ Chart.js -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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