# คู่มือการใช้งาน MQTT Explorer กับ Django IoT Dashboard

## 🔧 การติดตั้ง MQTT Explorer

### Windows:
1. ดาวน์โหลดจาก: http://mqtt-explorer.com/
2. ติดตั้งไฟล์ `.exe` ที่ดาวน์โหลดมา
3. เปิดโปรแกรม MQTT Explorer

### macOS:
```bash
# ใช้ Homebrew
brew install --cask mqtt-explorer
```

### Linux:
```bash
# ดาวน์โหลด AppImage จาก
wget https://github.com/thomasnordquist/MQTT-Explorer/releases/latest/download/MQTT-Explorer-*.AppImage
chmod +x MQTT-Explorer-*.AppImage
./MQTT-Explorer-*.AppImage
```

---

## ⚙️ การตั้งค่า MQTT Explorer

### 1. เชื่อมต่อกับ MQTT Broker

เปิด MQTT Explorer และสร้าง connection ใหม่:

**Connection Settings:**
- **Name:** `IoT Dashboard Test`
- **Protocol:** `mqtt://`
- **Host:** `broker.hivemq.com`
- **Port:** `1883`
- **Username:** (ว่างไว้)
- **Password:** (ว่างไว้)

### 2. กด Connect เพื่อเชื่อมต่อ

---

## 📤 การส่งข้อมูลไปยัง Django Dashboard

### Topic สำหรับ LED Status:
```
thaitechzone/v2_board/state/led
```

### วิธีส่งข้อมูล:

1. **คลิกขวาที่ Topic Tree** → เลือก **"Publish"**
2. **หรือใช้ Publish Panel ด้านล่าง**

**ตัวอย่างการส่งข้อมูล:**

#### 🟢 เปิด LED:
- **Topic:** `thaitechzone/v2_board/state/led`
- **Payload:** `ON`
- **QoS:** `0`
- **Retain:** `false`

#### 🔴 ปิด LED:
- **Topic:** `thaitechzone/v2_board/state/led`  
- **Payload:** `OFF`
- **QoS:** `0`
- **Retain:** `false`

---

## 🧪 ขั้นตอนการทดสอบ

### ขั้นตอนที่ 1: เริ่ม Django System

**Terminal 1 - Django Web Server:**
```bash
cd "D:\GitHub\DjangoDashboardFramework\django_iot_dashboard"
python manage.py runserver
```

**Terminal 2 - MQTT Listener:**
```bash
cd "D:\GitHub\DjangoDashboardFramework\django_iot_dashboard"
python manage.py mqtt_listener
```

### ขั้นตอนที่ 2: เปิด Dashboard
- เปิดเบราว์เซอร์ไปที่: `http://127.0.0.1:8000/`
- ควรเห็นหน้า Dashboard พร้อม LED status

### ขั้นตอนที่ 3: ทดสอบด้วย MQTT Explorer

1. **เชื่อมต่อ MQTT Explorer** กับ `broker.hivemq.com`

2. **ส่งคำสั่งเปิด LED:**
   - Topic: `thaitechzone/v2_board/state/led`
   - Payload: `ON`
   - กด **Publish**

3. **ตรวจสอบผลลัพธ์:**
   - ดู Terminal 2 (MQTT Listener) ควรแสดง:
     ```
     Connected to MQTT Broker with result code 0
     Received message on topic thaitechzone/v2_board/state/led: ON
     Updated Onboard LED status to True
     ```
   - Refresh หน้าเว็บ Dashboard ควรเห็น LED เป็น **ON (สีเขียว)**

4. **ส่งคำสั่งปิด LED:**
   - Topic: `thaitechzone/v2_board/state/led`
   - Payload: `OFF`  
   - กด **Publish**

5. **ตรวจสอบผลลัพธ์:**
   - ดู Terminal 2 ควรแสดง:
     ```
     Received message on topic thaitechzone/v2_board/state/led: OFF
     Updated Onboard LED status to False
     ```
   - Refresh หน้าเว็บ Dashboard ควรเห็น LED เป็น **OFF (สีเทา)**

---

## 📊 การตรวจสอบข้อมูลใน Database

### ตรวจสอบผ่าน Django Admin:

