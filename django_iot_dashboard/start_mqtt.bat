@echo off
REM ============================================
REM  Django IoT Dashboard - MQTT Listener
REM  ไฟล์สำหรับรัน MQTT Background Service
REM ============================================

echo.
echo ========================================
echo   Django IoT Dashboard - MQTT Listener
echo ========================================
echo.

REM เช็คว่ามี virtual environment หรือไม่
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] ไม่พบ Virtual Environment!
    echo กรุณารันคำสั่ง: python -m venv venv
    echo.
    pause
    exit /b 1
)

REM เปิดใช้งาน virtual environment
echo [1/2] กำลังเปิดใช้งาน Virtual Environment...
call venv\Scripts\activate.bat

REM ตรวจสอบว่า paho-mqtt ติดตั้งแล้วหรือไม่
python -c "import paho.mqtt.client as mqtt" 2>nul
if errorlevel 1 (
    echo.
    echo [WARNING] ไม่พบ paho-mqtt!
    echo กำลังติดตั้ง dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] ติดตั้ง dependencies ไม่สำเร็จ!
        pause
        exit /b 1
    )
)

echo [2/2] กำลังเริ่มต้น MQTT Listener...
echo.
echo ========================================
echo   MQTT Listener กำลังทำงาน
echo   Broker: broker.hivemq.com:1883
echo ========================================
echo.
echo 📌 คำอธิบาย:
echo    • รับข้อมูล Temperature/Humidity จาก ESP32
echo    • รับสถานะ LED และ RELAY
echo    • แสดง log ทุกข้อความที่รับได้
echo.
echo 💡 Tips:
echo    • ตรวจสอบว่า ESP32 เชื่อมต่อ WiFi แล้ว
echo    • ตรวจสอบว่า ESP32 ส่งข้อมูลไป MQTT Broker
echo    • กด Ctrl+C เพื่อหยุด
echo.

REM รัน Django management command สำหรับ MQTT Listener
python manage.py mqtt_listener --verbose

if errorlevel 1 (
    echo.
    echo [ERROR] MQTT Listener เกิดข้อผิดพลาด!
    echo.
    echo วิธีแก้:
    echo 1. ตรวจสอบว่าเชื่อมต่ออินเทอร์เน็ต
    echo 2. ตรวจสอบว่า broker.hivemq.com ทำงานอยู่
    echo 3. ลองรัน Django Server แทน: start_server.bat
    echo    (MQTT จะทำงานอัตโนมัติผ่าน apps.py)
    echo.
)

pause
