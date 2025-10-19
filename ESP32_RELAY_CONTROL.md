# 🔌 ESP32 RELAY Control Documentation

## 📋 Overview
เอกสารนี้อธิบายการควบคุม RELAY 3 ช่องจาก Django Dashboard ผ่าน MQTT

## 🎯 MQTT Topics

### Control Topics (Subscribe บน ESP32)
```
thaitechzone/v2_board/control/relay1  - ควบคุม RELAY 1
thaitechzone/v2_board/control/relay2  - ควบคุม RELAY 2
thaitechzone/v2_board/control/relay3  - ควบคุม RELAY 3
```

### Status Topics (Publish จาก ESP32)
```
thaitechzone/v2_board/state/relay1    - สถานะ RELAY 1
thaitechzone/v2_board/state/relay2    - สถานะ RELAY 2
thaitechzone/v2_board/state/relay3    - สถานะ RELAY 3
```

## 📡 Message Format

### Control Messages (รับจาก Dashboard)
```
Payload: "ON"  - เปิด RELAY
Payload: "OFF" - ปิด RELAY
```

### Status Messages (ส่งไป Dashboard)
```
Payload: "ON"  - RELAY เปิดอยู่
Payload: "OFF" - RELAY ปิดอยู่
```

## 💻 ESP32 Code Example

### 1. Pin Configuration
```cpp
// กำหนด GPIO pins สำหรับ RELAY
#define RELAY1_PIN 25  // GPIO 25 สำหรับ RELAY 1
#define RELAY2_PIN 26  // GPIO 26 สำหรับ RELAY 2
#define RELAY3_PIN 27  // GPIO 27 สำหรับ RELAY 3

// ตัวแปรเก็บสถานะ RELAY
bool relay1_state = false;
bool relay2_state = false;
bool relay3_state = false;
```

### 2. Setup Function
```cpp
void setup() {
    Serial.begin(115200);
    
    // ตั้งค่า RELAY pins เป็น OUTPUT
    pinMode(RELAY1_PIN, OUTPUT);
    pinMode(RELAY2_PIN, OUTPUT);
    pinMode(RELAY3_PIN, OUTPUT);
    
    // ปิด RELAY ทั้งหมดตอนเริ่มต้น
    digitalWrite(RELAY1_PIN, LOW);
    digitalWrite(RELAY2_PIN, LOW);
    digitalWrite(RELAY3_PIN, LOW);
    
    // เชื่อมต่อ WiFi และ MQTT
    connectWiFi();
    connectMQTT();
    
    // Subscribe MQTT topics
    mqttClient.subscribe("thaitechzone/v2_board/control/relay1");
    mqttClient.subscribe("thaitechzone/v2_board/control/relay2");
    mqttClient.subscribe("thaitechzone/v2_board/control/relay3");
}
```

### 3. MQTT Callback Function
```cpp
void mqttCallback(char* topic, byte* payload, unsigned int length) {
    // แปลง payload เป็น String
    String message = "";
    for (int i = 0; i < length; i++) {
        message += (char)payload[i];
    }
    
    Serial.print("📨 Received: ");
    Serial.print(topic);
    Serial.print(" = ");
    Serial.println(message);
    
    // ตรวจสอบ topic และควบคุม RELAY
    String topicStr = String(topic);
    
    // RELAY 1
    if (topicStr == "thaitechzone/v2_board/control/relay1") {
        if (message == "ON") {
            digitalWrite(RELAY1_PIN, HIGH);
            relay1_state = true;
            Serial.println("🟢 RELAY 1 ON");
        } else if (message == "OFF") {
            digitalWrite(RELAY1_PIN, LOW);
            relay1_state = false;
            Serial.println("⚫ RELAY 1 OFF");
        }
        // ส่งสถานะกลับไป Dashboard
        publishRelayStatus(1, relay1_state);
    }
    
    // RELAY 2
    else if (topicStr == "thaitechzone/v2_board/control/relay2") {
        if (message == "ON") {
            digitalWrite(RELAY2_PIN, HIGH);
            relay2_state = true;
            Serial.println("🟢 RELAY 2 ON");
        } else if (message == "OFF") {
            digitalWrite(RELAY2_PIN, LOW);
            relay2_state = false;
            Serial.println("⚫ RELAY 2 OFF");
        }
        publishRelayStatus(2, relay2_state);
    }
    
    // RELAY 3
    else if (topicStr == "thaitechzone/v2_board/control/relay3") {
        if (message == "ON") {
            digitalWrite(RELAY3_PIN, HIGH);
            relay3_state = true;
            Serial.println("🟢 RELAY 3 ON");
        } else if (message == "OFF") {
            digitalWrite(RELAY3_PIN, LOW);
            relay3_state = false;
            Serial.println("⚫ RELAY 3 OFF");
        }
        publishRelayStatus(3, relay3_state);
    }
}
```

