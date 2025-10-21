# 🐳 วิธีสร้าง Docker Image และ Container

## 📋 เอกสารประกอบ Django IoT Dashboard

เอกสารนี้อธิบาย**ขั้นตอนการสร้าง Dockerfile และ Docker Compose** สำหรับโปรเจกต์ Django IoT Dashboard ตั้งแต่เริ่มต้น พร้อมคำอธิบายแต่ละส่วน

---

## 🎯 เป้าหมาย

สร้าง Docker configuration ที่:
- ✅ รัน Django Application บน Docker
- ✅ ติดตั้ง dependencies อัตโนมัติ
- ✅ Migration database อัตโนมัติ
- ✅ เปิด port 8000 เพื่อเข้าถึงจากภายนอก
- ✅ เก็บข้อมูล database ใน volume
- ✅ แจกจ่ายให้ผู้อื่นได้ง่าย

---

## 📁 ขั้นตอนที่ 1: เตรียม Project Structure

```
DjangoDashboardFramework/
├── django_iot_dashboard/       # โฟลเดอร์ Django project
│   ├── dashboard_project/
│   ├── iot_dashboard/
│   ├── manage.py
│   ├── requirements.txt        # ⭐ สำคัญ!
│   └── db.sqlite3
│
├── Dockerfile                  # ← เราจะสร้างไฟล์นี้
├── docker-compose.yml          # ← เราจะสร้างไฟล์นี้
├── .dockerignore              # ← เราจะสร้างไฟล์นี้
└── README.md
```

---

## 📝 ขั้นตอนที่ 2: สร้าง Dockerfile

### 2.1 สร้างไฟล์ `Dockerfile`

สร้างไฟล์ใหม่ชื่อ **`Dockerfile`** (ไม่มี extension) ที่ root ของโปรเจกต์:

```dockerfile
# ======================================
# Django IoT Dashboard - Dockerfile
# ======================================

# ขั้นที่ 1: เลือก Base Image
# ใช้ Python 3.11 slim (ขนาดเล็ก, เหมาะสำหรับ production)
FROM python:3.11-slim

# ขั้นที่ 2: ตั้งค่า Environment Variables
# PYTHONDONTWRITEBYTECODE: ไม่สร้าง .pyc files (ลด disk usage)
# PYTHONUNBUFFERED: แสดง output แบบ real-time
# DJANGO_SETTINGS_MODULE: กำหนด settings module
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=dashboard_project.settings

# ขั้นที่ 3: ตั้งค่า Working Directory
# กำหนดให้ทุกคำสั่งทำงานใน /app
WORKDIR /app

# ขั้นที่ 4: ติดตั้ง System Dependencies
# gcc: สำหรับ compile Python packages บางตัว
# postgresql-client: สำหรับเชื่อมต่อ PostgreSQL (ถ้าใช้ในอนาคต)
# rm -rf /var/lib/apt/lists/*: ลบ cache เพื่อลดขนาด image
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# ขั้นที่ 5: Copy Requirements File
# Copy แค่ requirements.txt ก่อน (เพื่อใช้ประโยชน์จาก Docker cache)
COPY django_iot_dashboard/requirements.txt .

# ขั้นที่ 6: ติดตั้ง Python Dependencies
# --upgrade pip: อัปเดต pip ให้ใหม่ล่าสุด
# --no-cache-dir: ไม่เก็บ cache เพื่อลดขนาด image
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ขั้นที่ 7: Copy Project Files
# Copy ทั้งโฟลเดอร์ django_iot_dashboard เข้า /app
COPY django_iot_dashboard/ .

# ขั้นที่ 8: สร้าง Directories สำหรับ Static และ Media
# mkdir -p: สร้างแม้ว่าจะมีอยู่แล้วก็ไม่ error
RUN mkdir -p staticfiles media

# ขั้นที่ 9: Expose Port
# บอก Docker ว่า container จะใช้ port 8000
EXPOSE 8000

# ขั้นที่ 10: สร้าง Entrypoint Script
# สร้าง shell script ที่จะรันเมื่อ container เริ่มต้น
RUN echo '#!/bin/bash\n\
echo "========================================"\n\
echo "  Django IoT Dashboard - Starting..."\n\
echo "========================================"\n\
echo ""\n\
echo "Waiting for database..."\n\
sleep 2\n\
echo ""\n\
echo "Running migrations..."\n\
python manage.py makemigrations --noinput\n\
python manage.py migrate --noinput\n\
echo ""\n\
echo "========================================"\n\
echo "  ✓ Server starting at port 8000"\n\
echo "========================================"\n\
echo ""\n\
echo "📌 Access Dashboard at:"\n\
echo "   http://localhost:8000/"\n\
echo "   http://127.0.0.1:8000/"\n\
echo ""\n\
echo "📌 MQTT Broker:"\n\
echo "   broker.hivemq.com:1883"\n\
echo ""\n\
echo "📌 Stop: Press Ctrl+C or run: docker-compose down"\n\
echo ""\n\
exec python manage.py runserver 0.0.0.0:8000' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

# ขั้นที่ 11: กำหนด Entrypoint
# รัน entrypoint script เมื่อ container เริ่มต้น
ENTRYPOINT ["/entrypoint.sh"]
```

