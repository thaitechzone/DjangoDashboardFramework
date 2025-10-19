# 🎯 Quick Guide: วิธีรัน MQTT Listener และทดสอบ

## 🚀 วิธีรัน (แบบง่าย)

### วิธีที่ 1: ใช้ Batch Script (แนะนำ) ⭐

```cmd
Double Click:  start_mqtt.bat
```

ระบบจะ:
1. เปิด Virtual Environment อัตโนมัติ
2. รัน MQTT Listener
3. แสดง log ทุกข้อความที่รับได้

---

### วิธีที่ 2: ใช้ Command Line

```cmd
cd django_iot_dashboard
venv\Scripts\activate
python manage.py mqtt_listener
```

**เพิ่ม verbose mode (แสดง debug):**
```cmd
python manage.py mqtt_listener --verbose
```

---

## 🧪 วิธีทดสอบ

### ทดสอบแบบง่าย (Batch Script):

```cmd
# Terminal 1: รัน MQTT Listener
Double Click:  start_mqtt.bat

# Terminal 2: ส่งข้อมูลทดสอบ
Double Click:  test_send_sensor.bat
```

---

### ทดสอบแบบละเอียด (Python Script):

```cmd
# Terminal 1: รัน MQTT Listener
start_mqtt.bat

# Terminal 2: ส่งข้อมูลหลายครั้ง
cd django_iot_dashboard
venv\Scripts\activate
python test_mqtt_sender.py
```

**ผลลัพธ์ที่คาดหวัง:**
- ส่งข้อมูล 5 ครั้ง (ทุก 3 วินาที)
- แต่ละครั้งส่ง: Sensor + LED + RELAY (3 ช่อง)
- Terminal 1 จะแสดง log ทุกข้อความ

---

## 📊 ตัวอย่าง Output

### เมื่อรัน start_mqtt.bat:

```
========================================
  MQTT Listener กำลังทำงาน
  Broker: broker.hivemq.com:1883
========================================

🚀 Starting MQTT Listener for IoT Dashboard...
✅ Connected to MQTT Broker successfully!
📡 Subscribed to topics:
   • thaitechzone/v2_board/state/led
   • thaitechzone/v2_board/sensor/data      ← รับข้อมูล sensor
   • thaitechzone/v2_board/state/relay1
   • thaitechzone/v2_board/state/relay2
   • thaitechzone/v2_board/state/relay3

✅ MQTT listener started successfully!
📱 Ready to receive messages from ESP32...
```

---

### เมื่อรับข้อมูล Sensor:

```
[2025-10-19 20:15:30] 📨 Message Received:
  Topic: thaitechzone/v2_board/sensor/data
  Payload: {"temperature": 28.5, "humidity": 65.2}
  
  📊 Parsed JSON data:
     Temperature: 28.5°C
     Humidity: 65.2%
     
🌡️  Temperature: 28.5°C
💧 Humidity: 65.2%
✅ Sensor data saved to database (ID: 45)
📊 Total sensor records in database: 45
```

---

### เมื่อรับสถานะ RELAY:

```
[2025-10-19 20:15:32] 📨 Message Received:
  Topic: thaitechzone/v2_board/state/relay1
  Payload: ON
  
⚡ RELAY 1 Status: 🟢 ON
  → Changed from OFF to ON
✅ RELAY 1 state saved to database
```

---

## 🎯 Topics ที่รองรับ

| Topic | คำอธิบาย | Format |
|-------|----------|--------|
| `sensor/data` | ข้อมูล Temperature/Humidity | JSON: `{"temperature": 28.5, "humidity": 65.2}` |
| `state/led` | สถานะ LED | `ON` หรือ `OFF` |
| `state/relay1` | สถานะ RELAY 1 | `ON` หรือ `OFF` |
| `state/relay2` | สถานะ RELAY 2 | `ON` หรือ `OFF` |
| `state/relay3` | สถานะ RELAY 3 | `ON` หรือ `OFF` |

**Base Topic:** `thaitechzone/v2_board/`

---

## ⚠️ หมายเหตุสำคัญ

### MQTT Listener vs Django Server:

1. **Django Server (start_server.bat):**
   - MQTT ทำงาน **อัตโนมัติ** ใน background
   - ผ่าน `iot_dashboard/apps.py`
   - ไม่แสดง log บนหน้าจอ
   - ✅ **ใช้แบบนี้ปกติ**

2. **MQTT Listener (start_mqtt.bat):**
   - รัน MQTT **แยกต่างหาก**
   - แสดง log ทุกข้อความ
   - ✅ **ใช้เมื่อต้องการ debug**

---

## 🔍 Debug Tips

### ถ้าไม่รับข้อมูล:

1. **ตรวจสอบ ESP32:**
   - WiFi เชื่อมต่อแล้ว?
   - MQTT เชื่อมต่อ broker.hivemq.com แล้ว?
   - Topic ถูกต้อง?

2. **ตรวจสอบ Internet:**
   ```cmd
   ping broker.hivemq.com
   ```

3. **ทดสอบส่งข้อมูล:**
   ```cmd
   test_send_sensor.bat
   ```

4. **ดู Error:**
   ```cmd
   python manage.py mqtt_listener --verbose
   ```

---

## 📁 ไฟล์ที่เกี่ยวข้อง

```
django_iot_dashboard/
├── start_mqtt.bat              ← รัน MQTT Listener
├── test_send_sensor.bat        ← ทดสอบส่งข้อมูล (ง่าย)
├── test_mqtt_sender.py         ← ทดสอบส่งข้อมูล (ละเอียด)
└── iot_dashboard/
    └── management/
        └── commands/
            └── mqtt_listener.py  ← Management Command
```

---

## ✅ Checklist

- [ ] รัน `start_mqtt.bat`
- [ ] เห็นข้อความ "✅ Connected to MQTT Broker successfully!"
- [ ] เห็นข้อความ "✅ MQTT listener started successfully!"
- [ ] ทดสอบด้วย `test_send_sensor.bat`
- [ ] เห็นข้อมูล sensor ใน terminal
- [ ] เช็ค Dashboard: http://127.0.0.1:8000/
- [ ] เห็นข้อมูลใน Temperature/Humidity cards
- [ ] เห็นกราฟอัปเดต
- [ ] เห็นตาราง Recent Readings

---

## 🎉 สำเร็จ!

ถ้าทำตาม checklist แล้วเห็นข้อมูลครบ = **ระบบพร้อมใช้งาน!** 🎊

---

**Quick Commands:**

```cmd
# รัน MQTT Listener
start_mqtt.bat

# ทดสอบส่งข้อมูล
test_send_sensor.bat

# หยุด
Ctrl + C
```
