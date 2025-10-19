# 🔌 RELAY MQTT Integration - Complete Documentation

## 📋 Overview
อัปเดต Django Dashboard ให้รองรับการควบคุม RELAY 3 ช่องแบบสมบูรณ์ พร้อม synchronization กับ ESP32 แบบ 2-way communication

## 🎯 Features Implemented

### 1. **Control Topics** (Dashboard → ESP32)
Dashboard ส่งคำสั่งไปยัง ESP32 ผ่าน topics:
- `thaitechzone/v2_board/control/relay1` - ควบคุม RELAY 1
- `thaitechzone/v2_board/control/relay2` - ควบคุม RELAY 2
- `thaitechzone/v2_board/control/relay3` - ควบคุม RELAY 3
- **Payload**: `ON` หรือ `OFF`

### 2. **State Topics** (ESP32 → Dashboard)
ESP32 ส่งสถานะกลับมายัง Dashboard ผ่าน topics:
- `thaitechzone/v2_board/state/relay1` - สถานะ RELAY 1
- `thaitechzone/v2_board/state/relay2` - สถานะ RELAY 2
- `thaitechzone/v2_board/state/relay3` - สถานะ RELAY 3
- **Payload**: `ON` หรือ `OFF`

### 3. **Database Synchronization**
- Dashboard อัปเดต database เมื่อส่งคำสั่ง
- Dashboard อัปเดต database เมื่อได้รับสถานะจาก ESP32
- สถานะใน dashboard จะตรงกับ ESP32 เสมอ

## 🔧 Files Modified

### 1. `mqtt_manager.py`
**เพิ่ม:**
- RELAY control topics (3 topics)
- RELAY state topics (3 topics)
- `send_relay_command(relay_num, command)` method
- Subscribe state topics เมื่อเชื่อมต่อสำเร็จ
- อัปเดต `get_status()` เพื่อแสดง RELAY topics

**Code Example:**
```python
# RELAY Control Topics (Dashboard → ESP32)
self.RELAY1_CONTROL_TOPIC = "thaitechzone/v2_board/control/relay1"
self.RELAY2_CONTROL_TOPIC = "thaitechzone/v2_board/control/relay2"
self.RELAY3_CONTROL_TOPIC = "thaitechzone/v2_board/control/relay3"

# RELAY State Topics (ESP32 → Dashboard)
self.RELAY1_STATE_TOPIC = "thaitechzone/v2_board/state/relay1"
self.RELAY2_STATE_TOPIC = "thaitechzone/v2_board/state/relay2"
self.RELAY3_STATE_TOPIC = "thaitechzone/v2_board/state/relay3"

def send_relay_command(self, relay_num, command):
    """ส่งคำสั่งควบคุม RELAY"""
    topic_map = {
        1: self.RELAY1_CONTROL_TOPIC,
        2: self.RELAY2_CONTROL_TOPIC,
        3: self.RELAY3_CONTROL_TOPIC
    }
    topic = topic_map[relay_num]
    return self.send_message(topic, command)
```

### 2. `mqtt_callbacks.py` (NEW FILE ✨)
**ฟังก์ชันหลัก:**

#### `handle_relay_state_message(topic, message)`
- รับสถานะ RELAY จาก ESP32
- ดึงหมายเลข relay จาก topic
- อัปเดต database Relay model
- แสดง log เมื่อสถานะเปลี่ยน

**Code Example:**
```python
def handle_relay_state_message(topic, message):
    """จัดการข้อความสถานะ RELAY"""
    # ดึงหมายเลข RELAY จาก topic
    if 'relay1' in topic:
        relay_num = 1
    elif 'relay2' in topic:
        relay_num = 2
    elif 'relay3' in topic:
        relay_num = 3
    
    # แปลงสถานะ
    new_state = (message.upper().strip() == 'ON')
    
    # อัปเดต database
    relay_controller, _ = Relay.objects.get_or_create(
        name="ESP32 Relay Controller"
    )
    
    if relay_num == 1:
        relay_controller.relay1_status = new_state
    elif relay_num == 2:
        relay_controller.relay2_status = new_state
    elif relay_num == 3:
        relay_controller.relay3_status = new_state
    
    relay_controller.save()
```

#### `handle_sensor_data_message(topic, message)`
- รับข้อมูล temperature/humidity จาก ESP32
- Parse JSON data
- สร้าง SensorData record ใหม่

#### `handle_led_status_message(topic, message)`
- รับสถานะ LED จาก ESP32
- อัปเดต Device model

#### `register_mqtt_callbacks(mqtt_manager)`
- ลงทะเบียน callbacks ทั้งหมดกับ MQTT Manager
- เรียกใช้เมื่อ Django app เริ่มทำงาน

### 3. `views_simple.py`
**เปลี่ยนแปลง:**

