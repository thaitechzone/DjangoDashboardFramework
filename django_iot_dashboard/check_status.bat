@echo off
REM ============================================
REM  Django IoT Dashboard - Check Status
REM  ตรวจสอบสถานะระบบ
REM ============================================

echo.
echo ================================================
echo   Django IoT Dashboard - System Status
echo ================================================
echo.

REM ตรวจสอบ Python
echo [1/5] Python Installation:
python --version 2>nul
if errorlevel 1 (
    echo [✗] Python ไม่ได้ติดตั้ง
) else (
    echo [✓] Python พร้อมใช้งาน
)
echo.

REM ตรวจสอบ Virtual Environment
echo [2/5] Virtual Environment:
if exist "venv\Scripts\activate.bat" (
    echo [✓] Virtual Environment พร้อมใช้งาน
    echo     Path: venv\
) else (
    echo [✗] ไม่พบ Virtual Environment
    echo     กรุณารัน: setup.bat
)
echo.

REM ตรวจสอบ Dependencies
echo [3/5] Python Packages:
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    python -c "import django; print('[✓] Django version:', django.get_version())" 2>nul
    if errorlevel 1 (
        echo [✗] Django ไม่ได้ติดตั้ง
    )
    
    python -c "import paho.mqtt.client; print('[✓] paho-mqtt ติดตั้งแล้ว')" 2>nul
    if errorlevel 1 (
        echo [✗] paho-mqtt ไม่ได้ติดตั้ง
    )
) else (
    echo [!] ข้ามการตรวจสอบ (ไม่มี venv)
)
echo.

REM ตรวจสอบฐานข้อมูล
echo [4/5] Database:
if exist "db.sqlite3" (
    echo [✓] Database พร้อมใช้งาน
    echo     File: db.sqlite3
) else (
    echo [✗] ไม่พบ Database
    echo     กรุณารัน: python manage.py migrate
)
echo.

REM ตรวจสอบ Django Server
echo [5/5] Django Server Status:
netstat -ano | find ":8000" | find "LISTENING" >nul
if errorlevel 1 (
    echo [✗] Django Server ไม่ได้ทำงาน
    echo     รันด้วย: start_server.bat
) else (
    echo [✓] Django Server กำลังทำงาน
    echo     URL: http://127.0.0.1:8000/
    for /f "tokens=5" %%a in ('netstat -ano ^| find ":8000" ^| find "LISTENING"') do (
        echo     PID: %%a
    )
)
echo.

echo ================================================
echo   Summary
echo ================================================
echo.
echo วิธีรันระบบ:
echo   • ครั้งแรก: รัน setup.bat
echo   • รันปกติ: รัน start_all.bat
echo   • หยุดระบบ: รัน stop_all.bat
echo.
echo ดู Dashboard:
echo   http://127.0.0.1:8000/
echo   http://localhost:8000/
echo.

pause
