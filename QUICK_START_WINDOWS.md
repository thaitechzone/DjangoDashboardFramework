# 🚀 Quick Start Guide สำหรับ Windows

## 📌 คำสั่งสำเร็จรูปสำหรับ CMD/PowerShell

ไฟล์ Batch Scripts ที่สร้างไว้ให้ใช้งานง่าย **แค่ Double Click!**

---

## 🎯 ไฟล์สำคัญที่ต้องรู้จัก

| ไฟล์ | คำอธิบาย | เมื่อไหร่ใช้ |
|------|----------|-------------|
| **`setup.bat`** | ติดตั้งระบบครั้งแรก | ครั้งแรกที่โคลนโปรเจกต์มา |
| **`start_all.bat`** | รันทุกอย่างพร้อมกัน | ใช้งานปกติทุกครั้ง (แนะนำ) |
| **`start_server.bat`** | รัน Django Server อย่างเดียว | เมื่อต้องการรัน Web Server เท่านั้น |
| **`start_mqtt.bat`** | รัน MQTT Listener | ทดสอบ MQTT แยก (ไม่จำเป็น) |
| **`stop_all.bat`** | หยุดทุก process | หยุดระบบทั้งหมด |
| **`check_status.bat`** | ตรวจสอบสถานะ | ดูว่าติดตั้งครบหรือยัง |

---

## 🔧 ขั้นตอนการใช้งาน (ครั้งแรก)

### 1️⃣ Clone โปรเจกต์

```cmd
git clone https://github.com/thaitechzone/DjangoDashboardFramework.git
cd DjangoDashboardFramework\django_iot_dashboard
```

### 2️⃣ ติดตั้งระบบ (ครั้งแรกเท่านั้น)

**Double Click ที่ไฟล์:** `setup.bat`

หรือพิมพ์ใน CMD:
```cmd
setup.bat
```

**สิ่งที่จะเกิดขึ้น:**
1. ✅ ตรวจสอบ Python
2. ✅ สร้าง Virtual Environment
3. ✅ ติดตั้ง Django และ paho-mqtt
4. ✅ สร้างฐานข้อมูล
5. ✅ ถามว่าจะสร้าง Admin User ไหม (Optional)

**ระยะเวลา:** ประมาณ 2-3 นาที

---

## ▶️ วิธีรันระบบ (ทุกครั้งที่ใช้งาน)

### วิธีที่ 1: รันทุกอย่างพร้อมกัน (แนะนำ) ⭐

**Double Click ที่ไฟล์:** `start_all.bat`

หรือพิมพ์ใน CMD:
```cmd
start_all.bat
```

**ผลลัพธ์:**
- ✅ เปิด Django Web Server ใน window ใหม่
- ✅ MQTT Listener ทำงานอัตโนมัติใน background
- ✅ พร้อมใช้งานที่ http://127.0.0.1:8000/

### วิธีที่ 2: รัน Django Server อย่างเดียว

**Double Click ที่ไฟล์:** `start_server.bat`

หรือพิมพ์ใน CMD:
```cmd
start_server.bat
```

**ใช้เมื่อ:** ต้องการแค่ Web Dashboard ไม่ต้องการ MQTT

---

## 🛑 วิธีหยุดระบบ

### วิธีที่ 1: กดปุ่มในหน้าต่าง

ใน window ที่แสดง "Django Web Server" กด:
```
Ctrl + C
```

### วิธีที่ 2: ใช้ Batch Script

**Double Click ที่ไฟล์:** `stop_all.bat`

หรือพิมพ์ใน CMD:
```cmd
stop_all.bat
```

**ผลลัพธ์:**
- ✅ หยุด Django Server (port 8000)
- ✅ แจ้งเตือนถ้ามี Python processes อื่นๆ

### วิธีที่ 3: ปิดหน้าต่างทั้งหมด

แค่กดปุ่ม ❌ ที่มุมบนขวาของหน้าต่าง

---

## 🔍 ตรวจสอบสถานะระบบ

**Double Click ที่ไฟล์:** `check_status.bat`

หรือพิมพ์ใน CMD:
```cmd
check_status.bat
```

**จะแสดง:**
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

---

## 📖 คำสั่ง CMD สำเร็จรูป

### สำหรับติดตั้งครั้งแรก:

```cmd
REM 1. Clone โปรเจกต์
git clone https://github.com/thaitechzone/DjangoDashboardFramework.git
cd DjangoDashboardFramework\django_iot_dashboard

REM 2. ติดตั้งระบบ
setup.bat

REM 3. รันระบบ
start_all.bat
```

### สำหรับใช้งานปกติ:

```cmd
REM เข้าโฟลเดอร์โปรเจกต์
cd DjangoDashboardFramework\django_iot_dashboard

REM รันระบบ
start_all.bat

REM เปิด Browser ไปที่
start http://127.0.0.1:8000/
```

