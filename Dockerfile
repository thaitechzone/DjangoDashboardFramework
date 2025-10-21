# ======================================
# Django IoT Dashboard - Dockerfile
# ======================================
# Base image: Python 3.11 slim
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=dashboard_project.settings

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY django_iot_dashboard/requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY django_iot_dashboard/ .

# Create directories for static and media files
RUN mkdir -p staticfiles media

# Collect static files (if needed in future)
# RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Create entrypoint script
RUN echo '#!/bin/bash\n\
echo "========================================"\n\
echo "  Django IoT Dashboard - Starting..."\n\
echo "========================================"\n\
echo ""\n\
echo "Waiting for database..."\n\
sleep 2\n\
echo ""\n\
echo "Running migrations..."\n\
python manage.py makemigrations --noinput\n\
python manage.py migrate --noinput\n\
echo ""\n\
echo "========================================"\n\
echo "  ✓ Server starting at port 8000"\n\
echo "========================================"\n\
echo ""\n\
echo "📌 Access Dashboard at:"\n\
echo "   http://localhost:8000/"\n\
echo "   http://127.0.0.1:8000/"\n\
echo ""\n\
echo "📌 MQTT Broker:"\n\
echo "   broker.hivemq.com:1883"\n\
echo ""\n\
echo "📌 Stop: Press Ctrl+C or run: docker-compose down"\n\
echo ""\n\
exec python manage.py runserver 0.0.0.0:8000' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Run entrypoint
ENTRYPOINT ["/entrypoint.sh"]
