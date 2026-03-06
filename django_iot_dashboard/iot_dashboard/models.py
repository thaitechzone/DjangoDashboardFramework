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
        verbose_name = "Output Monitor"
        verbose_name_plural = "Output Monitoring"
    
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


class RelayLog(models.Model):
    """บันทึกประวัติการเปลี่ยนแปลงสถานะ RELAY ทุกครั้ง"""

    SOURCE_CHOICES = [
        ('mqtt',      'ESP32 (MQTT feedback)'),
        ('ai_agent',  'AI Agent'),
        ('threshold', 'Threshold Auto-control'),
        ('manual',    'Manual (Admin)'),
    ]

    relay_number = models.IntegerField(
        choices=[(1, 'RELAY 1'), (2, 'RELAY 2'), (3, 'RELAY 3')],
        verbose_name='Relay'
    )
    new_state    = models.BooleanField(verbose_name='สถานะใหม่')
    previous_state = models.BooleanField(null=True, blank=True, verbose_name='สถานะเดิม')
    source       = models.CharField(max_length=20, choices=SOURCE_CHOICES,
                                    default='mqtt', verbose_name='แหล่งที่สั่ง')
    reason       = models.TextField(blank=True, verbose_name='เหตุผล')
    timestamp    = models.DateTimeField(default=timezone.now, verbose_name='เวลา', db_index=True)

    class Meta:
        verbose_name = 'Relay Log'
        verbose_name_plural = 'Relay Logs'
        ordering = ['-timestamp']

    def __str__(self):
        state = 'ON' if self.new_state else 'OFF'
        return f"[{self.get_source_display()}] RELAY {self.relay_number} → {state} @ {self.timestamp:%d/%m/%Y %H:%M:%S}"

    @classmethod
    def record(cls, relay_number, new_state, previous_state=None, source='mqtt', reason=''):
        """Helper สร้าง log entry"""
        cls.objects.create(
            relay_number=relay_number,
            new_state=new_state,
            previous_state=previous_state,
            source=source,
            reason=reason,
        )


class RelaySettings(models.Model):
    """การตั้งค่าชื่อ Output ของ ESP32 (singleton — มีแค่ 1 record)"""
    relay1_name = models.CharField(max_length=50, default='RELAY 1', verbose_name='ชื่อ RELAY 1')
    relay2_name = models.CharField(max_length=50, default='RELAY 2', verbose_name='ชื่อ RELAY 2')
    relay3_name = models.CharField(max_length=50, default='RELAY 3', verbose_name='ชื่อ RELAY 3')
    led_name    = models.CharField(max_length=50, default='Onboard LED', verbose_name='ชื่อ LED')

    class Meta:
        verbose_name = 'Output Settings'
        verbose_name_plural = 'Output Settings'

    def __str__(self):
        return f'{self.relay1_name} / {self.relay2_name} / {self.relay3_name}'

    def save(self, *args, **kwargs):
        """Singleton: ไม่ให้สร้าง record ใหม่ถ้ามีอยู่แล้ว"""
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class WeatherAPISettings(models.Model):
    """การตั้งค่า OpenWeatherMap API (singleton — มีแค่ 1 record)"""
    UNITS_CHOICES = [
        ('metric',   'Metric (°C, m/s)'),
        ('imperial', 'Imperial (°F, mph)'),
    ]

    api_key    = models.CharField(
        max_length=100, blank=True, default='',
        verbose_name='API Key',
        help_text='OpenWeatherMap API Key — ดูได้จาก https://openweathermap.org/api'
    )
    location   = models.CharField(
        max_length=100, default='Nakhon Si Thammarat,TH',
        verbose_name='Location',
        help_text='รูปแบบ: "ชื่อเมือง,รหัสประเทศ" เช่น Bangkok,TH หรือ London,GB'
    )
    units      = models.CharField(
        max_length=10, choices=UNITS_CHOICES, default='metric',
        verbose_name='หน่วย'
    )
    is_enabled = models.BooleanField(
        default=True,
        verbose_name='เปิดใช้งาน Weather API',
        help_text='ปิดเพื่อหยุดดึงข้อมูลอากาศ (AI Agent จะทำงานโดยไม่ใช้ข้อมูลอากาศ)'
    )
    last_tested    = models.DateTimeField(null=True, blank=True, verbose_name='ทดสอบล่าสุด')
    last_test_ok   = models.BooleanField(null=True, blank=True, verbose_name='ผลทดสอบล่าสุด')
    last_test_msg  = models.CharField(max_length=200, blank=True, verbose_name='ข้อความผลทดสอบ')

    class Meta:
        verbose_name = 'Weather API Settings'
        verbose_name_plural = 'Weather API Settings'

    def __str__(self):
        status = '✅ เปิด' if self.is_enabled else '❌ ปิด'
        return f'OpenWeather: {self.location} [{status}]'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(pk=1, defaults={
            'api_key': '',
            'location': 'Nakhon Si Thammarat,TH',
        })
        return obj

    def masked_key(self):
        """แสดง API key แบบ mask เพื่อความปลอดภัย"""
        if not self.api_key:
            return '(ยังไม่ได้ตั้งค่า)'
        return self.api_key[:6] + '••••••••••••••••••••' + self.api_key[-4:]


