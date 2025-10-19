@echo off
REM ============================================
REM  Django IoT Dashboard - Start All Services
REM  รัน Django Server และ MQTT Listener พร้อมกัน
REM ============================================

echo.
echo ================================================
echo   Django IoT Dashboard - Starting All Services
echo ================================================
echo.

REM เช็คว่ามี virtual environment หรือไม่
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] ไม่พบ Virtual Environment!
    echo.
    echo กรุณาทำตามขั้นตอนนี้ก่อน:
    echo 1. python -m venv venv
    echo 2. venv\Scripts\activate.bat
    echo 3. pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo [INFO] กำลังเตรียมระบบ...
echo.

REM เปิด Django Server ใน window ใหม่
echo [1/2] เปิด Django Web Server...
start "Django Web Server" cmd /k "cd /d %~dp0 && call start_server.bat"

REM รอ 3 วินาที
timeout /t 3 /nobreak >nul

REM MQTT จะทำงานอัตโนมัติผ่าน Django Apps.py
echo [2/2] MQTT Listener จะเริ่มทำงานอัตโนมัติ
echo      (ผ่าน iot_dashboard/apps.py)
echo.

echo ================================================
echo   ✓ ระบบพร้อมใช้งานแล้ว!
echo ================================================
echo.
echo 📌 เปิด Web Browser ไปที่:
echo    http://127.0.0.1:8000/
echo    http://localhost:8000/
echo.
echo 📌 MQTT Listener:
echo    ทำงานใน Background อัตโนมัติ
echo    Broker: broker.hivemq.com:1883
echo.
echo 📌 การหยุดระบบ:
echo    ปิด window "Django Web Server"
echo    หรือกด Ctrl+C ใน window นั้น
echo.

pause