### 💡 คำอธิบาย Dockerfile แต่ละส่วน:

| คำสั่ง | คำอธิบาย | เหตุผล |
|--------|----------|--------|
| `FROM python:3.11-slim` | เลือก base image | slim = ขนาดเล็ก (~150MB) |
| `ENV PYTHONUNBUFFERED=1` | แสดง logs แบบ real-time | เห็น output ทันที ไม่รอ buffer |
| `WORKDIR /app` | กำหนด working directory | ทุกคำสั่งทำงานใน /app |
| `COPY requirements.txt .` | Copy แค่ requirements ก่อน | ใช้ Docker cache layer |
| `RUN pip install...` | ติดตั้ง Python packages | ติดตั้งก่อน copy code |
| `COPY django_iot_dashboard/ .` | Copy project files | Copy ทุกไฟล์เข้า container |
| `EXPOSE 8000` | เปิด port | บอก Docker ว่าใช้ port 8000 |
| `ENTRYPOINT` | กำหนดคำสั่งเริ่มต้น | รัน migration + runserver |

---

## 📝 ขั้นตอนที่ 3: สร้าง .dockerignore

สร้างไฟล์ **`.dockerignore`** เพื่อไม่ให้ copy ไฟล์ที่ไม่จำเป็นเข้า image:

```dockerfile
# ======================================
# .dockerignore
# ไฟล์ที่ไม่ต้อง copy เข้า Docker Image
# ======================================

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
dist/
build/

# Virtual Environment
venv/
env/
ENV/

# Django
*.log
db.sqlite3
db.sqlite3-journal
staticfiles/
media/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Git
.git/
.gitignore

# Documentation (เก็บแค่ README)
*.md
!README.md

# OS
.DS_Store
Thumbs.db

# Batch files (Windows specific)
*.bat

# Test files
test_*.py
*_test.py
```

### 💡 ทำไมต้องมี .dockerignore?

- ✅ ลดขนาด image (ไม่ copy ไฟล์ที่ไม่ใช้)
- ✅ เร็วขึ้น (copy น้อยกว่า)
- ✅ ปลอดภัยขึ้น (ไม่ copy secrets, logs)

---

## 📝 ขั้นตอนที่ 4: สร้าง docker-compose.yml

สร้างไฟล์ **`docker-compose.yml`** สำหรับจัดการ containers:

```yaml
# ======================================
# Docker Compose Configuration
# สำหรับรัน Django IoT Dashboard
# ======================================

version: '3.8'

services:
  # Django Web Application
  web:
    # Build จาก Dockerfile ในโฟลเดอร์เดียวกัน
    build: .
    
    # ชื่อ container
    container_name: django_iot_dashboard
    
    # คำสั่งที่จะรัน (override ENTRYPOINT ถ้าต้องการ)
    command: python manage.py runserver 0.0.0.0:8000
    
    # Mount volumes
    volumes:
      # Mount code เพื่อ live reload (development)
      - ./django_iot_dashboard:/app
      # Mount database เพื่อเก็บข้อมูล (persistent)
      - sqlite_data:/app/db
    
    # Port mapping (host:container)
    ports:
      - "8000:8000"
    
    # Environment variables
    environment:
      - PYTHONUNBUFFERED=1
      - DJANGO_SETTINGS_MODULE=dashboard_project.settings
    
    # Restart policy
    restart: unless-stopped
    
    # Network
    networks:
      - iot_network
    
    # Health check
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000')"]
      interval: 30s        # ตรวจสอบทุก 30 วินาที
      timeout: 10s         # รอ response สูงสุด 10 วินาที
      retries: 3           # ลองใหม่ 3 ครั้ง
      start_period: 40s    # รอ 40 วินาทีก่อนเริ่มตรวจสอบ

# Volumes (persistent storage)
volumes:
  sqlite_data:
    driver: local

# Networks
networks:
  iot_network:
    driver: bridge
```

### 💡 คำอธิบาย docker-compose.yml:

| Section | คำอธิบาย | เหตุผล |
|---------|----------|--------|
| `version: '3.8'` | เวอร์ชัน compose file | ใช้ syntax ล่าสุด |
| `build: .` | Build จาก Dockerfile | อยู่โฟลเดอร์เดียวกัน |
| `volumes` | Mount folders | Code + Database persistent |
| `ports` | Port mapping | 8000:8000 = host:container |
| `restart: unless-stopped` | Auto restart | รันอัตโนมัติเมื่อ reboot |
| `healthcheck` | ตรวจสุขภาพ | ตรวจว่า container ทำงานปกติ |
| `networks` | สร้าง network | แยก network ไม่ปนกับ container อื่น |

---

## 📝 ขั้นตอนที่ 5: สร้าง docker-compose.dev.yml (Optional)

สร้างไฟล์ **`docker-compose.dev.yml`** สำหรับ development:

```yaml
# ======================================
# Development Docker Compose
# สำหรับ development ที่ต้องการ live reload
# ======================================

version: '3.8'

services:
  web:
    build: .
    container_name: django_iot_dashboard_dev
    command: python manage.py runserver 0.0.0.0:8000
    
    # Mount code เพื่อ live reload
    volumes:
      - ./django_iot_dashboard:/app
      - sqlite_data:/app/db
    
    ports:
      - "8000:8000"
    
    environment:
      - PYTHONUNBUFFERED=1
      - DJANGO_SETTINGS_MODULE=dashboard_project.settings
      - DEBUG=True          # เปิด debug mode
    
    restart: unless-stopped
    networks:
      - iot_network
    
    # เปิด stdin และ tty สำหรับ debug
    stdin_open: true
    tty: true

volumes:
  sqlite_data:
    driver: local

networks:
  iot_network:
    driver: bridge
```

---

## 🔧 ขั้นตอนที่ 6: Build และ Test

### 6.1 Build Docker Image

```bash
# Build image
docker build -t django-iot-dashboard .

# ดู images ที่สร้างแล้ว
docker images
```

**Output ที่คาดหวัง:**
```
REPOSITORY               TAG       IMAGE ID       CREATED         SIZE
django-iot-dashboard     latest    1234567890ab   2 minutes ago   450MB
```

### 6.2 Test รัน Container แบบเดี่ยว

```bash
# Run container
docker run -d \
  --name test_django \
  -p 8000:8000 \
  django-iot-dashboard

# ดู logs
docker logs -f test_django

# Test เปิด browser
# http://localhost:8000/

# หยุดและลบ
docker stop test_django
docker rm test_django
```