### 4. Publish Status Function
```cpp
void publishRelayStatus(int relayNum, bool state) {
    String topic = "thaitechzone/v2_board/state/relay" + String(relayNum);
    String payload = state ? "ON" : "OFF";
    
    mqttClient.publish(topic.c_str(), payload.c_str());
    
    Serial.print("📤 Published: ");
    Serial.print(topic);
    Serial.print(" = ");
    Serial.println(payload);
}
```

### 5. Main Loop
```cpp
void loop() {
    // ตรวจสอบการเชื่อมต่อ MQTT
    if (!mqttClient.connected()) {
        reconnectMQTT();
    }
    mqttClient.loop();
    
    // ส่งสถานะ RELAY ทุกๆ 30 วินาที
    static unsigned long lastStatusUpdate = 0;
    if (millis() - lastStatusUpdate > 30000) {
        publishRelayStatus(1, relay1_state);
        publishRelayStatus(2, relay2_state);
        publishRelayStatus(3, relay3_state);
        lastStatusUpdate = millis();
    }
    
    delay(100);
}
```

## 🔧 Hardware Connection

### RELAY Module Connection
```
ESP32 GPIO    ->    RELAY Module
----------------------------------------
GPIO 25       ->    RELAY 1 IN
GPIO 26       ->    RELAY 2 IN
GPIO 27       ->    RELAY 3 IN
GND           ->    GND
5V            ->    VCC (หรือ VIN)
```

### RELAY Module Specifications
- **Input Voltage**: 5V DC
- **Trigger Signal**: 3.3V (Compatible with ESP32)
- **Relay Rating**: 10A 250VAC / 10A 30VDC
- **Active State**: HIGH = ON, LOW = OFF

## ⚠️ Safety Considerations

1. **High Voltage Warning**: RELAY สามารถควบคุมไฟ 220V ได้ ต้องระวังอันตรายจากไฟฟ้า
2. **Load Rating**: ไม่ให้โหลดเกิน 10A per relay
3. **Power Supply**: ใช้ไฟเลี้ยง 5V ที่เพียงพอสำหรับ RELAY module
4. **Isolation**: RELAY module ควรมี Optocoupler เพื่อป้องกัน ESP32

## 🔍 Troubleshooting

### RELAY ไม่ทำงาน
1. ตรวจสอบการเชื่อมต่อสาย VCC และ GND
2. ตรวจสอบ GPIO pins ว่าถูกต้องหรือไม่
3. ตรวจสอบว่า MQTT connected หรือไม่
4. ดู Serial Monitor ว่ามี log หรือไม่

### RELAY ติดค้าง
1. เพิ่ม delay ระหว่างการสั่งงาน
2. ตรวจสอบแรงดันไฟเลี้ยง
3. ตรวจสอบความร้อนของ RELAY

### MQTT ไม่ได้รับข้อความ
1. ตรวจสอบว่า Subscribe topics ถูกต้อง
2. ตรวจสอบ MQTT broker connection
3. ตรวจสอบ WiFi connection

## 📊 Database Variables

### Django Model: Relay
```python
relay1_status = BooleanField(default=False)  # RELAY 1 สถานะ
relay2_status = BooleanField(default=False)  # RELAY 2 สถานะ
relay3_status = BooleanField(default=False)  # RELAY 3 สถานะ
last_updated = DateTimeField()               # เวลาอัพเดทล่าสุด
```

### API Endpoints
```
POST /api/control-relay/
Body: {
    "relay_num": "1",     // "1", "2", "3"
    "action": "on"        // "on", "off", "toggle"
}

Response: {
    "success": true,
    "relay_num": "1",
    "status": true,
    "message": "RELAY 1 is now ON",
    "command_sent": "ON"
}
```

## 🎮 Dashboard Usage

1. **การเปิด RELAY**: กดปุ่ม "🟢 ON"
2. **การปิด RELAY**: กดปุ่ม "⚫ OFF"
3. **Toggle RELAY**: กดปุ่ม "🔄"
4. **ดูสถานะ**: indicator สีเขียว (ON) หรือสีเทา (OFF)

## 📝 Notes

- RELAY จะถูกควบคุมผ่าน MQTT protocol
- สถานะจะถูกบันทึกใน database
- Dashboard จะ auto-update ทุก 5 วินาที
- ESP32 ควรส่งสถานะกลับมาทุกครั้งที่มีการเปลี่ยนแปลง

## 🚀 Next Steps

1. Upload code ลง ESP32
2. เปิด Serial Monitor เพื่อดู debug messages
3. เปิด Dashboard และทดสอบควบคุม RELAY
4. ตรวจสอบว่า RELAY ทำงานตามคำสั่ง

---
**Created**: 2025-10-19
**Version**: 1.0
**Author**: ThaiTechZone
