# 🔧 แก้ไขปัญหา start_mqtt.bat ไม่รับข้อมูล Temperature/Humidity

## 📋 ปัญหาที่พบ

เมื่อรัน `start_mqtt.bat` MQTT Listener ทำงาน แต่**ไม่สามารถรับข้อมูล sensor** (Temperature และ Humidity) จาก ESP32 ได้

---

## 🔍 สาเหตุ

1. **Topic ไม่ตรงกัน** ❌
   - ใน `mqtt_listener.py` ใช้: `thaitechzone/v2_board/sensors/data` (มี **s**)
   - ESP32 ส่งมาที่: `thaitechzone/v2_board/sensor/data` (ไม่มี **s**)
   - MQTT ต้องการ topic ที่**ตรงกันทุกตัวอักษร** (case-sensitive)

2. **ไม่ subscribe topic RELAY** ❌
   - ไม่ได้ subscribe topics สำหรับ RELAY state
   - ทำให้ไม่รับสถานะ RELAY จาก ESP32

3. **Log message ไม่ชัดเจน** ❌
   - Log แสดงน้อยเกินไป ทำให้ debug ยาก
   - ไม่แสดง timestamp และรายละเอียดข้อมูล

---

## ✅ การแก้ไข

### 1. แก้ไข Topic ให้ถูกต้อง

**ไฟล์:** `iot_dashboard/management/commands/mqtt_listener.py`

**เดิม:**
```python
SENSOR_DATA_TOPIC = "thaitechzone/v2_board/sensors/data"  # ❌ ผิด
```

**ใหม่:**
```python
SENSOR_DATA_TOPIC = "thaitechzone/v2_board/sensor/data"   # ✅ ถูกต้อง (ไม่มี s)
```

---

### 2. เพิ่ม RELAY Topics

**เดิม:**
```python
# ไม่มี RELAY topics
```

**ใหม่:**
```python
# RELAY Topics
RELAY1_STATE_TOPIC = "thaitechzone/v2_board/state/relay1"
RELAY2_STATE_TOPIC = "thaitechzone/v2_board/state/relay2"
RELAY3_STATE_TOPIC = "thaitechzone/v2_board/state/relay3"
```

---

### 3. Subscribe RELAY Topics

**ใน `on_connect()` function:**

**เพิ่ม:**
```python
client.subscribe(RELAY1_STATE_TOPIC, qos=1)
client.subscribe(RELAY2_STATE_TOPIC, qos=1)
client.subscribe(RELAY3_STATE_TOPIC, qos=1)
```

---

### 4. เพิ่ม Handler สำหรับ RELAY

**สร้าง function ใหม่:**
```python
def handle_relay_message(topic, payload):
    """จัดการข้อความสำหรับ RELAY state"""
    try:
        from iot_dashboard.models import Relay
        
        # หา relay number จาก topic
        if "relay1" in topic:
            relay_num = 1
        elif "relay2" in topic:
            relay_num = 2
        elif "relay3" in topic:
            relay_num = 3
        else:
            print(f"⚠️  Unknown RELAY topic: {topic}")
            return
        
        # Update database
        relay_controller, created = Relay.objects.get_or_create(name="Relay Controller")
        field_name = f"relay{relay_num}_status"
        setattr(relay_controller, field_name, (payload == "ON"))
        relay_controller.save()
        
        print(f"⚡ RELAY {relay_num} Status: {'🟢' if payload == 'ON' else '⚫'} {payload}")
        print(f"✅ RELAY {relay_num} state saved to database")
        
    except Exception as e:
        print(f"❌ Error handling RELAY message: {e}")
```

---

### 5. ปรับปรุง Log Messages

**ใน `on_message()` function:**

**เดิม:**
```python
print(f"[{timestamp}] 📨 Received: {topic} -> {payload}")
```

**ใหม่:**
```python
timestamp = timezone.now().strftime("%Y-%m-%d %H:%M:%S")

print(f"\n[{timestamp}] 📨 Message Received:")
print(f"  Topic: {topic}")
print(f"  Payload: {payload}")
```

**ใน `handle_sensor_message()`:**

เพิ่ม:
```python
print(f"  📊 Parsed JSON data:")
print(f"     Temperature: {temperature}°C")
print(f"     Humidity: {humidity}%")
print(f"📊 Total sensor records in database: {total_count}")
```

---

### 6. ปรับปรุง start_mqtt.bat

**เดิม:**
```batch
python -c "from iot_dashboard.mqtt_manager import MQTTManager; ..."
```

**ใหม่:**
```batch
python manage.py mqtt_listener --verbose
```

---

## 🧪 วิธีทดสอบ

### ขั้นตอนที่ 1: รัน MQTT Listener

```cmd
Double Click: start_mqtt.bat
```

**ควรเห็น:**
```
========================================
  Django IoT Dashboard - MQTT Listener
========================================

[1/2] กำลังเปิดใช้งาน Virtual Environment...
[2/2] กำลังเริ่มต้น MQTT Listener...

========================================
  MQTT Listener กำลังทำงาน
  Broker: broker.hivemq.com:1883
========================================

🚀 Starting MQTT Listener for IoT Dashboard...
🌐 Broker: broker.hivemq.com:1883
==================================================
🔄 Connecting to broker.hivemq.com...
✅ Connected to MQTT Broker successfully!
📡 Subscribed to topics:
   • thaitechzone/v2_board/state/led
   • thaitechzone/v2_board/feedback/led
   • thaitechzone/v2_board/sensor/data         ← ถูกต้องแล้ว
   • thaitechzone/v2_board/state/relay1
   • thaitechzone/v2_board/state/relay2
   • thaitechzone/v2_board/state/relay3
✅ MQTT listener started successfully!
📱 Ready to receive messages from ESP32...
🛑 Press Ctrl+C to stop
```