### 6.3 Test รันด้วย Docker Compose

```bash
# Build และรัน
docker-compose up --build

# หรือรันแบบ background
docker-compose up -d --build

# ดู logs
docker-compose logs -f

# ดูสถานะ
docker-compose ps

# หยุด
docker-compose down
```

---

## 📊 ขั้นตอนที่ 7: ตรวจสอบและ Debug

### 7.1 เข้าไปใน Container

```bash
# เข้าไปใน container shell
docker-compose exec web bash

# หรือ
docker exec -it django_iot_dashboard bash
```

**ภายใน container สามารถรัน:**
```bash
# ตรวจสอบ Python version
python --version

# ตรวจสอบ packages
pip list

# ตรวจสอบ Django
python manage.py --version

# ตรวจสอบ migrations
python manage.py showmigrations

# สร้าง superuser
python manage.py createsuperuser

# Exit
exit
```

### 7.2 ตรวจสอบ Logs

```bash
# ดู logs แบบ real-time
docker-compose logs -f

# ดู logs ของ web service อย่างเดียว
docker-compose logs -f web

# ดู logs 50 บรรทัดล่าสุด
docker-compose logs --tail=50 web
```

### 7.3 ตรวจสอบ Network

```bash
# ดู networks
docker network ls

# ดูรายละเอียด network
docker network inspect djangodashboardframework_iot_network

# ตรวจสอบ port
docker port django_iot_dashboard
```

### 7.4 ตรวจสอบ Volumes

```bash
# ดู volumes
docker volume ls

# ดูรายละเอียด volume
docker volume inspect djangodashboardframework_sqlite_data

# ดูขนาด volume
docker system df -v
```

---

## 🎯 ขั้นตอนที่ 8: Optimize Image Size

### 8.1 ตรวจสอบขนาด Image

```bash
# ดูขนาด image แต่ละ layer
docker history django-iot-dashboard

# ดูขนาดรวม
docker images django-iot-dashboard
```

### 8.2 Tips เพื่อลดขนาด:

1. **ใช้ slim base image** ✅ (ทำแล้ว)
   ```dockerfile
   FROM python:3.11-slim  # แทน python:3.11
   ```

2. **ลบ cache หลังติดตั้ง** ✅ (ทำแล้ว)
   ```dockerfile
   RUN apt-get update && apt-get install -y gcc \
       && rm -rf /var/lib/apt/lists/*
   
   RUN pip install --no-cache-dir -r requirements.txt
   ```

3. **ใช้ .dockerignore** ✅ (ทำแล้ว)

4. **Multi-stage build** (Advanced):
   ```dockerfile
   # Stage 1: Builder
   FROM python:3.11-slim as builder
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --user --no-cache-dir -r requirements.txt
   
   # Stage 2: Runtime
   FROM python:3.11-slim
   WORKDIR /app
   COPY --from=builder /root/.local /root/.local
   COPY django_iot_dashboard/ .
   ENV PATH=/root/.local/bin:$PATH
   EXPOSE 8000
   CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
   ```

---

## 🚀 ขั้นตอนที่ 9: แจกจ่าย Docker Image

### 9.1 วิธีที่ 1: แจกผ่าน Docker Hub

```bash
# 1. Login Docker Hub
docker login

# 2. Tag image
docker tag django-iot-dashboard yourusername/django-iot-dashboard:latest

# 3. Push to Docker Hub
docker push yourusername/django-iot-dashboard:latest

# ผู้ใช้งานสามารถ pull:
docker pull yourusername/django-iot-dashboard:latest
docker run -d -p 8000:8000 yourusername/django-iot-dashboard:latest
```

### 9.2 วิธีที่ 2: แจกเป็นไฟล์ .tar