```python
# เพิ่ม import
from .mqtt_manager import get_mqtt_manager, send_led_command, send_relay_command

def control_relay(request):
    """ควบคุม RELAY ผ่าน MQTT Manager"""
    if request.method == 'POST':
        relay_num = request.POST.get('relay_num')  # '1', '2', '3'
        action = request.POST.get('action')  # 'on', 'off', 'toggle'
        
        # กำหนดคำสั่ง MQTT
        if action == 'on':
            mqtt_command = 'ON'
        elif action == 'off':
            mqtt_command = 'OFF'
        elif action == 'toggle':
            mqtt_command = 'ON' if new_state else 'OFF'
        
        # ส่งคำสั่งผ่าน MQTT Manager
        success, result_msg = send_relay_command(int(relay_num), mqtt_command)
        
        if success:
            # อัปเดต database
            relay_controller.save()
            messages.success(request, f'✅ Success')
```

### 4. `apps.py`
**เปลี่ยนแปลง:**
- Import `register_mqtt_callbacks` แทน callback แบบเดิม
- เรียก `register_mqtt_callbacks(mqtt_manager)` ใน `ready()`
- ลบ inline callback functions ออก

**Before:**
```python
def ready(self):
    mqtt_manager = get_mqtt_manager()
    
    def handle_led_status(topic, message):
        # inline callback...
    
    mqtt_manager.register_message_callback(...)
```

**After:**
```python
def ready(self):
    mqtt_manager = get_mqtt_manager()
    register_mqtt_callbacks(mqtt_manager)  # ใช้ callbacks จาก mqtt_callbacks.py
```

## 📊 Data Flow Diagrams

### Control Flow (Dashboard → ESP32)
```
User Click Button
       ↓
views_simple.control_relay()
       ↓
send_relay_command(relay_num, 'ON'/'OFF')
       ↓
mqtt_manager.send_relay_command()
       ↓
mqtt_manager.send_message(topic, payload)
       ↓
MQTT Broker (HiveMQ)
       ↓
ESP32 receives on control topic
       ↓
ESP32 executes relay control
       ↓
ESP32 publishes state to state topic
```

### State Flow (ESP32 → Dashboard)
```
ESP32 changes relay state
       ↓
ESP32 publishes to state topic
       ↓
MQTT Broker (HiveMQ)
       ↓
mqtt_manager receives message
       ↓
mqtt_manager._on_message()
       ↓
handle_relay_state_message()
       ↓
Update Relay model in database
       ↓
Dashboard reflects new state
```

## 🔌 ESP32 Integration

### Required ESP32 Code Structure:

```cpp
// Topic definitions
const char* RELAY1_CONTROL_TOPIC = "thaitechzone/v2_board/control/relay1";
const char* RELAY2_CONTROL_TOPIC = "thaitechzone/v2_board/control/relay2";
const char* RELAY3_CONTROL_TOPIC = "thaitechzone/v2_board/control/relay3";
const char* RELAY1_STATE_TOPIC = "thaitechzone/v2_board/state/relay1";
const char* RELAY2_STATE_TOPIC = "thaitechzone/v2_board/state/relay2";
const char* RELAY3_STATE_TOPIC = "thaitechzone/v2_board/state/relay3";

// MQTT Callback
void callback(char* topic, byte* payload, unsigned int length) {
    String message = "";
    for (int i = 0; i < length; i++) {
        message += (char)payload[i];
    }
    
    // RELAY 1
    if (String(topic) == RELAY1_CONTROL_TOPIC) {
        if (message == "ON") {
            digitalWrite(RELAY1_PIN, HIGH);
            publishRelayState(1, true);
        } else if (message == "OFF") {
            digitalWrite(RELAY1_PIN, LOW);
            publishRelayState(1, false);
        }
    }
    
    // RELAY 2
    else if (String(topic) == RELAY2_CONTROL_TOPIC) {
        if (message == "ON") {
            digitalWrite(RELAY2_PIN, HIGH);
            publishRelayState(2, true);
        } else if (message == "OFF") {
            digitalWrite(RELAY2_PIN, LOW);
            publishRelayState(2, false);
        }
    }
    
    // RELAY 3
    else if (String(topic) == RELAY3_CONTROL_TOPIC) {
        if (message == "ON") {
            digitalWrite(RELAY3_PIN, HIGH);
            publishRelayState(3, true);
        } else if (message == "OFF") {
            digitalWrite(RELAY3_PIN, LOW);
            publishRelayState(3, false);
        }
    }
}

// Publish relay state back to dashboard
void publishRelayState(int relayNum, bool state) {
    String topic = "";
    String payload = state ? "ON" : "OFF";
    
    if (relayNum == 1) topic = RELAY1_STATE_TOPIC;
    else if (relayNum == 2) topic = RELAY2_STATE_TOPIC;
    else if (relayNum == 3) topic = RELAY3_STATE_TOPIC;
    
    mqtt_client.publish(topic.c_str(), payload.c_str());
}

// Subscribe to control topics
void setup() {
    // ... WiFi, MQTT setup ...
    
    mqtt_client.subscribe(RELAY1_CONTROL_TOPIC);
    mqtt_client.subscribe(RELAY2_CONTROL_TOPIC);
    mqtt_client.subscribe(RELAY3_CONTROL_TOPIC);
}
```