class GeminiAISettings(models.Model):
    """การตั้งค่า Google Gemini AI (singleton — มีแค่ 1 record)"""

    api_key = models.CharField(
        max_length=200, blank=True, default='',
        verbose_name='Gemini API Key',
        help_text='Google Gemini API Key — ดูได้จาก https://makersuite.google.com/app/apikey'
    )
    model_name = models.CharField(
        max_length=100, default='gemini-2.0-flash',
        verbose_name='Model Name',
        help_text='ชื่อ model เช่น gemini-2.0-flash, gemini-1.5-pro'
    )
    interval_minutes = models.PositiveIntegerField(
        default=60,
        verbose_name='รอบการวิเคราะห์ (นาที)',
        help_text='AI Agent จะวิเคราะห์และตัดสินใจทุกกี่นาที (ค่าน้อย = บ่อยขึ้น = ใช้ quota เร็วขึ้น)'
    )
    is_enabled = models.BooleanField(
        default=True,
        verbose_name='เปิดใช้งาน AI Agent',
        help_text='ปิดเพื่อหยุด AI Agent ไม่ให้ส่งคำสั่งควบคุม Relay'
    )
    last_tested   = models.DateTimeField(null=True, blank=True, verbose_name='ทดสอบล่าสุด')
    last_test_ok  = models.BooleanField(null=True, blank=True, verbose_name='ผลทดสอบล่าสุด')
    last_test_msg = models.CharField(max_length=500, blank=True, verbose_name='ข้อความผลทดสอบ')

    class Meta:
        verbose_name = 'Gemini AI Settings'
        verbose_name_plural = 'Gemini AI Settings'

    def __str__(self):
        status = '✅ เปิด' if self.is_enabled else '❌ ปิด'
        return f'Gemini AI: {self.model_name} | {self.interval_minutes} นาที [{status}]'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(pk=1, defaults={
            'api_key': '',
            'model_name': 'gemini-2.0-flash',
            'interval_minutes': 60,
        })
        return obj

    def masked_key(self):
        if not self.api_key:
            return '(ยังไม่ได้ตั้งค่า)'
        return self.api_key[:6] + '••••••••••••••••••••' + self.api_key[-4:]


class SensorData(models.Model):
    device_name = models.CharField(max_length=100, default="ESP32_DHT22")
    temperature = models.FloatField(null=True, blank=True)
    humidity = models.FloatField(null=True, blank=True)
    ds18b20_temperature = models.FloatField(null=True, blank=True, verbose_name="DS18B20 (°C)")
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


