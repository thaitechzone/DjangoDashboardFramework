# 🚀 คู่มือการติดตั้งและใช้งาน Django IoT Dashboard

## 📋 ข้อกำหนดระบบ

### ซอฟต์แวร์ที่จำเป็น:
- **Python 3.8 ขึ้นไป** 
- **Git** สำหรับ clone repository
- **MQTT Explorer** (สำหรับทดสอบ MQTT)
- **เว็บเบราว์เซอร์** (Chrome, Firefox, Edge, Safari)

### ตรวจสอบเวอร์ชัน Python:
```cmd
python --version
# หรือ
python -V

# หากไม่มี python ให้ลองใช้
py --version
```

**หมายเหตุ:** หาก Python ไม่ทำงาน ให้ดาวน์โหลดจาก [python.org](https://python.org)

---

## 🔽 ขั้นตอนที่ 1: Clone Project จาก GitHub

### 1.1 Clone Repository
```bash
git clone https://github.com/thaitechzone/DjangoDashboardFramework.git
```

### 1.2 เข้าสู่โฟลเดอร์ Project
```bash
cd DjangoDashboardFramework
```

### 1.3 ตรวจสอบโครงสร้างไฟล์
```cmd
dir
# ควรเห็นไฟล์และโฟลเดอร์:
# - django_iot_dashboard/
# - InstallDjangoDashboard.md
# - Step2FirstLEDOnDashboard.md
# - MQTT_Explorer_Guide.md
# - และไฟล์อื่นๆ
```

---

## 🐍 ขั้นตอนที่ 2: สร้าง Virtual Environment

Virtual Environment ช่วยแยก dependencies ของโปรเจคออกจากระบบหลัก ป้องกันปัญหา conflict

### 2.1 สำหรับ Windows (Command Prompt):
```cmd
# สร้าง virtual environment
python -m venv django_env

# เปิดใช้งาน virtual environment  
django_env\Scripts\activate

# ตรวจสอบว่าเปิดใช้งานสำเร็จ (ควรมี (django_env) หน้าบรรทัดคำสั่ง)
```

### 2.2 สำหรับ Windows (PowerShell):
```powershell
# สร้าง virtual environment
python -m venv django_env

# เปิดใช้งาน virtual environment
.\django_env\Scripts\Activate.ps1

# หากเจอปัญหา ExecutionPolicy ให้รันคำสั่งนี้ก่อน:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2.3 สำหรับ Linux/Mac:
```bash
# สร้าง virtual environment
python3 -m venv django_env

# เปิดใช้งาน virtual environment
source django_env/bin/activate
```

### 2.4 ตรวจสอบการเปิดใช้งาน Virtual Environment:
เมื่อเปิดใช้งานสำเร็จ จะเห็น `(django_env)` หน้าบรรทัดคำสั่ง:
```
(django_env) C:\path\to\DjangoDashboardFramework>
```

---

## 📂 ขั้นตอนที่ 3: เข้าไปยัง Directory ของ Django Project

```cmd
# เข้าไปยังโฟลเดอร์ Django project
cd django_iot_dashboard

# ตรวจสอบไฟล์ในโฟลเดอร์
dir
# ควรเห็น:
# - manage.py (ไฟล์สำคัญสำหรับจัดการ Django)
# - requirements.txt (รายชื่อ packages ที่ต้องติดตั้ง)
# - dashboard_project/ (โฟลเดอร์ settings)
# - iot_dashboard/ (โฟลเดอร์ main app)
```

---

## 📦 ขั้นตอนที่ 4: ติดตั้ง Dependencies

### 4.1 ตรวจสอบไฟล์ requirements.txt:
```cmd
type requirements.txt
# ควรเห็น:
# Django==5.2.7
# paho-mqtt==2.1.0
# asgiref==3.10.0
# sqlparse==0.5.3
# tzdata==2025.2
```

### 4.2 อัปเดต pip (แนะนำ):
```cmd
python -m pip install --upgrade pip
```

### 4.3 ติดตั้ง packages ที่จำเป็น:
```cmd
pip install -r requirements.txt
```

### 4.4 ตรวจสอบการติดตั้ง:
```cmd
pip list
# ควรเห็น packages ที่ติดตั้งพร้อมเวอร์ชัน
```

### Dependencies ที่จะติดตั้ง:
- **Django==5.2.7** - Framework หลัก
- **paho-mqtt==2.1.0** - สำหรับเชื่อมต่อ MQTT
- **asgiref==3.10.0** - สำหรับ async support
- **sqlparse==0.5.3** - สำหรับ SQL parsing
- **tzdata==2025.2** - ข้อมูล timezone

---

## 🗄️ ขั้นตอนที่ 5: ตั้งค่า Database และ Migrations

Django ใช้ SQLite เป็น database เริ่มต้น ไม่ต้องติดตั้งเพิ่มเติม

### 5.1 ตรวจสอบสถานะ migrations:
```cmd
python manage.py showmigrations
# ตรวจสอบว่า migration ไหนถูก apply แล้ว ([X]) และยังไม่ได้ apply ([ ])
```

### 5.2 สร้าง migration files (หากยังไม่มี):
```cmd
python manage.py makemigrations
# สร้างไฟล์ migration จาก model changes
```

### 5.3 รัน migrations เพื่อสร้างตาราง database:
```cmd
python manage.py migrate
# ดำเนินการสร้างตารางใน database ตาม migrations
```

### 5.4 ตรวจสอบว่า migrations ทั้งหมดถูก apply แล้ว:
```cmd
python manage.py showmigrations
# ทุกรายการควรมี [X] หน้า migration name
```

### 5.5 ตรวจสอบไฟล์ database:
```cmd
dir db.sqlite3
# ควรเห็นไฟล์ db.sqlite3 ถูกสร้างขึ้น
```

---

## 👤 ขั้นตอนที่ 6: สร้าง Superuser (ผู้ดูแลระบบ)

Superuser สำหรับเข้าใช้งาน Django Admin Panel

### 6.1 สร้าง superuser:
```cmd
python manage.py createsuperuser
```

### 6.2 ใส่ข้อมูลตามที่ถาม:
```
Username: admin
Email address: admin@example.com
Password: ********
Password (again): ********
```

**หมายเหตุ:** 
- Username และ Email สามารถใส่อะไรก็ได้
- Password ต้องมีความซับซ้อนตามที่ Django กำหนด
- จดจำ username และ password ไว้สำหรับใช้งาน Admin Panel

---

## 🚀 ขั้นตอนที่ 7: รัน Development Server

### 7.1 รัน Django server:
```cmd
python manage.py runserver
```

### 7.2 หรือระบุ port เฉพาะ:
```cmd
python manage.py runserver 8000
```

### 7.3 หรือให้เข้าถึงได้จากเครื่องอื่นในเครือข่าย:
```cmd
python manage.py runserver 0.0.0.0:8000
```

### 7.4 ผลลัพธ์ที่ควรเห็น:
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
October 17, 2025 - 21:15:38
Django version 5.2.7, using settings 'dashboard_project.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

**🎉 เมื่อเห็นข้อความนี้ แสดงว่า Server ทำงานสำเร็จแล้ว!**

---

## 🌐 ขั้นตอนที่ 8: เข้าใช้งาน Dashboard

### 8.1 เปิดเว็บเบราว์เซอร์และไปที่:

#### Dashboard หลัก:
```
http://127.0.0.1:8000/
```
- แสดงหน้า IoT Dashboard
- ดู LED status และอุปกรณ์ต่างๆ

#### Django Admin Panel:
```
http://127.0.0.1:8000/admin/
```
- ใช้ username และ password ที่สร้างในขั้นตอนที่ 6
- จัดการข้อมูลในระบบ

### 8.2 ทดสอบการทำงานเบื้องต้น:
1. **ตรวจสอบหน้า Dashboard** - ควรเห็นหน้าเว็บแสดงสถานะ LED
2. **ทดสอบ Admin Panel** - เข้าสู่ระบบและดูข้อมูล Device
3. **ตรวจสอบ Console** - ไม่ควรมี error ใน terminal

---

## 📡 ขั้นตอนที่ 9: ตั้งค่าและทดสอบ MQTT

### 9.1 รัน MQTT Listener (Terminal แยก):

**เปิด Terminal/Command Prompt ใหม่:**
```cmd
# เข้าสู่โฟลเดอร์ project
cd DjangoDashboardFramework\django_iot_dashboard

# เปิดใช้งาน virtual environment
django_env\Scripts\activate

# รัน MQTT Listener
python manage.py mqtt_listener
```

### 9.2 ผลลัพธ์ที่ควรเห็น:
```
MQTT listener started...
Connected to MQTT Broker with result code 0
```

### 9.3 การทำงานของ MQTT Listener:
- **เชื่อมต่อ** กับ MQTT Broker: `broker.hivemq.com`
- **ฟัง Topic:** `thaitechzone/v2_board/state/led`
- **อัปเดต Database** เมื่อได้รับข้อมูล

---

## 🧪 ขั้นตอนที่ 10: ทดสอบด้วย MQTT Explorer

### 10.1 ติดตั้ง MQTT Explorer:

#### Windows:
1. ดาวน์โหลดจาก: http://mqtt-explorer.com/
2. ติดตั้งไฟล์ `.exe`
3. เปิดโปรแกรม MQTT Explorer

#### macOS:
```bash
brew install --cask mqtt-explorer
```

#### Linux:
```bash
# ดาวน์โหลด AppImage
wget https://github.com/thomasnordquist/MQTT-Explorer/releases/latest/download/MQTT-Explorer-*.AppImage
chmod +x MQTT-Explorer-*.AppImage
./MQTT-Explorer-*.AppImage
```

### 10.2 ตั้งค่าการเชื่อมต่อ MQTT Explorer:

**สร้าง Connection ใหม่:**
- **Name:** `IoT Dashboard Test`
- **Protocol:** `mqtt://`
- **Host:** `broker.hivemq.com`
- **Port:** `1883`
- **Username:** (ว่างไว้)
- **Password:** (ว่างไว้)

**กด Connect**

### 10.3 ทดสอบการส่งข้อมูล:

#### เปิด LED:
- **Topic:** `thaitechzone/v2_board/state/led`
- **Payload:** `ON`
- **QoS:** `0`
- **Retain:** `false`
- **กด Publish**

#### ปิด LED:
- **Topic:** `thaitechzone/v2_board/state/led`
- **Payload:** `OFF`
- **QoS:** `0`
- **Retain:** `false`
- **กด Publish**

### 10.4 ตรวจสอบผลลัพธ์:

**ใน Terminal ที่รัน MQTT Listener:**
```
Received message on topic thaitechzone/v2_board/state/led: ON
Updated Onboard LED status to True
```

**ในหน้า Dashboard:**
- Refresh หน้าเว็บ (F5)
- ควรเห็น LED status เปลี่ยนเป็น 🟢 ON หรือ ⚫ OFF

---

## 🔄 การรัน Server ครั้งต่อไป

### สำหรับการใช้งานประจำ:

**Terminal 1 - Django Web Server:**
```cmd
# 1. เข้าสู่โฟลเดอร์ project
cd DjangoDashboardFramework\django_iot_dashboard

# 2. เปิดใช้งาน virtual environment
django_env\Scripts\activate

# 3. รัน server
python manage.py runserver
```

**Terminal 2 - MQTT Listener (Optional):**
```cmd
# 1. เข้าสู่โฟลเดอร์ project
cd DjangoDashboardFramework\django_iot_dashboard

# 2. เปิดใช้งาน virtual environment
django_env\Scripts\activate

# 3. รัน MQTT listener
python manage.py mqtt_listener
```

---

## ⛔ การหยุด Server

### หยุด Django Server:
- กด `Ctrl + C` ใน terminal ที่รัน server

### หยุด MQTT Listener:
- กด `Ctrl + C` ใน terminal ที่รัน mqtt_listener

### ปิด Virtual Environment:
```cmd
deactivate
```

---

## 🔧 การแก้ไขปัญหา (Troubleshooting)

### ปัญหา 1: Python command ไม่ทำงาน
```cmd
# ลองใช้ py แทน python
py manage.py runserver

# หรือระบุ path เต็ม
C:\Users\YourName\AppData\Local\Programs\Python\Python311\python.exe manage.py runserver
```

### ปัญหา 2: Port 8000 ถูกใช้งานอยู่
```cmd
# ใช้ port อื่น
python manage.py runserver 8080
python manage.py runserver 9000
```

### ปัญหา 3: Migration Error
```cmd
# ลบ database และสร้างใหม่
del db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### ปัญหา 4: MQTT ไม่เชื่อมต่อ
- ตรวจสอบการเชื่อมต่อ Internet
- ตรวจสอบ Firewall ไม่บล็อก port 1883
- ลองใช้ MQTT Broker อื่น เช่น `test.mosquitto.org`

### ปัญหา 5: Virtual Environment ไม่ทำงาน
```cmd
# สำหรับ PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# หรือใช้ Command Prompt แทน PowerShell
```

### ปัญหา 6: ModuleNotFoundError
```cmd
# ตรวจสอบว่าเปิด virtual environment แล้ว
# ติดตั้ง dependencies อีกครั้ง
pip install -r requirements.txt
```

---

## 📊 การตรวจสอบข้อมูลระบบ

### ตรวจสอบผ่าน Django Admin:
1. ไปที่ `http://127.0.0.1:8000/admin/`
2. เข้าสู่ระบบด้วย superuser
3. คลิก **Devices** ใน IoT Dashboard section
4. ดูข้อมูล "Onboard LED" และสถานะ

### ตรวจสอบผ่าน Django Shell:
```cmd
python manage.py shell
```

```python
# ใน Django shell
from iot_dashboard.models import Device

# ดูข้อมูลทั้งหมด
devices = Device.objects.all()
for device in devices:
    print(f"{device.name}: {device.is_on} - Updated: {device.last_updated}")

# ดูข้อมูล LED เฉพาะ
try:
    led = Device.objects.get(name="Onboard LED")
    print(f"LED Status: {'ON' if led.is_on else 'OFF'}")
    print(f"Last Updated: {led.get_last_updated_thai()}")
except Device.DoesNotExist:
    print("LED device not found")

# ออกจาก shell
exit()
```

---

## 📁 โครงสร้างไฟล์ที่สำคัญ

```
DjangoDashboardFramework/
├── django_iot_dashboard/           # โฟลเดอร์หลักของ Django
│   ├── manage.py                   # คำสั่งจัดการ Django
│   ├── requirements.txt            # รายชื่อ packages
│   ├── db.sqlite3                  # Database file
│   ├── dashboard_project/          # Settings และ configuration
│   │   ├── settings.py             # การตั้งค่าหลัก
│   │   ├── urls.py                 # URL routing หลัก
│   │   └── ...
│   └── iot_dashboard/              # Main application
│       ├── models.py               # Database models
│       ├── views.py                # Business logic
│       ├── urls.py                 # URL routing สำหรับ app
│       ├── management/
│       │   └── commands/
│       │       └── mqtt_listener.py # MQTT listener script
│       └── templates/
│           └── iot_dashboard/
│               └── dashboard.html   # HTML template
├── django_env/                     # Virtual environment
├── MQTT_Explorer_Guide.md          # คู่มือ MQTT Explorer
├── Step2FirstLEDOnDashboard.md     # คู่มือการใช้งาน LED
└── InstallDjangoDashboard.md       # คู่มือติดตั้งเพิ่มเติม
```

---

## 🎯 เป้าหมายการเรียนรู้

หลังจากทำตามขั้นตอนนี้สำเร็จแล้ว คุณจะได้:

1. **Django IoT Dashboard** ที่ทำงานได้
2. **ความรู้เกี่ยวกับ Virtual Environment** 
3. **การใช้งาน Django Admin Panel**
4. **การเชื่อมต่อ MQTT** กับ Dashboard
5. **การทดสอบด้วย MQTT Explorer**
6. **ความเข้าใจ Database Migrations**

---

## 📚 ขั้นตอนถัดไป

เมื่อระบบทำงานสมบูรณ์แล้ว:

1. **อ่าน `Step2FirstLEDOnDashboard.md`** - เรียนรู้การใช้งาน LED controls
2. **อ่าน `MQTT_Explorer_Guide.md`** - เรียนรู้การทดสอบ MQTT อย่างละเอียด
3. **อ่าน `InstallDjangoDashboard.md`** - เรียนรู้การติดตั้งขั้นสูง
4. **พัฒนาเพิ่มเติม** - เพิ่ม sensor อื่นๆ, WebSocket, Charts

---

## 💡 เทคนิคการใช้งาน

### 1. การใช้งาน Multiple Terminals:
- **Terminal 1:** Django Server (ต้องเปิดค้างไว้)
- **Terminal 2:** MQTT Listener (ต้องเปิดค้างไว้)
- **Terminal 3:** สำหรับคำสั่งอื่นๆ (migrations, shell, etc.)

### 2. การ Backup ข้อมูล:
```cmd
# สำรองข้อมูล database
copy db.sqlite3 db_backup.sqlite3

# สำรองไฟล์ settings
copy dashboard_project\settings.py settings_backup.py
```

### 3. การใช้งาน Git:
```cmd
# ตรวจสอบสถานะ
git status

# ดูการเปลี่ยนแปลง
git diff

# Commit การเปลี่ยนแปลง
git add .
git commit -m "Your message"
```

---

## 🎉 สรุป

คุณได้ติดตั้งและรัน **Django IoT Dashboard** สำเร็จแล้ว! 

ระบบนี้พร้อมสำหรับ:
- 📊 **แสดงข้อมูล** IoT devices
- 📡 **รับ-ส่งข้อมูล** ผ่าน MQTT
- 🔧 **จัดการข้อมูล** ผ่าน Admin Panel  
- 🧪 **ทดสอบ** ด้วย MQTT Explorer

**Happy Coding! 🚀**