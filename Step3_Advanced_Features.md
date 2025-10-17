# Django IoT Dashboard - Step 3: Advanced Features

## 🎯 ขั้นตอนการพัฒนาต่อ (หลังจากทดสอบ MQTT สำเร็จแล้ว)

### ✅ สิ่งที่ใช้งานได้แล้ว:
- ✅ Django Web Server ทำงานได้
- ✅ MQTT Listener รับข้อมูลได้
- ✅ Database บันทึกสถานะได้
- ✅ Dashboard แสดงผลได้
- ✅ MQTT Explorer ส่งข้อมูลได้

---

## 🚀 การปรับปรุงต่อไป

### 1. เพิ่ม Auto-Refresh Dashboard
ทำให้หน้าเว็บอัพเดทอัตโนมัติโดยไม่ต้อง refresh ด้วยตนเอง

### 2. เพิ่มการควบคุม LED จากหน้าเว็บ
สร้างปุ่ม ON/OFF บนหน้า Dashboard เพื่อควบคุม LED

### 3. เพิ่ม Device อื่นๆ
- เซนเซอร์อุณหภูมิ
- เซนเซอร์ความชื้น
- ปุ่มกด
- Servo Motor

### 4. เพิ่ม Charts และ Graphs
แสดงข้อมูลในรูปแบบกราฟ

### 5. เพิ่ม Alert System
แจ้งเตือนเมื่อค่าผิดปกติ

---

## 📊 ข้อมูลการทดสอบที่สำเร็จ

### MQTT Topics ที่ใช้งานได้:
- `thaitechzone/v2_board/state/led` → สถานะ LED (ON/OFF)

### Database Records:
- Device: "Onboard LED" 
- Status: เปลี่ยนตาม MQTT message

### Web Interface:
- URL: `http://127.0.0.1:8000/`
- แสดงสถานะ LED แบบ real-time (หลัง refresh)

---

## 🔧 ขั้นตอนถัดไป - Auto-Refresh

### Step 3.1: เพิ่ม Auto-Refresh ใน Template

แก้ไขไฟล์ `dashboard.html` เพื่อเพิ่มการ refresh อัตโนมัติ:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>IoT Dashboard</title>
    <meta http-equiv="refresh" content="2"> <!-- Refresh ทุก 2 วินาที -->
    <style>
        body { font-family: sans-serif; padding: 20px; background-color: #f5f5f5; }
        .dashboard-container { max-width: 1200px; margin: 0 auto; }
        .device { 
            border: 1px solid #ccc; 
            padding: 20px; 
            margin: 10px; 
            border-radius: 12px; 
            width: 250px; 
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            display: inline-block;
            vertical-align: top;
        }
        .status-on { 
            color: #28a745; 
            font-weight: bold; 
            font-size: 18px;
        }
        .status-off { 
            color: #6c757d; 
            font-weight: bold; 
            font-size: 18px;
        }
        .last-updated {
            font-size: 12px;
            color: #6c757d;
            margin-top: 10px;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .led-indicator {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 10px;
        }
        .led-on {
            background-color: #28a745;
            box-shadow: 0 0 10px #28a745;
        }
        .led-off {
            background-color: #6c757d;
        }
    </style>
</head>
<body>
    <div class="dashboard-container">
        <h1>🏠 My IoT Dashboard</h1>

        <div class="device">
            <h2>💡 {{ led.name }}</h2>
            <p>
                <span class="led-indicator {% if led.is_on %}led-on{% else %}led-off{% endif %}"></span>
                Status:
                {% if led.is_on %}
                    <span class="status-on">🟢 ON</span>
                {% else %}
                    <span class="status-off">⚫ OFF</span>
                {% endif %}
            </p>
            <div class="last-updated">
                Last updated: <span id="current-time"></span>
            </div>
        </div>
    </div>

    <script>
        // แสดงเวลาปัจจุบัน
        function updateTime() {
            const now = new Date();
            document.getElementById('current-time').textContent = now.toLocaleTimeString();
        }
        updateTime();
        setInterval(updateTime, 1000); // อัพเดทเวลาทุกวินาที
    </script>
</body>
</html>
```

### Step 3.2: เพิ่มปุ่มควบคุม LED

สร้าง view สำหรับควบคุม LED และเพิ่มปุ่มใน template:

#### เพิ่มใน `views.py`:
```python
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Device
import paho.mqtt.client as mqtt
import json

# MQTT Configuration
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
LED_CONTROL_TOPIC = "thaitechzone/v2_board/control/led"

def dashboard_view(request):
    # Get the LED device object
    led_device, created = Device.objects.get_or_create(name="Onboard LED")
    
    context = {
        'led': led_device
    }
    return render(request, 'iot_dashboard/dashboard.html', context)

def control_led(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        
        # ส่งคำสั่งผ่าน MQTT
        client = mqtt.Client()
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        
        if action == 'on':
            client.publish(LED_CONTROL_TOPIC, 'ON')
            # อัพเดทใน database ด้วย
            led_device, created = Device.objects.get_or_create(name="Onboard LED")
            led_device.is_on = True
            led_device.save()
        elif action == 'off':
            client.publish(LED_CONTROL_TOPIC, 'OFF')
            # อัพเดทใน database ด้วย
            led_device, created = Device.objects.get_or_create(name="Onboard LED")
            led_device.is_on = False
            led_device.save()
        
        client.disconnect()
        
    return redirect('dashboard')
```

#### เพิ่มใน `urls.py`:
```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('control/led/', views.control_led, name='control_led'),
]
```

### Step 3.3: เพิ่มการจัดเก็บข้อมูลแบบ Time Series

สร้าง model ใหม่สำหรับเก็บประวัติข้อมูล:

#### เพิ่มใน `models.py`:
```python
from django.db import models
from django.utils import timezone

class Device(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_on = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} is {'ON' if self.is_on else 'OFF'}"

class DeviceHistory(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    status = models.BooleanField()
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.device.name} was {'ON' if self.status else 'OFF'} at {self.timestamp}"
```

---

## 📱 สิ่งที่จะได้หลังจากอัพเกรด:

1. **🔄 Auto-Refresh:** หน้าเว็บอัพเดทอัตโนมัติทุก 2 วินาที
2. **🎨 UI ที่สวยขึ้น:** เพิ่ม CSS styling และ LED indicator
3. **⏰ แสดงเวลา:** เห็นเวลาที่อัพเดทล่าสุด
4. **🎮 ปุ่มควบคุม:** ควบคุม LED จากหน้าเว็บ
5. **📊 ประวัติข้อมูล:** เก็บประวัติการเปลี่ยนแปลงสถานะ

---

## 🎯 การทดสอบระบบใหม่:

1. **ทดสอบ Auto-Refresh:**
   - เปิดหน้าเว็บ
   - ส่ง MQTT จาก MQTT Explorer
   - ดูหน้าเว็บอัพเดทอัตโนมัติใน 2 วินาที

2. **ทดสอบปุ่มควบคุม:**
   - กดปุ่ม ON/OFF บนหน้าเว็บ
   - ดูการเปลี่ยนแปลงใน MQTT Explorer
   - ดูการเปลี่ยนแปลงใน ESP32

3. **ทดสอบประวัติข้อมูล:**
   - ดูข้อมูลใน Django Admin
   - ตรวจสอบ DeviceHistory records

คุณต้องการให้ผมช่วยสร้างโค้ดสำหรับขั้นตอนใดก่อนครับ? 🚀