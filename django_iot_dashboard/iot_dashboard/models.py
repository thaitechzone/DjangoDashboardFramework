from django.db import models
from django.utils import timezone
from django.db.models import Avg

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


class Relay(models.Model):
    """Model สำหรับควบคุม RELAY 3 ตัว"""
    name = models.CharField(max_length=100, default="Relay Control")
    relay1_status = models.BooleanField(default=False, verbose_name="RELAY 1")
    relay2_status = models.BooleanField(default=False, verbose_name="RELAY 2")
    relay3_status = models.BooleanField(default=False, verbose_name="RELAY 3")
    last_updated = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = "Relay Controller"
        verbose_name_plural = "Relay Controllers"
    
    def __str__(self):
        return f"{self.name} - R1:{'ON' if self.relay1_status else 'OFF'} R2:{'ON' if self.relay2_status else 'OFF'} R3:{'ON' if self.relay3_status else 'OFF'}"
    
    def get_relay1_display(self):
        return "🟢 ON" if self.relay1_status else "⚫ OFF"
    
    def get_relay2_display(self):
        return "🟢 ON" if self.relay2_status else "⚫ OFF"
    
    def get_relay3_display(self):
        return "🟢 ON" if self.relay3_status else "⚫ OFF"
    
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


class ThresholdSetting(models.Model):
    """
    Model สำหรับเก็บค่า Threshold การแจ้งเตือน Temperature และ Humidity
    รองรับโหมด AUTO (ควบคุม Relay อัตโนมัติ) และ MANUAL (ควบคุมด้วยมือ)
    """
    MODE_CHOICES = [
        ('AUTO', 'Auto - ควบคุมอัตโนมัติ'),
        ('MANUAL', 'Manual - ควบคุมด้วยมือ'),
    ]
    
    # ค่า Threshold สำหรับอุณหภูมิ (Temperature)
    temperature_high = models.FloatField(
        default=35.0,
        verbose_name="อุณหภูมิสูงสุด (°C)",
        help_text="เมื่ออุณหภูมิเกินค่านี้จะเปิด Relay 1"
    )
    temperature_low = models.FloatField(
        default=20.0,
        verbose_name="อุณหภูมิต่ำสุด (°C)",
        help_text="เมื่ออุณหภูมิต่ำกว่าค่านี้จะเปิด Relay 1"
    )
    
    # ค่า Threshold สำหรับความชื้น (Humidity)
    humidity_high = models.FloatField(
        default=80.0,
        verbose_name="ความชื้นสูงสุด (%)",
        help_text="เมื่อความชื้นเกินค่านี้จะเปิด Relay 1"
    )
    humidity_low = models.FloatField(
        default=30.0,
        verbose_name="ความชื้นต่ำสุด (%)",
        help_text="เมื่อความชื้นต่ำกว่าค่านี้จะเปิด Relay 1"
    )
    
    # โหมดการทำงาน
    mode = models.CharField(
        max_length=10,
        choices=MODE_CHOICES,
        default='MANUAL',
        verbose_name="โหมดควบคุม"
    )
    
    # เปิด/ปิดการควบคุม Relay 1 อัตโนมัติ
    relay1_auto_enabled = models.BooleanField(
        default=True,
        verbose_name="เปิดใช้งาน Relay 1 อัตโนมัติ"
    )
    
    # สถานะการแจ้งเตือน
    alarm_active = models.BooleanField(
        default=False,
        verbose_name="สถานะ Alarm",
        help_text="True = กำลังแจ้งเตือน (Relay 1 เปิด), False = ปกติ"
    )
    
    # เวลาที่ Alarm ถูกเปิดใช้งานล่าสุด
    last_triggered = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="เวลาแจ้งเตือนล่าสุด"
    )
    
    # บันทึกเหตุผลที่ Alarm เปิด
    alarm_reason = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="สาเหตุการแจ้งเตือน"
    )
    
    # Hysteresis (ช่วงความแตกต่างเพื่อป้องกันการเปิด-ปิดบ่อยเกินไป)
    hysteresis_percentage = models.FloatField(
        default=2.0,
        verbose_name="Hysteresis (%)",
        help_text="ช่วงความแตกต่างกลับคืนสู่สถานะปกติ (ป้องกันการสั่นของ Relay)"
    )
    
    # จำนวน readings ที่ใช้คำนวณค่าเฉลี่ย
    average_window = models.IntegerField(
        default=10,
        verbose_name="จำนวน Readings สำหรับค่าเฉลี่ย",
        help_text="จำนวนข้อมูลล่าสุดที่ใช้คำนวณค่าเฉลี่ย"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Threshold Setting"
        verbose_name_plural = "Threshold Settings"
    
    def __str__(self):
        return f"Threshold [{self.mode}] - Temp: {self.temperature_low}~{self.temperature_high}°C, Hum: {self.humidity_low}~{self.humidity_high}%"
    
    def get_mode_display_thai(self):
        """แสดงโหมดเป็นภาษาไทยพร้อม icon"""
        if self.mode == 'AUTO':
            return "🤖 AUTO - ควบคุมอัตโนมัติ"
        else:
            return "👤 MANUAL - ควบคุมด้วยมือ"
    
    def get_alarm_status_display(self):
        """แสดงสถานะ Alarm พร้อม icon"""
        if self.alarm_active:
            return "🚨 กำลังแจ้งเตือน (Alarm Active)"
        else:
            return "✅ ปกติ (Normal)"
    
    def get_current_averages(self):
        """
        คำนวณค่าเฉลี่ย Temperature และ Humidity จากข้อมูลล่าสุด
        ใช้จำนวน readings ตาม average_window
        """
        recent_data = SensorData.objects.all()[:self.average_window]
        
        if not recent_data.exists():
            return None, None
        
        avg_temp = recent_data.aggregate(Avg('temperature'))['temperature__avg']
        avg_humidity = recent_data.aggregate(Avg('humidity'))['humidity__avg']
        
        return avg_temp, avg_humidity
    
    def check_threshold(self, sensor_data):
        """
        ตรวจสอบว่า sensor_data ที่รับเข้ามาเกิน Threshold หรือไม่
        
        Parameters:
            sensor_data: instance ของ SensorData
        
        Returns:
            dict: {
                'should_trigger': bool,
                'reason': str,
                'temperature': float,
                'humidity': float,
                'avg_temperature': float,
                'avg_humidity': float
            }
        """
        # คำนวณค่าเฉลี่ย
        avg_temp, avg_humidity = self.get_current_averages()
        
        # ถ้าไม่มีข้อมูลเฉลี่ย ใช้ค่าปัจจุบันแทน
        if avg_temp is None:
            avg_temp = sensor_data.temperature
        if avg_humidity is None:
            avg_humidity = sensor_data.humidity
        
        reasons = []
        should_trigger = False
        
        # ตรวจสอบอุณหภูมิ
        if sensor_data.temperature is not None:
            if sensor_data.temperature > self.temperature_high:
                reasons.append(f"🌡️ อุณหภูมิสูง: {sensor_data.temperature:.1f}°C > {self.temperature_high}°C")
                should_trigger = True
            elif sensor_data.temperature < self.temperature_low:
                reasons.append(f"❄️ อุณหภูมิต่ำ: {sensor_data.temperature:.1f}°C < {self.temperature_low}°C")
                should_trigger = True
        
        # ตรวจสอบความชื้น
        if sensor_data.humidity is not None:
            if sensor_data.humidity > self.humidity_high:
                reasons.append(f"💧 ความชื้นสูง: {sensor_data.humidity:.1f}% > {self.humidity_high}%")
                should_trigger = True
            elif sensor_data.humidity < self.humidity_low:
                reasons.append(f"🏜️ ความชื้นต่ำ: {sensor_data.humidity:.1f}% < {self.humidity_low}%")
                should_trigger = True
        
        # ตรวจสอบ Hysteresis (ป้องกันการเปิด-ปิดบ่อย)
        if self.alarm_active and should_trigger:
            # ถ้า Alarm เปิดอยู่แล้ว ต้องตรวจสอบว่าค่ากลับมาปกติหรือยัง (ต้องต่ำกว่า threshold - hysteresis)
            hysteresis_temp_high = self.temperature_high - (self.temperature_high * self.hysteresis_percentage / 100)
            hysteresis_temp_low = self.temperature_low + (self.temperature_low * self.hysteresis_percentage / 100)
            hysteresis_hum_high = self.humidity_high - (self.humidity_high * self.hysteresis_percentage / 100)
            hysteresis_hum_low = self.humidity_low + (self.humidity_low * self.hysteresis_percentage / 100)
            
            # ตรวจสอบว่าค่ากลับมาอยู่ในช่วงปกติหรือไม่
            temp_ok = hysteresis_temp_low <= sensor_data.temperature <= hysteresis_temp_high
            hum_ok = hysteresis_hum_low <= sensor_data.humidity <= hysteresis_hum_high
            
            if temp_ok and hum_ok:
                should_trigger = False
                reasons = ["✅ ค่ากลับสู่สภาวะปกติ (Hysteresis)"]
        
        return {
            'should_trigger': should_trigger,
            'reason': ' | '.join(reasons) if reasons else 'ปกติ',
            'temperature': sensor_data.temperature,
            'humidity': sensor_data.humidity,
            'avg_temperature': avg_temp,
            'avg_humidity': avg_humidity
        }
    
    def should_activate_alarm(self, sensor_data):
        """
        ตรวจสอบว่าควรเปิด Alarm หรือไม่
        (ใช้เฉพาะเมื่อ mode = AUTO และ relay1_auto_enabled = True)
        
        Parameters:
            sensor_data: instance ของ SensorData
        
        Returns:
            bool: True = ควรเปิด Relay 1, False = ไม่ต้องเปิด
        """
        if self.mode != 'AUTO':
            return False
        
        if not self.relay1_auto_enabled:
            return False
        
        result = self.check_threshold(sensor_data)
        return result['should_trigger']
    
    def activate_alarm(self, reason=""):
        """
        เปิด Alarm (บันทึกสถานะ)
        """
        self.alarm_active = True
        self.last_triggered = timezone.now()
        self.alarm_reason = reason
        self.save()
    
    def deactivate_alarm(self):
        """
        ปิด Alarm (บันทึกสถานะ)
        """
        self.alarm_active = False
        self.alarm_reason = ""
        self.save()
    
    @classmethod
    def get_or_create_default(cls):
        """
        สร้างหรือดึง ThresholdSetting แบบ Singleton
        (ควรมีแค่ 1 instance เท่านั้น)
        """
        obj, created = cls.objects.get_or_create(
            id=1,
            defaults={
                'temperature_high': 35.0,
                'temperature_low': 20.0,
                'humidity_high': 80.0,
                'humidity_low': 30.0,
                'mode': 'MANUAL',
                'relay1_auto_enabled': True,
                'alarm_active': False,
            }
        )
        return obj
