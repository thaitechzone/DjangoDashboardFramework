@echo off
REM ============================================
REM  Docker Logs - Django IoT Dashboard
REM ============================================

echo.
echo ========================================
echo   Django IoT Dashboard - Logs
echo ========================================
echo.
echo กด Ctrl+C เพื่อหยุดดู logs
echo.

docker-compose logs -f

pause
