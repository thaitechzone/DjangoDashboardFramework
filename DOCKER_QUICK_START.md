# 🐳 Docker Quick Start Guide

## 📋 สารบัญ
1. [ความต้องการของระบบ](#-ความต้องการของระบบ)
2. [ติดตั้ง Docker Desktop](#-ติดตั้ง-docker-desktop)
3. [รันด้วย Docker (วิธีที่ 1 - แนะนำ)](#-วิธีที่-1-รันด้วย-docker-compose-แนะนำ)
4. [รันด้วย Docker CLI (วิธีที่ 2)](#-วิธีที่-2-รันด้วย-docker-cli)
5. [การทดสอบ](#-การทดสอบ)
6. [การแก้ไขปัญหา](#️-การแก้ไขปัญหา)

---

## 📦 ความต้องการของระบบ

### Windows:
- Windows 10/11 (64-bit)
- WSL 2 (Windows Subsystem for Linux)
- Docker Desktop for Windows
- RAM: 4GB ขึ้นไป (แนะนำ 8GB)

### Mac:
- macOS 10.15 หรือใหม่กว่า
- Docker Desktop for Mac
- RAM: 4GB ขึ้นไป (แนะนำ 8GB)

### Linux:
- Docker Engine
- Docker Compose
- RAM: 2GB ขึ้นไป (แนะนำ 4GB)

---

## 🔧 ติดตั้ง Docker Desktop

### Windows:

1. **ดาวน์โหลด Docker Desktop:**
   - ไปที่: https://www.docker.com/products/docker-desktop/
   - คลิก "Download for Windows"

2. **ติดตั้ง WSL 2:**
   ```powershell
   # เปิด PowerShell แบบ Administrator
   wsl --install
   
   # หรือถ้าติดตั้งแล้ว อัปเดต
   wsl --update
   ```

3. **ติดตั้ง Docker Desktop:**
   - รันไฟล์ `Docker Desktop Installer.exe`
   - ติ๊กถูก "Use WSL 2 instead of Hyper-V"
   - กด "OK" และรอติดตั้ง
   - Restart คอมพิวเตอร์

4. **เปิด Docker Desktop:**
   - เปิดแอพ Docker Desktop
   - รอให้ Docker Engine เริ่มทำงาน (สัญลักษณ์สีเขียว)

5. **ตรวจสอบการติดตั้ง:**
   ```cmd
   docker --version
   docker-compose --version
   ```

### Mac:

1. **ดาวน์โหลดและติดตั้ง:**
   - Intel Chip: https://desktop.docker.com/mac/main/amd64/Docker.dmg
   - Apple Silicon (M1/M2): https://desktop.docker.com/mac/main/arm64/Docker.dmg

2. **เปิด Docker Desktop:**
   - ลาก Docker.app ไปที่ Applications
   - เปิดแอพ Docker
   - อนุญาต permissions

3. **ตรวจสอบ:**
   ```bash
   docker --version
   docker-compose --version
   ```

### Linux:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose

# CentOS/RHEL
sudo yum install docker docker-compose

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

---

## 🚀 วิธีที่ 1: รันด้วย Docker Compose (แนะนำ)

### ขั้นตอนที่ 1: Clone โปรเจกต์

```bash
# Clone repository
git clone https://github.com/thaitechzone/DjangoDashboardFramework.git

# เข้าไปในโฟลเดอร์
cd DjangoDashboardFramework
```

### ขั้นตอนที่ 2: Build และ Run

**Windows (Command Prompt):**
```cmd
docker-compose up --build
```

**Windows (PowerShell):**
```powershell
docker-compose up --build
```

**Mac/Linux:**
```bash
docker-compose up --build
```

**หรือรัน background (detached mode):**
```bash
docker-compose up -d --build
```

### ผลลัพธ์ที่คาดหวัง:

```
[+] Building 45.2s (15/15) FINISHED
[+] Running 2/2
 ✔ Network djangodashboardframework_iot_network  Created
 ✔ Container django_iot_dashboard                Started

========================================
  Django IoT Dashboard - Starting...
========================================

Waiting for database...

Running migrations...
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, iot_dashboard, sessions
Running migrations:
  Applying iot_dashboard.0001_initial... OK

========================================
  ✓ Server starting at port 8000
========================================

📌 Access Dashboard at:
   http://localhost:8000/
   http://127.0.0.1:8000/

📌 MQTT Broker:
   broker.hivemq.com:1883

📌 Stop: Press Ctrl+C or run: docker-compose down

Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
October 21, 2025 - 10:30:00
Django version 5.2.7, using settings 'dashboard_project.settings'
Starting development server at http://0.0.0.0:8000/
Quit the server with CONTROL-C.
```

### ขั้นตอนที่ 3: เปิด Dashboard

1. เปิดเบราว์เซอร์
2. ไปที่: **http://localhost:8000/**

---

## 🔨 วิธีที่ 2: รันด้วย Docker CLI

### Build Image:

```bash
docker build -t django-iot-dashboard .
```

### Run Container:

```bash
docker run -d \
  --name django_iot_dashboard \
  -p 8000:8000 \
  -v $(pwd)/django_iot_dashboard:/app \
  django-iot-dashboard
```

**Windows CMD:**
```cmd
docker run -d --name django_iot_dashboard -p 8000:8000 -v %cd%\django_iot_dashboard:/app django-iot-dashboard
```

**Windows PowerShell:**
```powershell
docker run -d --name django_iot_dashboard -p 8000:8000 -v ${PWD}\django_iot_dashboard:/app django-iot-dashboard
```

### ดู Logs:

```bash
docker logs -f django_iot_dashboard
```

---

## 📱 การใช้งาน

### คำสั่งพื้นฐาน:

```bash
# เริ่มต้น containers
docker-compose up

# เริ่มต้นแบบ background
docker-compose up -d

# หยุด containers
docker-compose down

# ดู logs
docker-compose logs -f

# ดูสถานะ
docker-compose ps

# Rebuild image
docker-compose build --no-cache

# Restart containers
docker-compose restart
```

### เข้าถึง Container:

```bash
# เข้าไปใน container shell
docker-compose exec web bash

# รันคำสั่ง Django
docker-compose exec web python manage.py shell
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py migrate
```

### ดู Logs แบบ Real-time:

```bash
# ดู logs ทั้งหมด
docker-compose logs -f

# ดู logs เฉพาะ web service
docker-compose logs -f web
```

---

## 🧪 การทดสอบ

### 1. ทดสอบ Web Dashboard:

```bash
# เปิดเบราว์เซอร์
http://localhost:8000/
```

### 2. ทดสอบ MQTT:

```bash
# เข้าไปใน container
docker-compose exec web bash

# รัน MQTT listener
python manage.py mqtt_listener

# หรือส่งข้อมูลทดสอบ (terminal อื่น)
python test_mqtt_sender.py
```

### 3. ทดสอบ Database:

```bash
docker-compose exec web python manage.py shell
```

```python
from iot_dashboard.models import Device, Relay, SensorData

# ดูข้อมูลทั้งหมด
print("Devices:", Device.objects.all())
print("Relays:", Relay.objects.all())
print("Sensors:", SensorData.objects.all().count())
```

---

## 🔍 ดูข้อมูล Container

### ข้อมูลทั่วไป:

```bash
# ดู containers ที่รันอยู่
docker ps

# ดูทุก containers (รวมที่หยุด)
docker ps -a

# ดู images
docker images

# ดู volumes
docker volume ls

# ดู networks
docker network ls
```

### ข้อมูลโดยละเอียด:

```bash
# ดูข้อมูล container
docker inspect django_iot_dashboard

# ดู resource usage
docker stats django_iot_dashboard

# ดู port mapping
docker port django_iot_dashboard
```

---

## 🛑 หยุดและลบ

### หยุด Containers:

```bash
# หยุดและลบ containers
docker-compose down

# หยุดและลบทุกอย่าง (รวม volumes)
docker-compose down -v

# หยุดและลบทุกอย่าง (รวม images)
docker-compose down --rmi all
```

### ลบแบบ Manual:

```bash
# หยุด container
docker stop django_iot_dashboard

# ลบ container
docker rm django_iot_dashboard

# ลบ image
docker rmi django-iot-dashboard

# ลบ volume
docker volume rm djangodashboardframework_sqlite_data
```

---

## ⚡ Development Mode

สำหรับ development ที่ต้องการ live reload:

```bash
# ใช้ docker-compose.dev.yml
docker-compose -f docker-compose.dev.yml up --build

# หรือตั้งค่าเป็น default
export COMPOSE_FILE=docker-compose.dev.yml
docker-compose up
```

**Features:**
- ✅ Live code reload
- ✅ Debug mode เปิดอยู่
- ✅ Volume mount สำหรับ development

---

## 🎯 การแจกจ่าย (Distribution)

### วิธีที่ 1: แจกจ่ายผ่าน Docker Hub

```bash
# Tag image
docker tag django-iot-dashboard yourusername/django-iot-dashboard:latest

# Push to Docker Hub
docker login
docker push yourusername/django-iot-dashboard:latest
```

**ผู้ใช้งานสามารถ pull:**
```bash
docker pull yourusername/django-iot-dashboard:latest
docker run -d -p 8000:8000 yourusername/django-iot-dashboard:latest
```

### วิธีที่ 2: แจกจ่ายผ่าน Docker Image File

```bash
# Save image เป็นไฟล์
docker save -o django-iot-dashboard.tar django-iot-dashboard:latest

# Compress (optional)
gzip django-iot-dashboard.tar
```

**ผู้ใช้งานสามารถ load:**
```bash
# Load image
docker load -i django-iot-dashboard.tar

# หรือถ้า compressed
gunzip -c django-iot-dashboard.tar.gz | docker load

# Run
docker run -d -p 8000:8000 django-iot-dashboard:latest
```

### วิธีที่ 3: แจกจ่ายผ่าน GitHub (แนะนำ)

```bash
# ผู้ใช้งาน clone และรัน
git clone https://github.com/thaitechzone/DjangoDashboardFramework.git
cd DjangoDashboardFramework
docker-compose up --build
```

---

## ⚠️ การแก้ไขปัญหา

### ❌ Docker Desktop ไม่เริ่มต้น (Windows)

**สาเหตุ:** WSL 2 ไม่ทำงาน

**วิธีแก้:**
```powershell
# เปิด PowerShell แบบ Admin
wsl --update
wsl --set-default-version 2

# Restart Docker Desktop
```

### ❌ Port 8000 ถูกใช้งานอยู่

**วิธีแก้:**
```bash
# ดู process ที่ใช้ port 8000
# Windows:
netstat -ano | findstr :8000

# Mac/Linux:
lsof -i :8000

# แก้ไข port ใน docker-compose.yml
ports:
  - "8080:8000"  # ใช้ port 8080 แทน
```

### ❌ Container ไม่สามารถเชื่อมต่อ Internet

**วิธีแก้:**
```bash
# ตรวจสอบ DNS
docker run --rm busybox nslookup google.com

# แก้ไข DNS ใน Docker Desktop
# Settings → Docker Engine → แก้ไข dns
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}
```

### ❌ Build ช้า

**วิธีแก้:**
```bash
# ใช้ BuildKit
export DOCKER_BUILDKIT=1
docker-compose build

# หรือ Windows
set DOCKER_BUILDKIT=1
docker-compose build
```

### ❌ Volume permission issues (Linux)

**วิธีแก้:**
```bash
# แก้ไข ownership
sudo chown -R $USER:$USER ./django_iot_dashboard

# หรือรันด้วย sudo
sudo docker-compose up
```

### ❌ MQTT ไม่เชื่อมต่อ

**วิธีแก้:**
```bash
# ตรวจสอบ Internet ใน container
docker-compose exec web ping -c 3 broker.hivemq.com

# ตรวจสอบ firewall
# อนุญาต port 1883 (MQTT)
```

---

## 📊 Resource Management

### กำหนด Resource Limits:

แก้ไขใน `docker-compose.yml`:

```yaml
services:
  web:
    build: .
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

### Clean Up:

```bash
# ลบ containers ที่หยุดแล้ว
docker container prune

# ลบ images ที่ไม่ใช้
docker image prune

# ลบ volumes ที่ไม่ใช้
docker volume prune

# ลบทุกอย่างที่ไม่ใช้
docker system prune -a
```

---

## 🎓 Best Practices

### 1. Security:
- ✅ ไม่ใส่ SECRET_KEY ใน Dockerfile
- ✅ ใช้ environment variables
- ✅ อัปเดต base image เป็นประจำ

### 2. Performance:
- ✅ ใช้ .dockerignore
- ✅ Multi-stage builds (ถ้าจำเป็น)
- ✅ Cache layers ที่เหมาะสม

### 3. Development:
- ✅ ใช้ volume mounts สำหรับ live reload
- ✅ แยก development และ production compose files
- ✅ ใช้ health checks

---

## 🔗 Links

- 🐳 [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- 📚 [Docker Documentation](https://docs.docker.com/)
- 🐙 [Docker Hub](https://hub.docker.com/)
- 📖 [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)

---

## ✅ Checklist

- [ ] ติดตั้ง Docker Desktop
- [ ] Clone โปรเจกต์
- [ ] รัน `docker-compose up --build`
- [ ] เปิด http://localhost:8000/
- [ ] ทดสอบ LED control
- [ ] ทดสอบ RELAY control
- [ ] ทดสอบ sensor data
- [ ] ตรวจสอบ MQTT connection

---

**🎉 พร้อมใช้งาน!**

ตอนนี้โปรเจกต์พร้อมรันบน Docker แล้ว!  
แค่ `docker-compose up` ก็ใช้งานได้เลย! 🚀