1. **สร้าง superuser (ถ้ายังไม่มี):**
```bash
cd "D:\GitHub\DjangoDashboardFramework\django_iot_dashboard"
python manage.py createsuperuser
```

2. **เปิด Django Admin:**
   - ไปที่: `http://127.0.0.1:8000/admin/`
   - ล็อกอินด้วย username/password ที่สร้าง

3. **ดูข้อมูล Device:**
   - คลิก **"Devices"** ใน IoT Dashboard section
   - ควรเห็น **"Onboard LED"** พร้อมสถานะปัจจุบัน

### ตรวจสอบผ่าน Django Shell:
```bash
cd "D:\GitHub\DjangoDashboardFramework\django_iot_dashboard"
python manage.py shell
```

```python
# ใน Django shell
from iot_dashboard.models import Device

# ดูข้อมูลทั้งหมด
devices = Device.objects.all()
for device in devices:
    print(f"{device.name}: {device.is_on}")

# ดูข้อมูล LED เฉพาะ
led = Device.objects.get(name="Onboard LED")
print(f"LED Status: {'ON' if led.is_on else 'OFF'}")
```

---

## 🔍 การตรวจสอบปัญหา

### ปัญหาที่พบบ่อย:

#### 1. MQTT Listener ไม่ได้รับข้อมูล
**ตรวจสอบ:**
- MQTT Explorer เชื่อมต่อสำเร็จหรือไม่
- Topic name ถูกต้องหรือไม่: `thaitechzone/v2_board/state/led`
- MQTT Listener ทำงานอยู่หรือไม่

**แก้ไข:**
```bash
# รีสตาร์ท MQTT Listener
# กด Ctrl+C ใน Terminal 2 แล้วรันใหม่
python manage.py mqtt_listener
```

#### 2. Dashboard ไม่อัพเดท
**สาเหตุ:** ต้อง refresh หน้าเว็บด้วยตนเอง

**แก้ไข:**
- กด F5 หรือ Ctrl+R เพื่อ refresh หน้าเว็บ
- หรือเพิ่ม auto-refresh ใน template

#### 3. Connection Error
**ตรวจสอบ:**
- เชื่อมต่อ Internet
- Firewall ไม่บล็อก port 1883

---

## 📱 ตัวอย่างคำสั่งอื่นๆ

### สำหรับทดสอบเพิ่มเติม:

#### ส่งข้อมูลอุณหภูมิ (สำหรับอนาคต):
- **Topic:** `thaitechzone/v2_board/sensor/temperature`
- **Payload:** `25.5`

#### ส่งข้อมูลความชื้น (สำหรับอนาคต):
- **Topic:** `thaitechzone/v2_board/sensor/humidity`  
- **Payload:** `60.2`

#### ส่งสถานะปุ่มกด (สำหรับอนาคต):
- **Topic:** `thaitechzone/v2_board/input/button`
- **Payload:** `PRESSED` หรือ `RELEASED`

---

## 🎯 Tips การใช้งาน

1. **ใช้ Retain Message:** เปิด `Retain` เพื่อให้ข้อมูลล่าสุดถูกเก็บไว้บน broker
2. **ตั้งค่า QoS:** ใช้ QoS 0 สำหรับข้อมูลทั่วไป, QoS 1 สำหรับข้อมูลสำคัญ
3. **ใช้ Wildcards:** Subscribe `thaitechzone/v2_board/#` เพื่อดูข้อมูลทั้งหมด
4. **เก็บ Log:** เปิด logging ใน MQTT Explorer เพื่อเก็บประวัติการส่งข้อมูล

---

## 🚀 การพัฒนาต่อ

หลังจากทดสอบสำเร็จแล้ว สามารถพัฒนาเพิ่มเติม:

1. **เพิ่ม Auto-refresh** ใน Dashboard
2. **เพิ่ม WebSocket** สำหรับ real-time updates  
3. **เพิ่มการควบคุม** LED จากหน้าเว็บ
4. **เพิ่ม Charts** สำหรับแสดงข้อมูล sensor
5. **เพิ่ม Authentication** สำหรับความปลอดภัย

**🎉 ขอให้สนุกกับการทดสอบ MQTT กับ Django Dashboard!**