```bash
# 1. Save image เป็นไฟล์
docker save -o django-iot-dashboard.tar django-iot-dashboard:latest

# 2. Compress (optional)
gzip django-iot-dashboard.tar
# ได้ไฟล์: django-iot-dashboard.tar.gz

# ผู้ใช้งานสามารถ load:
docker load -i django-iot-dashboard.tar
# หรือ
gunzip -c django-iot-dashboard.tar.gz | docker load
```

### 9.3 วิธีที่ 3: แจกผ่าน GitHub (แนะนำ)

```bash
# ผู้ใช้งาน:
git clone https://github.com/yourusername/DjangoDashboardFramework.git
cd DjangoDashboardFramework
docker-compose up --build

# หรือใช้ batch script (Windows)
docker-start.bat
```

---

## 📋 ขั้นตอนที่ 10: สร้าง Batch Scripts (Windows)

### 10.1 docker-start.bat

```batch
@echo off
echo ========================================
echo   Django IoT Dashboard - Docker Mode
echo ========================================
echo.

REM ตรวจสอบ Docker Desktop
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] ไม่พบ Docker!
    pause
    exit /b 1
)

REM Build และ Run
echo กำลัง Build Docker Image...
docker-compose up --build -d

echo.
echo ========================================
echo   ✓ Django IoT Dashboard พร้อมแล้ว!
echo ========================================
echo.
echo 📌 เปิด Web Browser ไปที่:
echo    http://localhost:8000/
echo.

timeout /t 2 /nobreak >nul
start http://localhost:8000/

pause
```

### 10.2 docker-stop.bat

```batch
@echo off
echo หยุด Django IoT Dashboard...
docker-compose down
echo ✓ หยุดเรียบร้อยแล้ว
pause
```

### 10.3 docker-logs.bat

```batch
@echo off
echo ========================================
echo   Django IoT Dashboard - Logs
echo ========================================
echo.
docker-compose logs -f
pause
```

---

## ✅ Checklist การสร้าง Docker

- [ ] สร้าง `Dockerfile`
- [ ] สร้าง `.dockerignore`
- [ ] สร้าง `docker-compose.yml`
- [ ] สร้าง `docker-compose.dev.yml` (optional)
- [ ] ทดสอบ build: `docker build -t django-iot-dashboard .`
- [ ] ทดสอบรัน: `docker run -d -p 8000:8000 django-iot-dashboard`
- [ ] ทดสอบ compose: `docker-compose up --build`
- [ ] ตรวจสอบ logs: `docker-compose logs -f`
- [ ] เข้า browser: `http://localhost:8000/`
- [ ] ทดสอบ LED control
- [ ] ทดสอบ RELAY control
- [ ] ทดสอบ sensor data
- [ ] สร้าง batch scripts (Windows)
- [ ] เขียนเอกสารใน README.md

---

## 🎓 สรุปขั้นตอนทั้งหมด

```bash
# 1. สร้างไฟล์
touch Dockerfile
touch .dockerignore
touch docker-compose.yml

# 2. Build image
docker build -t django-iot-dashboard .

# 3. Test รัน
docker run -d -p 8000:8000 django-iot-dashboard

# 4. หรือใช้ compose
docker-compose up --build

# 5. เปิด browser
# http://localhost:8000/

# 6. ดู logs
docker-compose logs -f

# 7. หยุด
docker-compose down
```

---

## 🔗 Resources

- 🐳 [Docker Documentation](https://docs.docker.com/)
- 📚 [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- 🐍 [Python Docker Images](https://hub.docker.com/_/python)
- 🎯 [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)

---

## 💡 Tips & Tricks

### Build แบบไม่ใช้ cache:
```bash
docker-compose build --no-cache
```

### รัน specific service:
```bash
docker-compose up web
```

### ดู resource usage:
```bash
docker stats django_iot_dashboard
```

### Clean up ทั้งหมด:
```bash
docker-compose down -v --rmi all
docker system prune -a
```

---

**🎉 เสร็จสิ้น!** ตอนนี้คุณสามารถสร้าง Docker Image และแจกจ่ายได้แล้ว! 🚀
