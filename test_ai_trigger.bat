@echo off
chcp 65001 > nul
echo ========================================
echo 🤖 AI Agent Manual Trigger Test
echo ========================================
echo.

echo กำลังสั่งให้ AI วิเคราะห์และควบคุม Relay 2...
echo.

curl -X POST http://localhost:8000/api/v1/ai/analyze-now/ -H "Content-Type: application/json"

echo.
echo.
echo ========================================
echo ✅ เสร็จสิ้น!
echo ========================================
echo.
echo ตรวจสอบผลลัพธ์:
echo 1. เปิด AI Dashboard: http://localhost:8000/ai/
echo 2. ดูสถานะ Relay 2 และการตัดสินใจล่าสุด
echo.
pause
