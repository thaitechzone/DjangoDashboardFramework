@echo off
REM ============================================
REM  Docker Quick Start - Django IoT Dashboard
REM  สำหรับ Windows
REM ============================================

echo.
echo ========================================
echo   Django IoT Dashboard - Docker Mode
echo ========================================
echo.

REM ตรวจสอบว่า Docker Desktop ทำงานหรือไม่
echo [1/3] ตรวจสอบ Docker Desktop...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] ไม่พบ Docker!
    echo.
    echo กรุณาติดตั้ง Docker Desktop:
    echo https://www.docker.com/products/docker-desktop/
    echo.
    pause
    exit /b 1
)

docker ps >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Desktop ไม่ทำงาน!
    echo.
    echo กรุณาเปิด Docker Desktop แล้วรอจนกว่าจะพร้อม
    echo (สัญลักษณ์ Docker สีเขียว)
    echo.
    pause
    exit /b 1
)

echo [OK] Docker Desktop พร้อมใช้งาน
echo.

REM Build และ Run
echo [2/3] กำลัง Build Docker Image...
echo (อาจใช้เวลา 2-3 นาทีในครั้งแรก)
echo.
docker-compose up --build -d

if errorlevel 1 (
    echo [ERROR] Build ไม่สำเร็จ!
    pause
    exit /b 1
)

echo.
echo [3/3] กำลังรอ Server เริ่มต้น...
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo   ✓ Django IoT Dashboard พร้อมแล้ว!
echo ========================================
echo.
echo 📌 เปิด Web Browser ไปที่:
echo    http://localhost:8000/
echo    http://127.0.0.1:8000/
echo.
echo 📌 ดู Logs:
echo    docker-compose logs -f
echo.
echo 📌 หยุดระบบ:
echo    docker-compose down
echo.
echo 📌 Restart:
echo    docker-compose restart
echo.

REM เปิด browser อัตโนมัติ
timeout /t 2 /nobreak >nul
start http://localhost:8000/

pause
