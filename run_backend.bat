@echo off
title Django IoT Dashboard - Backend
cd /d "%~dp0"

echo ========================================
echo  Django IoT Dashboard Backend
echo ========================================

REM ตรวจสอบ Virtual Environment
if not exist "venv\Scripts\activate.bat" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment. Make sure Python is installed.
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created.
)

REM Activate venv
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM ติดตั้ง dependencies
echo [INFO] Installing/updating requirements...
pip install -r django_iot_dashboard\requirements.txt --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install requirements.
    pause
    exit /b 1
)
echo [OK] Requirements ready.

REM เข้าไปใน project directory
cd django_iot_dashboard

REM รัน migrations
echo [INFO] Running database migrations...
python manage.py migrate --run-syncdb
if errorlevel 1 (
    echo [ERROR] Migration failed.
    pause
    exit /b 1
)
echo [OK] Database ready.

REM เปิด MQTT Listener ใน window ใหม่
echo [INFO] Starting MQTT Listener in a new window...
start "MQTT Listener" cmd /k "call ..\venv\Scripts\activate.bat && python manage.py mqtt_listener"

REM เปิด Django Development Server
echo [INFO] Starting Django server at http://127.0.0.1:8000
echo [INFO] Press Ctrl+C to stop the server.
echo ========================================
python manage.py runserver

pause
