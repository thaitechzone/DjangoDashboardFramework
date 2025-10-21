@echo off
REM ============================================
REM  Docker Stop - Django IoT Dashboard
REM ============================================

echo.
echo ========================================
echo   หยุด Django IoT Dashboard
echo ========================================
echo.

echo กำลังหยุด containers...
docker-compose down

if errorlevel 1 (
    echo [ERROR] หยุดไม่สำเร็จ!
) else (
    echo.
    echo ========================================
    echo   ✓ หยุดเรียบร้อยแล้ว
    echo ========================================
    echo.
    echo คำสั่งอื่นๆ:
    echo   docker-compose up -d     : เริ่มใหม่
    echo   docker-compose ps        : ดูสถานะ
    echo   docker-compose logs -f   : ดู logs
    echo.
)

pause
