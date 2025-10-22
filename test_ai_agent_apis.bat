@echo off
REM ===================================
REM AI Agent API Testing Script
REM ===================================

echo.
echo ===================================
echo  AI Agent API Testing
echo ===================================
echo.

set BASE_URL=http://localhost:8000

echo [1/5] Testing AI Agent Status...
echo ===================================
curl -s %BASE_URL%/api/v1/ai/status/ | findstr /i "success is_running"
if %ERRORLEVEL% EQU 0 (
    echo [OK] AI Agent Status API
) else (
    echo [FAIL] AI Agent Status API
)
echo.

echo [2/5] Triggering Manual AI Analysis...
echo ===================================
curl -s -X POST %BASE_URL%/api/v1/ai/analyze-now/ | findstr /i "success decision"
if %ERRORLEVEL% EQU 0 (
    echo [OK] Manual Trigger API
) else (
    echo [FAIL] Manual Trigger API
)
echo.

echo [3/5] Getting AI Statistics (7 days)...
echo ===================================
curl -s "%BASE_URL%/api/v1/ai/stats/?days=7" | findstr /i "total_decisions avg_confidence"
if %ERRORLEVEL% EQU 0 (
    echo [OK] Statistics API
) else (
    echo [FAIL] Statistics API
)
echo.

echo [4/5] Getting Decision History...
echo ===================================
curl -s "%BASE_URL%/api/v1/ai/decisions/?limit=5&offset=0" | findstr /i "pagination data"
if %ERRORLEVEL% EQU 0 (
    echo [OK] Decision History API
) else (
    echo [FAIL] Decision History API
)
echo.

echo [5/5] Getting System Status...
echo ===================================
curl -s %BASE_URL%/api/v1/system/status/ | findstr /i "relays mqtt"
if %ERRORLEVEL% EQU 0 (
    echo [OK] System Status API
) else (
    echo [FAIL] System Status API
)
echo.

echo ===================================
echo  All Tests Completed!
echo ===================================
echo.
pause
