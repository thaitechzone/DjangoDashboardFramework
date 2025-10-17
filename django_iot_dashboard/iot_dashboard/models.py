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