class DeviceConfig(models.Model):
    """
    Model สำหรับเก็บค่า Device Identity
    ใช้ Singleton pattern (id=1 เสมอ)
    ผู้ใช้สามารถเปลี่ยน device_name เพื่อป้องกัน MQTT Topic ซ้ำกัน
    """
    device_name = models.CharField(
        max_length=50,
        default="tti_board_001",
        verbose_name="Device Name (DEVICE_ID)",
        help_text="ชื่อบอร์ดที่ตั้งใน #define DEVICE_NAME ของ firmware เช่น tti_board_001"
    )
    mqtt_broker = models.CharField(
        max_length=100,
        default="broker.hivemq.com",
        verbose_name="MQTT Broker"
    )
    mqtt_port = models.IntegerField(
        default=1883,
        verbose_name="MQTT Port"
    )
    mqtt_client_id_prefix = models.CharField(
        max_length=50,
        default="ThaiTechZone",
        verbose_name="MQTT Client ID Prefix",
        help_text="Prefix สำหรับ MQTT Client ID เช่น ThaiTechZone → ThaiTechZone_tti_board_001"
    )
    # DS18B20 latest value cache
    ds18b20_temperature = models.FloatField(
        null=True, blank=True,
        verbose_name='DS18B20 Temperature (°C)',
        help_text='ค่าล่าสุดจาก DS18B20 sensor ที่รับผ่าน MQTT'
    )
    ds18b20_updated_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name='DS18B20 Last Updated'
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Device Configuration"
        verbose_name_plural = "Device Configurations"

    def __str__(self):
        return f"Device: {self.device_name} @ {self.mqtt_broker}:{self.mqtt_port}"

    @classmethod
    def get_config(cls):
        """ดึง config (Singleton id=1)"""
        obj, _ = cls.objects.get_or_create(
            id=1,
            defaults={
                'device_name': 'tti_board_001',
                'mqtt_broker': 'broker.hivemq.com',
                'mqtt_port': 1883,
                'mqtt_client_id_prefix': 'ThaiTechZone',
            }
        )
        return obj

    def get_base_topic(self):
        return f"thaitechzone/v2/{self.device_name}"

    # ─── Topic helpers (ตรงตาม mqtt_topic_id.md) ────────────────────────────

    def led_control_topic(self):
        return f"{self.get_base_topic()}/control/led"

    def led_state_topic(self):
        return f"{self.get_base_topic()}/state/led"

    def relay_control_topic(self, relay_num):
        return f"{self.get_base_topic()}/control/relay{relay_num}"

    def relay_state_topic(self, relay_num):
        return f"{self.get_base_topic()}/state/relay{relay_num}"

    def sensor_data_topic(self):
        return f"{self.get_base_topic()}/sensor/data"

    def temperature_topic(self):
        return f"{self.get_base_topic()}/sensor/temperature"

    def humidity_topic(self):
        return f"{self.get_base_topic()}/sensor/humidity"

    def isolate_in_topic(self, port_num):
        return f"{self.get_base_topic()}/state/isolate_in{port_num}"

    def ds18b20_topic(self):
        return f"{self.get_base_topic()}/sensor/ds18b20"

    def get_all_topics_display(self):
        """คืน dict ของ topics ทั้งหมดเพื่อแสดงใน UI"""
        return {
            'base': self.get_base_topic(),
            'led_control': self.led_control_topic(),
            'led_state': self.led_state_topic(),
            'relay1_control': self.relay_control_topic(1),
            'relay2_control': self.relay_control_topic(2),
            'relay3_control': self.relay_control_topic(3),
            'relay1_state': self.relay_state_topic(1),
            'relay2_state': self.relay_state_topic(2),
            'relay3_state': self.relay_state_topic(3),
            'sensor_data': self.sensor_data_topic(),
            'temperature': self.temperature_topic(),
            'humidity': self.humidity_topic(),
            'ds18b20': self.ds18b20_topic(),
        }


