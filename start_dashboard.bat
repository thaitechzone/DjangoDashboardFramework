@echo off
echo 🚀 Starting Django IoT Dashboard Server...
echo ==========================================

cd /d "D:\GitHub\DjangoDashboardFramework\django_iot_dashboard"

echo 📁 Current directory: %CD%
echo 📊 Checking database status...
python manage.py showmigrations --verbosity=0

echo.
echo 🌟 Starting development server...
echo 📍 URL: http://127.0.0.1:8000/
echo 💡 Press Ctrl+C to stop the server
echo.

python manage.py runserver

pause