### Manual Commands (ถ้าไม่ใช้ .bat):

```cmd
REM 1. เปิด Virtual Environment
venv\Scripts\activate

REM 2. รัน Django Server
python manage.py runserver

REM 3. เปิดหน้าต่างใหม่สำหรับทดสอบ
start cmd

REM 4. ในหน้าต่างใหม่ - เปิด venv อีกครั้ง
venv\Scripts\activate

REM 5. Test MQTT (Optional)
python -c "from iot_dashboard.mqtt_manager import MQTTManager; m = MQTTManager(); print(m.get_status())"
```

---

## 🎨 PowerShell Commands

ถ้าใช้ PowerShell แทน CMD:

```powershell
# 1. เปิด Virtual Environment
.\venv\Scripts\Activate.ps1

# ถ้าเจอ Error: Execution Policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 2. รัน Django Server
python manage.py runserver

# 3. เปิด Browser
Start-Process "http://127.0.0.1:8000/"
```

---

## 🐛 แก้ไขปัญหาที่พบบ่อย

### ❌ ปัญหา: "python ไม่เป็นที่รู้จักคำสั่ง"

**วิธีแก้:**
1. ติดตั้ง Python จาก https://www.python.org/downloads/
2. ✅ ติ๊กถูกที่ **"Add Python to PATH"** ขณะติดตั้ง
3. Restart Command Prompt

**หรือใช้:**
```cmd
py --version
py -m venv venv
py manage.py runserver
```

### ❌ ปัญหา: "Access Denied" เมื่อรัน .bat

**วิธีแก้:**
1. คลิกขวาที่ Command Prompt
2. เลือก **"Run as Administrator"**
3. รันคำสั่งอีกครั้ง

### ❌ ปัญหา: Port 8000 ถูกใช้งานอยู่

**วิธีแก้:**
```cmd
REM ดู process ที่ใช้ port 8000
netstat -ano | find "8000"

REM ฆ่า process (แทน 12345 ด้วย PID จริง)
taskkill /F /PID 12345

REM หรือใช้ port อื่น
python manage.py runserver 8001
```

### ❌ ปัญหา: Virtual Environment ไม่ทำงาน

**วิธีแก้:**
```cmd
REM ลบ venv เดิม
rmdir /s /q venv

REM สร้างใหม่
python -m venv venv

REM Activate
venv\Scripts\activate

REM ติดตั้ง packages
pip install -r requirements.txt
```

---

## 🎯 สรุปการใช้งานแบบสั้น

### ครั้งแรก (First Time Setup):
```cmd
git clone <repo-url>
cd DjangoDashboardFramework\django_iot_dashboard
setup.bat
start_all.bat
```

### ใช้งานปกติ (Daily Use):
```cmd
cd DjangoDashboardFramework\django_iot_dashboard
start_all.bat
```

### เปิด Dashboard:
```
http://127.0.0.1:8000/
```

### หยุดระบบ:
```cmd
Ctrl + C
```
หรือ
```cmd
stop_all.bat
```

---

## 📚 เอกสารเพิ่มเติม

- **README.md** - เอกสารหลักแบบเต็ม (ภาษาไทย)
- **Step1CreateFrameWork.md** - ขั้นตอนการสร้าง Framework
- **RELAY_QUICK_START_GUIDE.md** - คู่มือ RELAY
- **ESP32_RELAY_COMPLETE_CODE.ino** - โค้ด ESP32

---

## 🆘 ติดปัญหา?

1. ✅ ลองรัน `check_status.bat` ดูสถานะ
2. ✅ ลองรัน `setup.bat` ใหม่
3. ✅ อ่าน Error Messages ใน CMD ดูว่าขาดอะไร
4. ✅ เช็ค Python version: `python --version` (ต้อง 3.8+)
5. ✅ เช็ค pip: `pip --version`

---

## ✨ Tips & Tricks

### Shortcut สำหรับ Windows:

1. **สร้าง Shortcut บน Desktop:**
   - คลิกขวาที่ `start_all.bat`
   - เลือก **"Send to → Desktop (create shortcut)"**
   - ตั้งชื่อ: "🚀 Start IoT Dashboard"

2. **เปิด CMD ในโฟลเดอร์นี้เร็วๆ:**
   - กด `Shift + Right Click` ในโฟลเดอร์
   - เลือก **"Open PowerShell window here"** หรือ **"Open command window here"**

3. **เปิด Browser อัตโนมัติ:**
   - สร้างไฟล์ `open_dashboard.bat`:
   ```batch
   @echo off
   start http://127.0.0.1:8000/
   ```

---

**🎉 สนุกกับการพัฒนา IoT Dashboard!**
