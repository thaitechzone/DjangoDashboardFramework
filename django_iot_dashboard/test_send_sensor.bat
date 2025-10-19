@echo off
REM ============================================
REM  Test MQTT - ส่งข้อมูล Sensor ทดสอบ
REM  ใช้สำหรับทดสอบว่า MQTT Listener รับข้อมูลได้
REM ============================================

echo.
echo ========================================
echo   Test MQTT Sensor Data
echo ========================================
echo.

REM เช็คว่ามี virtual environment หรือไม่
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] ไม่พบ Virtual Environment!
    pause
    exit /b 1
)

REM เปิดใช้งาน virtual environment
call venv\Scripts\activate.bat

echo [INFO] กำลังส่งข้อมูล sensor ทดสอบ...
echo.

REM ส่งข้อมูล sensor ทดสอบ
python -c "import paho.mqtt.client as mqtt; import json; import time; client = mqtt.Client(); client.connect('broker.hivemq.com', 1883); time.sleep(1); data = {'temperature': 28.5, 'humidity': 65.2}; client.publish('thaitechzone/v2_board/sensor/data', json.dumps(data)); print('✅ ส่งข้อมูล sensor สำเร็จ!'); print(f'   Topic: thaitechzone/v2_board/sensor/data'); print(f'   Data: {json.dumps(data)}'); client.disconnect()"

if errorlevel 1 (
    echo [ERROR] ส่งข้อมูลไม่สำเร็จ!
) else (
    echo.
    echo ========================================
    echo   ✓ ส่งข้อมูลทดสอบสำเร็จ
    echo ========================================
    echo.
    echo 📌 ตรวจสอบที่:
    echo    1. Terminal ที่รัน start_mqtt.bat
    echo    2. หรือ Dashboard: http://127.0.0.1:8000/
    echo.
)

pause
