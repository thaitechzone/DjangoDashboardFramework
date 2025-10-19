# 🔧 RELAY Quick Fix - Dashboard Simple

## ❌ ปัญหา
RELAY card ไม่แสดงบน dashboard เพราะ:
- URL path `/` ใช้ `views_simple.dashboard_simple` ไม่ใช่ `views.dashboard_view`
- `views_simple.py` ไม่มี Relay model และฟังก์ชันควบคุม
- `dashboard_simple.html` ไม่มี RELAY card

## ✅ การแก้ไข

### 1. เพิ่ม Relay ใน views_simple.py
```python
from .models import Device, SensorData, Relay

def dashboard_simple(request):
    # Get or create Relay controller
    relay_controller, created = Relay.objects.get_or_create(
        name="ESP32 Relay Controller",
        defaults={
            'relay1_status': False,
            'relay2_status': False,
            'relay3_status': False
        }
    )
    
    context = {
        'led': led_device,
        'relay': relay_controller,  # ← เพิ่ม relay
        ...
    }

def control_relay(request):
    """ควบคุม RELAY 1, 2, 3"""
    # ... implementation
```

### 2. อัพเดท URL routing
```python
# urls.py
path('control-relay/', views_simple.control_relay, name='control_relay'),
```

### 3. เพิ่ม RELAY Card ใน dashboard_simple.html
```html
<!-- RELAY Control Card -->
<div class="card relay-control">
    <h2>⚡ RELAY Controller</h2>
    
    <!-- RELAY 1, 2, 3 -->
    ...
</div>
```

### 4. เพิ่ม CSS สำหรับ RELAY
```css
.relay-control { ... }
.relay-item { ... }
.relay-header { ... }
.btn-sm { ... }
.btn-info { ... }
```

## 🎯 ผลลัพธ์
- ✅ RELAY card แสดงบน dashboard
- ✅ ควบคุม RELAY 3 ช่อง (ON/OFF/Toggle)
- ✅ แสดงสถานะ real-time
- ✅ ส่งคำสั่ง MQTT ไปยัง ESP32

## 🚀 ทดสอบ
1. Refresh หน้าเว็บด้วย **Ctrl+F5**
2. ดู RELAY Controller card
3. กดปุ่ม ON/OFF/Toggle
4. ตรวจสอบ messages แสดงความสำเร็จ

## 📡 MQTT Topics
```
Control: thaitechzone/v2_board/control/relay1|2|3
Payload: "ON" / "OFF"
```

---
**Fixed**: 2025-10-19
**Status**: ✅ Working
