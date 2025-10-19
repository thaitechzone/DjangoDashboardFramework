from django.db import models
from django.utils import timezone

class Device(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_on = models.BooleanField(default=False)
    last_updated = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} is {'ON' if self.is_on else 'OFF'}"
    
    def get_status_display(self):
        return "🟢 ON" if self.is_on else "⚫ OFF"
    
    def get_last_updated_thai(self):
        """แสดงเวลาอัพเดทล่าสุดในรูปแบบภาษาไทย"""
        if self.last_updated:
            return self.last_updated.strftime("%d/%m/%Y %H:%M:%S")
        return "ไม่มีข้อมูล"


class SensorData(models.Model):
    device_name = models.CharField(max_length=100, default="ESP32_DHT22")
    temperature = models.FloatField(null=True, blank=True)
    humidity = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"{self.device_name}: {self.temperature}°C, {self.humidity}% - {self.timestamp}"
    
    def get_timestamp_thai(self):
        """แสดงเวลาในรูปแบบภาษาไทย"""
        if self.timestamp:
            return self.timestamp.strftime("%d/%m/%Y %H:%M:%S")
        return "ไม่มีข้อมูล"
    
    def get_temperature_display(self):
        """แสดงอุณหภูมิพร้อม icon"""
        if self.temperature is not None:
            if self.temperature > 30:
                return f"🔥 {self.temperature:.1f}°C"
            elif self.temperature < 20:
                return f"❄️ {self.temperature:.1f}°C"
            else:
                return f"🌡️ {self.temperature:.1f}°C"
        return "📊 ไม่มีข้อมูล"
    
    def get_humidity_display(self):
        """แสดงความชื้นพร้อม icon"""
        if self.humidity is not None:
            if self.humidity > 70:
                return f"💧 {self.humidity:.1f}%"
            elif self.humidity < 30:
                return f"🏜️ {self.humidity:.1f}%"
            else:
                return f"💨 {self.humidity:.1f}%"
        return "📊 ไม่มีข้อมูล"
