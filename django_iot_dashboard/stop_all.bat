@echo off
REM ============================================
REM  Django IoT Dashboard - Stop All Services
REM  หยุดทุก process ที่เกี่ยวข้อง
REM ============================================

echo.
echo ================================================
echo   Django IoT Dashboard - Stopping Services
echo ================================================
echo.

echo [1/2] กำลังหยุด Django Server (port 8000)...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do (
    echo [INFO] พบ process ID: %%a
    taskkill /F /PID %%a >nul 2>&1
    if errorlevel 1 (
        echo [WARNING] ไม่สามารถหยุด process %%a
    ) else (
        echo [OK] หยุด Django Server แล้ว (PID: %%a)
    )
)

echo.
echo [2/2] กำลังหยุด Python processes ที่เกี่ยวข้อง...
tasklist | find /I "python.exe" >nul
if errorlevel 1 (
    echo [INFO] ไม่พบ Python processes
) else (
    echo [WARNING] พบ Python processes กำลังทำงาน
    echo [INFO] กรุณาปิด windows ที่เปิดค้างไว้เอง
    echo       หรือใช้ Task Manager หยุด manual
)

echo.
echo ================================================
echo   ✓ เสร็จสิ้น
echo ================================================
echo.

pause
