@echo off
REM ============================================
REM  Django IoT Dashboard - Start Server
REM  ไฟล์สำหรับรัน Django Web Server
REM ============================================

echo.
echo ========================================
echo   Django IoT Dashboard - Web Server
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
echo [1/3] กำลังเปิดใช้งาน Virtual Environment...
call venv\Scripts\activate.bat

REM ตรวจสอบว่า Django ติดตั้งแล้วหรือไม่
python -c "import django" 2>nul
if errorlevel 1 (
    echo.
    echo [WARNING] ไม่พบ Django!
    echo กำลังติดตั้ง dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] ติดตั้ง dependencies ไม่สำเร็จ!
        pause
        exit /b 1
    )
)

echo [2/3] ตรวจสอบฐานข้อมูล...
if not exist "db.sqlite3" (
    echo [INFO] กำลังสร้างฐานข้อมูล...
    python manage.py migrate
)

echo [3/3] กำลังเริ่มต้น Django Server...
echo.
echo ========================================
echo   Server กำลังทำงานที่:
echo   http://127.0.0.1:8000/
echo   http://localhost:8000/
echo ========================================
echo.
echo กด Ctrl+C เพื่อหยุด Server
echo.

REM รัน Django server
python manage.py runserver

pause
