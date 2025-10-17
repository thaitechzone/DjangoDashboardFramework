# Django IoT Dashboard - คู่มือการติดตั้งและใช้งาน

## 📋 สารบัญ
1. [ความต้องการของระบบ](#ความต้องการของระบบ)
2. [ขั้นตอนการติดตั้ง](#ขั้นตอนการติดตั้ง)
3. [การรันเซิร์ฟเวอร์](#การรันเซิร์ฟเวอร์)
4. [การหยุดเซิร์ฟเวอร์](#การหยุดเซิร์ฟเวอร์)
5. [การใช้งานเบื้องต้น](#การใช้งานเบื้องต้น)
6. [การแก้ไขปัญหาที่พบบ่อย](#การแก้ไขปัญหาที่พบบ่อย)

---

## ความต้องการของระบบ

### ซอฟต์แวร์ที่จำเป็น:
- **Python 3.8+** (แนะนำ Python 3.10 หรือใหม่กว่า)
- **Git** (สำหรับดาวน์โหลดโปรเจค)
- **Terminal/Command Prompt**

### การตรวจสอบ Python:
```bash
# ตรวจสอบเวอร์ชันของ Python
python --version
# หรือ
python3 --version
```

---

## ขั้นตอนการติดตั้ง

### 1. 📁 สร้างโฟลเดอร์โปรเจค
```bash
# สร้างโฟลเดอร์โปรเจค
mkdir django_iot_dashboard

# เข้าไปในโฟลเดอร์
cd django_iot_dashboard
```

### 2. 🐍 สร้าง Virtual Environment
```bash
# สร้าง virtual environment
python -m venv venv

# สำหรับ macOS/Linux:
python3 -m venv venv
```

### 3. 🔄 เปิดใช้งาน Virtual Environment

**สำหรับ Windows (PowerShell/CMD):**
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

**📝 หมายเหตุ:** เมื่อเปิดใช้งาน virtual environment สำเร็จ จะเห็น `(venv)` ปรากฏที่ด้านหน้าของ command prompt

### 4. 📦 ติดตั้ง Django
```bash
# ติดตั้ง Django เวอร์ชันล่าสุด
pip install django

# หรือติดตั้งเวอร์ชันเฉพาะ
pip install django==5.2.7
```

### 5. 💾 สร้างไฟล์ requirements.txt
```bash
# บันทึก dependencies ลงไฟล์
pip freeze > requirements.txt
```

### 6. 🚀 สร้าง Django Project
```bash
# สร้างโปรเจค Django (ใส่ . ที่ท้ายเพื่อไม่ให้สร้างโฟลเดอร์เพิ่ม)
django-admin startproject dashboard_project .

# สร้าง Django App สำหรับ IoT Dashboard
python manage.py startapp iot_dashboard
```

### 7. ⚙️ กำหนดค่า Settings
แก้ไขไฟล์ `dashboard_project/settings.py`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'iot_dashboard',  # ← เพิ่มบรรทัดนี้
]
```

### 8. 🗄️ สร้างฐานข้อมูล
```bash
# รัน migration เพื่อสร้างตาราง
python manage.py migrate
```

---

## การรันเซิร์ฟเวอร์

### 🖥️ เริ่มต้น Development Server

1. **ตรวจสอบให้แน่ใจว่าอยู่ในโฟลเดอร์โปรเจค:**
```bash
# ตรวจสอบตำแหน่งปัจจุบัน
pwd  # macOS/Linux
cd   # Windows

# ควรเห็นไฟล์ manage.py ในโฟลเดอร์
ls    # macOS/Linux
dir   # Windows
```

2. **เปิดใช้งาน Virtual Environment (หากยังไม่ได้เปิด):**
```bash
# Windows
.\venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. **รันเซิร์ฟเวอร์:**
```bash
python manage.py runserver
```

4. **เปิดเบราว์เซอร์:**
   - ไปที่: `http://127.0.0.1:8000/` หรือ `http://localhost:8000/`
   - ควรเห็นหน้า Django Welcome Page

### 🌐 รันเซิร์ฟเวอร์ในพอร์ตอื่น
```bash
# รันในพอร์ต 8080
python manage.py runserver 8080

# รันและให้เครื่องอื่นเข้าถึงได้
python manage.py runserver 0.0.0.0:8000
```

---

## การหยุดเซิร์ฟเวอร์

### ⛔ วิธีหยุดเซิร์ฟเวอร์:
- กด **Ctrl + C** ใน Terminal/Command Prompt
- หรือกด **Ctrl + Break** (สำหรับ Windows บางเวอร์ชัน)

---

## การใช้งานเบื้องต้น

### 👤 สร้าง Admin User
```bash
# สร้าง superuser สำหรับเข้า Django Admin
python manage.py createsuperuser
```

### 📊 เข้าใช้งาน Admin Panel
1. รันเซิร์ฟเวอร์: `python manage.py runserver`
2. เปิดเบราว์เซอร์ไปที่: `http://127.0.0.1:8000/admin/`
3. ล็อกอินด้วย username และ password ที่สร้างไว้

### 🔄 เมื่อแก้ไขโค้ด
Django จะ reload อัตโนมัติเมื่อมีการแก้ไขไฟล์ Python หากต้องการ restart manual:
1. กด Ctrl + C เพื่อหยุดเซิร์ฟเวอร์
2. รันคำสั่ง `python manage.py runserver` อีกครั้ง

---

## การแก้ไขปัญหาที่พบบ่อย

### ❌ ปัญหา: "manage.py: command not found"
**สาเหตุ:** อยู่ในโฟลเดอร์ผิด
```bash
# ตรวจสอบว่ามีไฟล์ manage.py หรือไม่
ls manage.py     # macOS/Linux
dir manage.py    # Windows

# หากไม่พบ ให้เข้าไปในโฟลเดอร์ที่ถูกต้อง
cd path/to/your/django_iot_dashboard
```

### ❌ ปัญหา: "ModuleNotFoundError: No module named 'django'"
**สาเหตุ:** ไม่ได้เปิดใช้งาน virtual environment
```bash
# เปิดใช้งาน virtual environment
# Windows:
.\venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate

# ตรวจสอบว่า Django ติดตั้งแล้วหรือไม่
pip list | grep Django    # macOS/Linux
pip list | findstr Django # Windows
```

### ❌ ปัญหา: "Port already in use"
**สาเหตุ:** มีเซิร์ฟเวอร์อื่นใช้พอร์ต 8000 อยู่
```bash
# ใช้พอร์ตอื่น
python manage.py runserver 8080

# หรือหาและปิดโปรเซสที่ใช้พอร์ต 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F

# macOS/Linux:
lsof -ti:8000 | xargs kill -9
```

### ❌ ปัญหา: Permission Denied (Windows)
**สาเหตุ:** Windows บล็อกการรัน PowerShell scripts
```powershell
# เปิด PowerShell as Administrator และรัน:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# จากนั้นลองรันคำสั่งอีกครั้ง:
.\venv\Scripts\Activate.ps1
```

---

## 📝 คำสั่งที่ใช้บ่อย

```bash
# เปิดใช้งาน virtual environment
.\venv\Scripts\activate          # Windows
source venv/bin/activate         # macOS/Linux

# รันเซิร์ฟเวอร์
python manage.py runserver

# รัน migrations
python manage.py migrate

# สร้าง migrations ใหม่
python manage.py makemigrations

# สร้าง superuser
python manage.py createsuperuser

# เก็บ dependencies
pip freeze > requirements.txt

# ติดตั้งจาก requirements.txt
pip install -r requirements.txt
```

---

## 🎯 ขั้นตอนต่อไป

หลังจากติดตั้งเสร็จแล้ว คุณสามารถ:

1. **พัฒนา Models** สำหรับเก็บข้อมูล IoT devices
2. **สร้าง Views และ Templates** สำหรับ Dashboard
3. **เพิ่ม API endpoints** สำหรับรับส่งข้อมูล
4. **ติดตั้ง packages เพิ่มเติม** เช่น Django REST framework, Celery, Redis

---

## 📞 ช่วยเหลือเพิ่มเติม

หากพบปัญหาการติดตั้งหรือการใช้งาน สามารถ:
- ตรวจสอบ [Django Documentation](https://docs.djangoproject.com/)
- ค้นหาปัญหาใน [Stack Overflow](https://stackoverflow.com/questions/tagged/django)
- ตรวจสอบ error logs ใน terminal

---

**🎉 ขอให้สนุกกับการพัฒนา Django IoT Dashboard!**