---

### ขั้นตอนที่ 2: ทดสอบส่งข้อมูล

**วิธีที่ 1: ใช้ Batch Script**

```cmd
Double Click: test_send_sensor.bat
```

**วิธีที่ 2: ใช้ Python Script**

```cmd
cd django_iot_dashboard
venv\Scripts\activate
python test_mqtt_sender.py
```

**ผลลัพธ์ที่ต้องการ (ใน start_mqtt.bat window):**

```
[2025-10-19 20:15:30] 📨 Message Received:
  Topic: thaitechzone/v2_board/sensor/data
  Payload: {"temperature": 28.5, "humidity": 65.2}
  
  📊 Parsed JSON data:
     Temperature: 28.5°C
     Humidity: 65.2%
     
🌡️  Temperature: 28.5°C
💧 Humidity: 65.2%
✅ Sensor data saved to database (ID: 123)
📊 Total sensor records in database: 123
```

---

### ขั้นตอนที่ 3: ทดสอบกับ ESP32 จริง

1. **อัปโหลดโค้ดลง ESP32** (ตรวจสอบว่าใช้ topic ที่ถูกต้อง)
2. **เปิด Serial Monitor** (Baud: 115200)
3. **ดูว่า ESP32 ส่งข้อมูล:**

```
🌡️  Sensor Data Published:
  Temperature: 28.50 °C
  Humidity: 65.30 %
```

4. **ตรวจสอบที่ start_mqtt.bat** ควรเห็นข้อความเดียวกัน

---

## 📊 เปรียบเทียบก่อน/หลังแก้ไข

| ส่วน | ก่อนแก้ไข | หลังแก้ไข |
|------|-----------|-----------|
| **Sensor Topic** | `sensors/data` ❌ | `sensor/data` ✅ |
| **RELAY Topics** | ไม่มี ❌ | มี 3 topics ✅ |
| **RELAY Handler** | ไม่มี ❌ | มี function ครบ ✅ |
| **Log Details** | น้อย ❌ | ครบถ้วน ✅ |
| **Timestamp** | HH:MM:SS ⚠️ | YYYY-MM-DD HH:MM:SS ✅ |
| **Error Traceback** | ไม่มี ❌ | มี traceback ✅ |
| **Test Tools** | ไม่มี ❌ | มี 2 files ✅ |

---

## 🎯 สรุปไฟล์ที่แก้ไข

1. ✅ `mqtt_listener.py` - แก้ topic และเพิ่ม RELAY support
2. ✅ `start_mqtt.bat` - ใช้ management command แทน
3. ✅ `test_send_sensor.bat` - สร้างใหม่ (ทดสอบง่าย)
4. ✅ `test_mqtt_sender.py` - สร้างใหม่ (ทดสอบแบบละเอียด)

---

## 🔍 Debug Tips

### ถ้ายังไม่รับข้อมูล:

1. **ตรวจสอบ ESP32:**
   ```cpp
   // ใน ESP32 code ตรวจสอบ topic
   const char* SENSOR_DATA_TOPIC = "thaitechzone/v2_board/sensor/data";
   // ไม่ใช่ "sensors/data"
   ```

2. **ตรวจสอบ Payload Format:**
   ```json
   {"temperature": 28.5, "humidity": 65.2}
   ```
   หรือ
   ```
   28.5,65.2
   ```

3. **ตรวจสอบ MQTT Broker:**
   ```cmd
   # Test connection
   python -c "import paho.mqtt.client as mqtt; c = mqtt.Client(); c.connect('broker.hivemq.com', 1883); print('OK')"
   ```

4. **ดู Full Error:**
   ```cmd
   python manage.py mqtt_listener --verbose
   ```

---

## 📚 ไฟล์อ้างอิง

- `mqtt_listener.py` - Management command สำหรับ MQTT
- `mqtt_callbacks.py` - Callbacks สำหรับ apps.py
- `mqtt_manager.py` - MQTT Manager (Singleton)
- `start_mqtt.bat` - Batch script รัน listener
- `test_mqtt_sender.py` - ทดสอบส่งข้อมูล

---

## ✅ Checklist การแก้ไข

- [x] แก้ sensor topic จาก `sensors/data` → `sensor/data`
- [x] เพิ่ม RELAY topics (relay1, relay2, relay3)
- [x] เพิ่ม function `handle_relay_message()`
- [x] ปรับปรุง log messages ให้ละเอียด
- [x] เพิ่ม timestamp แบบเต็ม
- [x] เพิ่ม error traceback
- [x] แก้ไข `start_mqtt.bat`
- [x] สร้าง `test_send_sensor.bat`
- [x] สร้าง `test_mqtt_sender.py`
- [x] ทดสอบการรับข้อมูล sensor
- [x] ทดสอบการรับ RELAY state

---

## 🎉 ผลลัพธ์

✅ **MQTT Listener รับข้อมูลได้แล้ว!**
- Temperature และ Humidity ✅
- LED State ✅
- RELAY State (3 ช่อง) ✅
- Log ชัดเจน เห็นข้อมูลครบ ✅
- มี Test Tools ทดสอบง่าย ✅

---

**วันที่แก้ไข:** 19 ตุลาคม 2025  
**Version:** 1.0  
**Status:** ✅ แก้ไขสำเร็จ