## 🧪 Testing Checklist

### Dashboard Testing:
- [ ] กด ON button แต่ละ relay - ตรวจสอบ log
- [ ] กด OFF button แต่ละ relay - ตรวจสอบ log
- [ ] กด Toggle button แต่ละ relay
- [ ] Refresh หน้า - สถานะต้องยังคงเดิม
- [ ] ตรวจสอบ Django admin - Relay model มีข้อมูล
- [ ] ตรวจสอบ terminal logs - เห็นข้อความ MQTT

### MQTT Testing (Manual with MQTT Explorer):
- [ ] Publish `ON` to `control/relay1` - ดู state/relay1 response
- [ ] Publish `OFF` to `control/relay1` - ดู state/relay1 response
- [ ] Publish to relay2, relay3 topics
- [ ] Subscribe state topics - ดูว่า ESP32 ส่งอะไรมา

### ESP32 Testing:
- [ ] ESP32 รับคำสั่ง ON/OFF ได้
- [ ] ESP32 ส่ง state กลับมา
- [ ] RELAY ทำงานตามคำสั่ง
- [ ] Serial monitor แสดงข้อความ MQTT

## 📝 Database Schema

### Relay Model:
```python
class Relay(models.Model):
    name = models.CharField(max_length=100)
    relay1_status = models.BooleanField(default=False)
    relay2_status = models.BooleanField(default=False)
    relay3_status = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)
```

**Example Record:**
```
id: 1
name: "ESP32 Relay Controller"
relay1_status: True (ON)
relay2_status: False (OFF)
relay3_status: True (ON)
last_updated: 2025-10-19 14:30:22
```

## 🚀 Deployment Steps

1. **Restart Django Server:**
   ```bash
   python manage.py runserver
   ```

2. **Check Logs:**
   - ต้องเห็น "🚀 Initializing MQTT Manager..."
   - ต้องเห็น "✅ All MQTT callbacks registered successfully"
   - ต้องเห็น "📥 Subscribed to topic: thaitechzone/v2_board/state/relay1"

3. **Upload ESP32 Code:**
   - Include RELAY control + state topics
   - Subscribe control topics
   - Publish state topics after each control

4. **Test Control:**
   - Click dashboard buttons
   - Watch Django logs
   - Watch ESP32 serial monitor

## 🔍 Troubleshooting

### Issue: Dashboard ส่งคำสั่งแล้ว ESP32 ไม่ตอบสนง
**Solutions:**
- ตรวจสอบ ESP32 subscribe ครบ 3 topics หรือไม่
- ตรวจสอบ MQTT broker address ตรงกันหรือไม่
- ดู ESP32 serial monitor - เห็นข้อความหรือไม่
- ใช้ MQTT Explorer ดู traffic

### Issue: Dashboard ไม่อัปเดตสถานะจาก ESP32
**Solutions:**
- ตรวจสอบ ESP32 publish ไป state topics
- ตรวจสอบ Django logs - เห็น "📥 Received RELAY X state" หรือไม่
- ตรวจสอบ `apps.py` - callbacks ลงทะเบียนแล้วหรือยัง
- Restart Django server

### Issue: MQTT Manager ไม่เชื่อมต่อ
**Solutions:**
- ตรวจสอบ internet connection
- ลอง broker อื่น (test.mosquitto.org)
- ตรวจสอบ port 1883 เปิดหรือไม่
- ดู logs - "❌ Connection failed" หรือไม่

## 📚 Related Files
- `mqtt_manager.py` - MQTT connection + topics
- `mqtt_callbacks.py` - Message handlers
- `views_simple.py` - Control logic
- `apps.py` - Initialization
- `models.py` - Relay model
- `dashboard_simple.html` - UI

## 🎉 Summary
✅ Dashboard ส่งคำสั่งไปยัง ESP32 ผ่าน control topics
✅ ESP32 ส่งสถานะกลับมายัง Dashboard ผ่าน state topics
✅ Database synchronization แบบ 2-way
✅ Real-time updates เมื่อ ESP32 เปลี่ยนสถานะ
✅ Topic names ตรงกับ ESP32 ทุกประการ
✅ Payload format: ON/OFF (uppercase)
