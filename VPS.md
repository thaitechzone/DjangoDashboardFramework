# คู่มือการ Deploy Django IoT Dashboard บน VPS

## สารบัญ
1. [เตรียม VPS](#1-เตรียม-vps)
2. [ติดตั้ง Dependencies](#2-ติดตั้ง-dependencies)
3. [Clone โปรเจคและตั้งค่า Python Environment](#3-clone-โปรเจคและตั้งค่า-python-environment)
4. [ตั้งค่า Environment Variables](#4-ตั้งค่า-environment-variables)
5. [ปรับ Settings สำหรับ Production](#5-ปรับ-settings-สำหรับ-production)
6. [ตั้งค่าฐานข้อมูล](#6-ตั้งค่าฐานข้อมูล)
7. [Collect Static Files](#7-collect-static-files)
8. [ตั้งค่า Gunicorn](#8-ตั้งค่า-gunicorn)
9. [ตั้งค่า Nginx](#9-ตั้งค่า-nginx)
10. [ตั้งค่า SSL (HTTPS)](#10-ตั้งค่า-ssl-https)
11. [ติดตั้งและตั้งค่า MQTT Broker (Mosquitto)](#11-ติดตั้งและตั้งค่า-mqtt-broker-mosquitto)
12. [ตั้งค่า Systemd Services](#12-ตั้งค่า-systemd-services)
13. [ตั้งค่า Firewall](#13-ตั้งค่า-firewall)
14. [ตรวจสอบและแก้ปัญหา](#14-ตรวจสอบและแก้ปัญหา)

---

## สิ่งที่ต้องมีก่อน

- VPS รัน **Ubuntu 22.04 LTS** (แนะนำ) หรือ Ubuntu 20.04
- RAM อย่างน้อย **1 GB** (แนะนำ 2 GB)
- โดเมน หรือ IP สาธารณะ
- SSH access เข้า VPS

---

## 1. เตรียม VPS

### 1.1 เชื่อมต่อ SSH
```bash
ssh root@<YOUR_VPS_IP>
```

### 1.2 อัปเดตระบบ
```bash
apt update && apt upgrade -y
```

### 1.3 สร้าง User ใหม่ (ไม่ควรใช้ root)
```bash
adduser deploy
usermod -aG sudo deploy
su - deploy
```

---

## 2. ติดตั้ง Dependencies

### 2.1 ติดตั้ง Python 3, pip, venv และเครื่องมืออื่น ๆ
```bash
sudo apt install -y python3 python3-pip python3-venv
sudo apt install -y git curl wget build-essential
sudo apt install -y libpq-dev python3-dev  # เผื่อเปลี่ยนเป็น PostgreSQL ในอนาคต
```

### 2.2 ติดตั้ง Nginx
```bash
sudo apt install -y nginx
```

### 2.3 ติดตั้ง Certbot (สำหรับ SSL)
```bash
sudo apt install -y certbot python3-certbot-nginx
```

---

## 3. Clone โปรเจคและตั้งค่า Python Environment

### 3.1 Clone โปรเจคจาก GitHub
```bash
cd /home/deploy
git clone https://github.com/thaitechzone/DjangoDashboardFramework.git
cd DjangoDashboardFramework
```

### 3.2 สร้าง Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3.3 ติดตั้ง Python Packages
```bash
pip install --upgrade pip
pip install -r django_iot_dashboard/requirements.txt
```

### 3.4 ติดตั้ง Gunicorn และ python-dotenv (ถ้ายังไม่มีใน requirements.txt)
```bash
pip install gunicorn python-dotenv
```

---

## 4. ตั้งค่า Environment Variables

### 4.1 สร้างไฟล์ `.env` ที่ root ของโปรเจค
```bash
nano /home/deploy/DjangoDashboardFramework/.env
```

### 4.2 เพิ่มค่าต่อไปนี้ในไฟล์ `.env`
```env
# Django Settings
SECRET_KEY=your-very-long-random-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,<YOUR_VPS_IP>

# Google Gemini AI
GOOGLE_API_KEY=your-google-gemini-api-key

# MQTT Settings
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
MQTT_USERNAME=mqtt_user
MQTT_PASSWORD=mqtt_password

# Weather API (ถ้าใช้)
OPENWEATHER_API_KEY=your-openweather-api-key
```

> **สร้าง SECRET_KEY ใหม่** โดยรันคำสั่ง:
> ```bash
> python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
> ```

### 4.3 ตั้งค่าสิทธิ์ไฟล์ .env (ปกป้องข้อมูล)
```bash
chmod 600 /home/deploy/DjangoDashboardFramework/.env
```

---

## 5. ปรับ Settings สำหรับ Production

### 5.1 แก้ไขไฟล์ `settings.py`

```bash
nano /home/deploy/DjangoDashboardFramework/django_iot_dashboard/dashboard_project/settings.py
```

แก้ไขหรือเพิ่มค่าดังนี้:

```python
import os
from pathlib import Path
from dotenv import load_dotenv

# โหลด .env
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Security ---
SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-key-change-this')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# --- Static Files ---
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'   # เพิ่มบรรทัดนี้

# --- Security Headers (Production) ---
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HTTPS settings (เปิดใช้หลังติดตั้ง SSL)
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SECURE_SSL_REDIRECT = True
```

---

## 6. ตั้งค่าฐานข้อมูล

### 6.1 รัน Database Migrations
```bash
cd /home/deploy/DjangoDashboardFramework/django_iot_dashboard
source /home/deploy/DjangoDashboardFramework/venv/bin/activate
python manage.py migrate
```

### 6.2 สร้าง Superuser สำหรับ Django Admin
```bash
python manage.py createsuperuser
```

---

## 7. Collect Static Files

```bash
cd /home/deploy/DjangoDashboardFramework/django_iot_dashboard
source /home/deploy/DjangoDashboardFramework/venv/bin/activate
python manage.py collectstatic --noinput
```

ไฟล์ static จะถูกรวมไว้ที่ `django_iot_dashboard/staticfiles/`

---

## 8. ตั้งค่า Gunicorn

### 8.1 ทดสอบ Gunicorn ก่อน
```bash
cd /home/deploy/DjangoDashboardFramework/django_iot_dashboard
source /home/deploy/DjangoDashboardFramework/venv/bin/activate
gunicorn --workers 3 --bind 0.0.0.0:8000 dashboard_project.wsgi:application
```
> กด `Ctrl+C` เพื่อหยุด

### 8.2 สร้าง Gunicorn Socket File สำหรับ Systemd
```bash
sudo nano /etc/systemd/system/gunicorn.socket
```

```ini
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```

### 8.3 สร้าง Gunicorn Service
```bash
sudo nano /etc/systemd/system/gunicorn.service
```

```ini
[Unit]
Description=gunicorn daemon for Django IoT Dashboard
Requires=gunicorn.socket
After=network.target

[Service]
User=deploy
Group=www-data
WorkingDirectory=/home/deploy/DjangoDashboardFramework/django_iot_dashboard
ExecStart=/home/deploy/DjangoDashboardFramework/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          dashboard_project.wsgi:application
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### 8.4 เปิดใช้งาน Gunicorn
```bash
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket
sudo systemctl status gunicorn.socket
```

---

## 9. ตั้งค่า Nginx

### 9.1 สร้างไฟล์ config สำหรับโปรเจค
```bash
sudo nano /etc/nginx/sites-available/iot_dashboard
```

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Static files
    location /static/ {
        alias /home/deploy/DjangoDashboardFramework/django_iot_dashboard/staticfiles/;
    }

    # Forward ทุก request ไปยัง Gunicorn
    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
    }

    # ขนาดสูงสุดของ request body
    client_max_body_size 20M;
}
```

### 9.2 เปิดใช้งาน Config
```bash
sudo ln -s /etc/nginx/sites-available/iot_dashboard /etc/nginx/sites-enabled/
sudo nginx -t        # ทดสอบ config
sudo systemctl restart nginx
```

### 9.3 ตั้งค่า Permission ให้ Nginx เข้าถึงไฟล์ได้
```bash
sudo usermod -aG deploy www-data
chmod 710 /home/deploy
```

---

## 10. ตั้งค่า SSL (HTTPS)

### 10.1 ขอ SSL Certificate ด้วย Certbot
```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

> ทำตามขั้นตอนที่ Certbot แนะนำ: กรอก email และยอมรับ terms

### 10.2 ทดสอบ Auto-Renewal
```bash
sudo certbot renew --dry-run
```

### 10.3 เปิด HTTPS Settings ใน settings.py
แก้ไขไฟล์ `settings.py` เปิด comment บรรทัดเหล่านี้:
```python
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
```

---

## 11. ติดตั้งและตั้งค่า MQTT Broker (Mosquitto)

### 11.1 ติดตั้ง Mosquitto
```bash
sudo apt install -y mosquitto mosquitto-clients
```

### 11.2 ตั้งค่า Authentication สำหรับ MQTT
```bash
# สร้าง password file
sudo mosquitto_passwd -c /etc/mosquitto/passwd mqtt_user
# (ระบบจะขอให้ตั้ง password)
```

### 11.3 แก้ไข Mosquitto Config
```bash
sudo nano /etc/mosquitto/conf.d/default.conf
```

```conf
listener 1883 localhost
allow_anonymous false
password_file /etc/mosquitto/passwd

# สำหรับ WSS (WebSocket over SSL) ถ้าต้องการ
# listener 9001
# protocol websockets
```

### 11.4 รีสตาร์ท Mosquitto
```bash
sudo systemctl restart mosquitto
sudo systemctl enable mosquitto
sudo systemctl status mosquitto
```

### 11.5 ทดสอบ MQTT
```bash
# Terminal 1: Subscribe
mosquitto_sub -h localhost -t "test/topic" -u mqtt_user -P your_password

# Terminal 2: Publish
mosquitto_pub -h localhost -t "test/topic" -m "Hello VPS" -u mqtt_user -P your_password
```

---

## 12. ตั้งค่า Systemd Services

### 12.1 สร้าง Service สำหรับ MQTT Listener
สร้าง service เพื่อรัน Django management command `mqtt_listener`:

```bash
sudo nano /etc/systemd/system/mqtt_listener.service
```

```ini
[Unit]
Description=IoT Dashboard MQTT Listener
After=network.target mosquitto.service
Wants=mosquitto.service

[Service]
User=deploy
WorkingDirectory=/home/deploy/DjangoDashboardFramework/django_iot_dashboard
ExecStart=/home/deploy/DjangoDashboardFramework/venv/bin/python manage.py mqtt_listener
Restart=on-failure
RestartSec=5s
StandardOutput=append:/var/log/mqtt_listener.log
StandardError=append:/var/log/mqtt_listener_error.log

[Install]
WantedBy=multi-user.target
```

### 12.2 เปิดใช้งาน MQTT Listener Service
```bash
sudo systemctl daemon-reload
sudo systemctl start mqtt_listener
sudo systemctl enable mqtt_listener
sudo systemctl status mqtt_listener
```

### 12.3 ตรวจสอบสถานะ Services ทั้งหมด
```bash
sudo systemctl status gunicorn
sudo systemctl status nginx
sudo systemctl status mosquitto
sudo systemctl status mqtt_listener
```

---

## 13. ตั้งค่า Firewall

### 13.1 ติดตั้งและตั้งค่า UFW
```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'   # รองรับทั้ง HTTP (80) และ HTTPS (443)
sudo ufw allow 1883/tcp       # MQTT (เปิดเฉพาะถ้า ESP32 connect จากภายนอก)
sudo ufw enable
sudo ufw status
```

> **หมายเหตุ**: ถ้า ESP32 อยู่ใน network เดียวกับ VPS ไม่จำเป็นต้องเปิด port 1883 ออกสาธารณะ

---

## 14. ตรวจสอบและแก้ปัญหา

### ดู Log ของแต่ละ Service

```bash
# Gunicorn logs
sudo journalctl -u gunicorn -f

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# MQTT Listener logs
sudo tail -f /var/log/mqtt_listener.log
sudo tail -f /var/log/mqtt_listener_error.log

# Mosquitto logs
sudo journalctl -u mosquitto -f
```

### คำสั่ง Restart Services

```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
sudo systemctl restart mosquitto
sudo systemctl restart mqtt_listener
```

### ปัญหาที่พบบ่อย

| ปัญหา | สาเหตุ | วิธีแก้ |
|-------|--------|---------|
| `502 Bad Gateway` | Gunicorn ไม่ทำงาน | `sudo systemctl restart gunicorn` |
| Static files ไม่โหลด | ไม่ได้รัน `collectstatic` | รัน `python manage.py collectstatic` |
| MQTT ไม่รับข้อมูล | Service หยุดทำงาน | `sudo systemctl restart mqtt_listener` |
| `ALLOWED_HOSTS` error | ยังไม่ได้เพิ่ม IP/Domain | แก้ไขใน `.env` แล้ว restart gunicorn |
| Permission denied | สิทธิ์ไฟล์ผิด | ตรวจสอบ `chmod` และ `chown` |

---

## สรุปโครงสร้าง Services

```
Internet
   │
   ▼
[Nginx :80/:443]  ─── Static Files (/staticfiles/)
   │
   ▼ (Unix Socket)
[Gunicorn]
   │
   ▼
[Django App]
   │
   ├── [SQLite Database]
   ├── [Mosquitto MQTT Broker :1883]
   │       │
   │       ▼
   │   [mqtt_listener service]
   └── [Google Gemini AI API]
```

---

## อัปเดตโปรเจค (Deployment ครั้งต่อไป)

เมื่อมีการแก้ไข code และต้องการอัปเดต VPS:

```bash
cd /home/deploy/DjangoDashboardFramework
source venv/bin/activate

# ดึง code ใหม่
git pull origin main

# ติดตั้ง packages ใหม่ (ถ้ามี)
pip install -r django_iot_dashboard/requirements.txt

# รัน migrations ใหม่ (ถ้ามี)
cd django_iot_dashboard
python manage.py migrate

# Collect static files ใหม่
python manage.py collectstatic --noinput

# Restart services
sudo systemctl restart gunicorn
sudo systemctl restart mqtt_listener
```
