@echo off
REM ============================================
REM  Django IoT Dashboard - Setup Script
REM  ติดตั้งและตั้งค่าระบบครั้งแรก
REM ============================================

echo.
echo ================================================
echo   Django IoT Dashboard - Setup Wizard
echo ================================================
echo.

REM ตรวจสอบ Python
echo [1/6] ตรวจสอบ Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] ไม่พบ Python!
    echo กรุณาติดตั้ง Python 3.8 หรือสูงกว่า
    echo ดาวน์โหลดได้ที่: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

python --version
echo [OK] พบ Python แล้ว
echo.

REM สร้าง Virtual Environment
echo [2/6] สร้าง Virtual Environment...
if exist "venv" (
    echo [INFO] พบ Virtual Environment อยู่แล้ว
) else (
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] สร้าง Virtual Environment ไม่สำเร็จ!
        pause
        exit /b 1
    )
    echo [OK] สร้าง Virtual Environment สำเร็จ
)
echo.

REM เปิดใช้งาน Virtual Environment
echo [3/6] เปิดใช้งาน Virtual Environment...
call venv\Scripts\activate.bat
echo [OK] เปิดใช้งาน Virtual Environment แล้ว
echo.

REM ติดตั้ง Dependencies
echo [4/6] ติดตั้ง Python Packages...
if exist "requirements.txt" (
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] ติดตั้ง packages ไม่สำเร็จ!
        pause
        exit /b 1
    )
    echo [OK] ติดตั้ง packages สำเร็จ
) else (
    echo [INFO] ไม่พบ requirements.txt กำลังติดตั้งแบบ manual...
    pip install django==5.2.7
    pip install paho-mqtt==2.1.0
)
echo.

REM สร้างฐานข้อมูล
echo [5/6] สร้างฐานข้อมูล...
if exist "db.sqlite3" (
    echo [INFO] พบฐานข้อมูลอยู่แล้ว
    choice /C YN /M "ต้องการสร้างใหม่หรือไม่ (ข้อมูลเดิมจะหาย)"
    if errorlevel 2 goto skip_db
    if errorlevel 1 (
        del db.sqlite3
        echo [INFO] ลบฐานข้อมูลเดิมแล้ว
    )
)

echo [INFO] กำลังสร้างฐานข้อมูล...
python manage.py makemigrations
python manage.py migrate

if errorlevel 1 (
    echo [WARNING] พบปัญหาในการสร้างฐานข้อมูล
    echo [INFO] จะข้ามขั้นตอนนี้ไป
) else (
    echo [OK] สร้างฐานข้อมูลสำเร็จ
)

:skip_db
echo.

REM สร้าง Superuser (Optional)
echo [6/6] สร้าง Admin User (Optional)...
choice /C YN /M "ต้องการสร้าง Admin User หรือไม่"
if errorlevel 2 goto skip_superuser
if errorlevel 1 (
    echo.
    echo กรุณากรอกข้อมูล Admin:
    python manage.py createsuperuser
    echo.
)

:skip_superuser

REM สรุปผลการติดตั้ง
echo.
echo ================================================
echo   ✓ ติดตั้งเสร็จสมบูรณ์!
echo ================================================
echo.
echo 📌 วิธีรันระบบ:
echo    1. Double Click ที่ start_all.bat
echo    2. เปิด Browser ไปที่ http://127.0.0.1:8000/
echo.
echo 📌 วิธีรัน Server อย่างเดียว:
echo    Double Click ที่ start_server.bat
echo.
echo 📌 Django Admin Panel:
echo    http://127.0.0.1:8000/admin/
echo.
echo 📌 ไฟล์ที่สำคัญ:
echo    - start_all.bat     : รันทุกอย่างพร้อมกัน
echo    - start_server.bat  : รัน Django Server
echo    - start_mqtt.bat    : รัน MQTT Listener
echo    - stop_all.bat      : หยุดทุก process
echo.

pause
