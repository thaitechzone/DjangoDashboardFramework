@echo off
chcp 65001 > nul
echo ========================================
echo 🔍 ทดสอบสถานะ Relay 2
echo ========================================
echo.

echo 1. ตรวจสอบสถานะจาก AI Status API:
echo.
curl -s http://localhost:8000/api/v1/ai/status/ | findstr "relay2_current_status"
echo.

echo ========================================
echo 2. ตรวจสอบสถานะจาก Relay API:
echo.
curl -s http://localhost:8000/api/v1/relay/ | findstr "relay2_status"
echo.

echo ========================================
echo 3. ทดสอบการเปลี่ยนสถานะ:
echo.
echo กรุณาทดสอบด้วยตัวเอง:
echo - เปิด Main Dashboard: http://localhost:8000/
echo - สั่ง Relay 2 ON หรือ OFF
echo - Refresh AI Dashboard: http://localhost:8000/ai/
echo - ตรวจสอบว่าสถานะ Relay 2 เปลี่ยนตามหรือไม่
echo.

pause