class AIDecisionLog(models.Model):
    """
    Model สำหรับบันทึกการตัดสินใจของ AI Agent
    ใช้เก็บประวัติการควบคุม Relay 2 โดย Gemini AI
    """
    # การตัดสินใจของ AI
    decision = models.CharField(
        max_length=10,
        verbose_name="การตัดสินใจ",
        help_text="on = เปิด, off = ปิด"
    )
    
    # ความมั่นใจในการตัดสินใจ (0.0 - 1.0)
    confidence = models.FloatField(
        default=0.0,
        verbose_name="ความมั่นใจ"
    )
    
    # เหตุผลในการตัดสินใจ (คำอธิบายจาก AI)
    reasoning = models.TextField(
        verbose_name="เหตุผล",
        help_text="คำอธิบายการตัดสินใจจาก AI"
    )
    
    # ข้อมูลสภาพอากาศที่ใช้ตัดสินใจ (เก็บเป็น JSON)
    weather_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="ข้อมูลสภาพอากาศ"
    )
    
    # สถานะ Relay 2 หลังตัดสินใจ
    relay_status = models.BooleanField(
        default=False,
        verbose_name="สถานะ Relay 2"
    )
    
    # คำสั่งถูกส่งสำเร็จหรือไม่
    command_sent = models.BooleanField(
        default=False,
        verbose_name="ส่งคำสั่งสำเร็จ"
    )
    
    # เวลาที่บันทึก
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="เวลาที่บันทึก"
    )
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "AI Decision Log"
        verbose_name_plural = "AI Decision Logs"
    
    def __str__(self):
        return f"{self.timestamp.strftime('%d/%m/%Y %H:%M')} - {self.decision.upper()} - Confidence: {self.confidence:.2f}"
    
    def get_decision_display_thai(self):
        """แสดงการตัดสินใจเป็นภาษาไทยพร้อม icon"""
        if self.decision == 'on':
            return "🟢 เปิด Relay 2 (ON)"
        else:
            return "⚫ ปิด Relay 2 (OFF)"
    
    def get_confidence_display(self):
        """แสดงความมั่นใจเป็น %"""
        return f"{self.confidence * 100:.1f}%"
    
    def get_timestamp_thai(self):
        """แสดงเวลาในรูปแบบภาษาไทย"""
        if self.timestamp:
            return self.timestamp.strftime("%d/%m/%Y %H:%M:%S")
        return "ไม่มีข้อมูล"
    
    @classmethod
    def get_recent_decisions(cls, limit=10):
        """ดึงการตัดสินใจล่าสุด"""
        return cls.objects.all()[:limit]
    
    @classmethod
    def get_statistics(cls, days=7):
        """
        สถิติการตัดสินใจของ AI ในช่วง N วันที่ผ่านมา
        
        Returns:
            dict: {
                'total_decisions': int,
                'on_decisions': int,
                'off_decisions': int,
                'avg_confidence': float,
                'daily_breakdown': list
            }
        """
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Count, Avg
        from django.db.models.functions import TruncDate
        
        start_date = timezone.now() - timedelta(days=days)
        decisions = cls.objects.filter(timestamp__gte=start_date)
        
        total = decisions.count()
        if total == 0:
            return {
                'total_decisions': 0,
                'on_decisions': 0,
                'off_decisions': 0,
                'avg_confidence': 0.0,
                'daily_breakdown': []
            }
        
        on_decisions = decisions.filter(decision='on').count()
        off_decisions = decisions.filter(decision='off').count()
        avg_confidence = decisions.aggregate(Avg('confidence'))['confidence__avg'] or 0.0
        
        # Daily breakdown
        daily = decisions.annotate(date=TruncDate('timestamp')).values('date').annotate(
            total=Count('id'),
            on_count=Count('id', filter=models.Q(decision='on')),
            off_count=Count('id', filter=models.Q(decision='off')),
            avg_confidence=Avg('confidence')
        ).order_by('date')
        
        daily_breakdown = [
            {
                'date': item['date'].strftime('%Y-%m-%d'),
                'total': item['total'],
                'on_count': item['on_count'],
                'off_count': item['off_count'],
                'avg_confidence': item['avg_confidence'] or 0.0
            }
            for item in daily
        ]
        
        return {
            'total_decisions': total,
            'on_decisions': on_decisions,
            'off_decisions': off_decisions,
            'avg_confidence': avg_confidence,
            'daily_breakdown': daily_breakdown
        }
