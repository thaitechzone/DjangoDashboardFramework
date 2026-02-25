# ESP32 Firmware — คู่มือความรู้และโครงสร้าง Code

> เอกสารนี้อธิบายองค์ประกอบทุกส่วนของ Firmware ฝั่ง ESP32 ที่ทำงานร่วมกับ Django IoT Dashboard
> อ้างอิง Branch: `Step7_AddXY-MD03_To_Dashboard`

---

## สารบัญ

1. [ภาพรวม Firmware](#1-ภาพรวม-firmware)
2. [โครงสร้างไฟล์](#2-โครงสร้างไฟล์)
3. [Pin Configuration](#3-pin-configuration)
4. [Device Classes (Header Files)](#4-device-classes-header-files)
5. [MQTT Topics และ Pattern](#5-mqtt-topics-และ-pattern)
6. [Sensor ที่ใช้งาน](#6-sensor-ที่ใช้งาน)
7. [Serial / Baud Rate](#7-serial--baud-rate)
8. [Dynamic Device ID](#8-dynamic-device-id)
9. [Flow การทำงาน](#9-flow-การทำงาน)
10. [Libraries ที่ต้องติดตั้ง](#10-libraries-ที่ต้องติดตั้ง)
11. [วิธี Setup และ Flash](#11-วิธี-setup-และ-flash)
12. [ข้อควรระวัง](#12-ข้อควรระวัง)

---

## 1. ภาพรวม Firmware

ระบบนี้ใช้ **ESP32** เป็น Edge Device ทำหน้าที่ติดต่อกับ Sensor และ Actuator แต่ละตัว แล้วส่งข้อมูลผ่าน **MQTT Protocol** ไปยัง Django Backend ที่รันบน Server

```
[ESP32]
  ├── อ่านค่า Sensor (XY-MD03, DS18B20, DHT22, PZEM-016)
  ├── ควบคุม Relay 1/2/3 (Active Low)
  ├── รับคำสั่งจาก MQTT (Relay ON/OFF, LED ON/OFF)
  ├── ส่ง State กลับผ่าน MQTT (Retain = true)
  ├── แสดงผล OLED (128x64)
  └── ตรวจสอบ Isolated Input 1/2
       │
       │ MQTT (TCP Port 1883)
       ▼
[broker.hivemq.com] ──── [Django Backend] ──── [Dashboard Web UI]
```

**สถาปัตยกรรมหลัก:**
- ไม่มี RTOS — ทำงานแบบ Single-threaded, Timer-based ใน `loop()`
- Device แต่ละตัวจัดการผ่าน Class ที่แยกไฟล์ (Header Files)
- MQTT Topics สร้างแบบ Dynamic จาก `DEVICE_ID` ทำให้ Deploy หลายบอร์ดได้โดยไม่ชนกัน

---

## 2. โครงสร้างไฟล์

```
ESP32 Code/
├── ESP32_RELAY_CONTROL_FULL_CODE.ino   ← Main Firmware (entry point)
├── DevRelay.h                          ← คลาสควบคุม Relay
├── DevSwitch.h                         ← คลาสจัดการปุ่มกด (Debounce, Long-press)
├── DevIsoInput.h                       ← คลาสจัดการ Isolated Input
├── DevTempHumidity.h                   ← คลาสอ่าน XY-MD03 ผ่าน Modbus RTU
├── DevPZEM.h                           ← คลาสอ่าน PZEM-016 ผ่าน Modbus RTU
└── ESP32Template.md                    ← เอกสารนี้
```

**ความสัมพันธ์ระหว่าง Files:**

```
ESP32_RELAY_CONTROL_FULL_CODE.ino
  ├── #include "DevRelay.h"         → ไม่ได้ใช้งาน instance โดยตรง (ควบคุม relay ผ่าน digitalRead/Write)
  ├── #include "DevSwitch.h"        → ไม่ได้ใช้งาน instance โดยตรง (ใช้ raw debounce)
  ├── #include "DevIsoInput.h"      → ไม่ได้ใช้งาน instance โดยตรง (ใช้ raw debounce)
  ├── #include "DevPZEM.h"          → ไม่ได้ใช้งาน instance โดยตรง (ready for future)
  └── #include "DevTempHumidity.h"  → ใช้งาน: DevTempHumidity xyMD03(&Serial, 1)
```

> **หมายเหตุ:** Class ส่วนใหญ่ในระบบนี้เป็น Reusable Components ที่พร้อมใช้งานในโปรเจกต์อื่น
> ปัจจุบัน DevTempHumidity เท่านั้นที่ถูก instantiate จริงในไฟล์หลัก

---

## 3. Pin Configuration

### ตาราง GPIO สรุป

| GPIO | ชื่อ | ประเภท | หมายเหตุ |
|------|------|--------|----------|
| 2 | LED_PIN | OUTPUT | LED บนบอร์ด, Active High |
| 4 | RELAY3_PIN | OUTPUT | Relay 3, Active Low (HIGH=OFF, LOW=ON) |
| 14 | DS18B20_PIN | INPUT | DS18B20 Temperature Sensor (1-Wire) |
| 15 | DHT_PIN | INPUT | DHT22 Temperature/Humidity (ยังไม่ได้ใช้งานหลัก) |
| 16 | RELAY2_PIN | OUTPUT | Relay 2, Active Low (HIGH=OFF, LOW=ON) |
| 17 | RELAY1_PIN | OUTPUT | Relay 1, Active Low (HIGH=OFF, LOW=ON) |
| 21 | SDA (I2C) | I2C | OLED SSD1306 (ค่า default ของ Wire.h) |
| 22 | SCL (I2C) | I2C | OLED SSD1306 (ค่า default ของ Wire.h) |
| 27 | ISOLATE_IN2 | INPUT | Isolated Digital Input 2, Active Low, External Pull-up |
| 32 | SW3_PIN | INPUT | ปุ่มกด 3 (Internal Pull-up ได้) |
| 33 | ISOLATE_IN1 | INPUT | Isolated Digital Input 1, Active Low, External Pull-up |
| 34 | SW1_PIN | INPUT | ปุ่มกด 1 (ต้องใช้ External Pull-up — GPIO34 ไม่มี Internal) |
| 35 | SW2_PIN | INPUT | ปุ่มกด 2 (ต้องใช้ External Pull-up — GPIO35 ไม่มี Internal) |
| TX0 | UART0 TX | UART | XY-MD03 + PZEM-016 ผ่าน RS485 (Serial0) |
| RX0 | UART0 RX | UART | XY-MD03 + PZEM-016 ผ่าน RS485 (Serial0) |

### ข้อสำคัญเกี่ยวกับ GPIO ESP32

```
⚠️  GPIO 34, 35, 36, 39 = Input Only (ไม่มี Internal Pull-up/Pull-down)
    ต้องใช้ External Pull-up 10kΩ ต่อ 3.3V เสมอ

⚠️  GPIO 0, 2, 12 = Strapping Pins (ระวังอย่าดึง LOW ตอน Boot)

✅  GPIO 21 (SDA) / GPIO 22 (SCL) = ค่า default I2C ของ Wire.h ESP32
```

### วงจร Active Low (Relay)

```
ESP32 GPIO17 ──┬── Relay Module IN1
               │
              [Relay Module ใช้ Logic Level Converter ภายใน]
              
GPIO HIGH (3.3V) → Relay OFF
GPIO LOW  (0V)   → Relay ON    ← Active Low
```

---

## 4. Device Classes (Header Files)

### 4.1 `DevRelay.h` — คลาสควบคุม Relay

**วัตถุประสงค์:** ห่อหุ้ม GPIO control ของ Relay ให้เรียกใช้ง่าย รองรับทั้ง Active Low และ Active High

```cpp
// วิธีใช้งาน
DevRelay relay(17, true);   // GPIO17, Active Low
relay.begin();              // ตั้งค่า pinMode + เริ่มต้นปิด
relay.on();                 // เปิด
relay.off();                // ปิด
relay.toggle();             // สลับ
relay.setState(true);       // ตั้งค่า (true=ON, false=OFF)
relay.getState();           // อ่านสถานะ
```

**Subclass: `DevRelayWithTimer`**
```cpp
DevRelayWithTimer timerRelay(17, true);
timerRelay.begin();
timerRelay.onWithTimer(5000);    // เปิด 5 วินาที แล้วปิดเอง
timerRelay.checkTimer();         // ต้องเรียกใน loop() ทุกรอบ
timerRelay.getRemainingTime();   // เวลาที่เหลืออยู่ (ms)
```

**Logic ภายใน:**
```
Active Low = true:
  on()  → digitalWrite(pin, LOW)
  off() → digitalWrite(pin, HIGH)

Active Low = false:
  on()  → digitalWrite(pin, HIGH)
  off() → digitalWrite(pin, LOW)
```

---

### 4.2 `DevSwitch.h` — คลาสจัดการปุ่มกด

**วัตถุประสงค์:** จัดการ Debounce, Edge Detection, Long-press และ Callback Functions

```cpp
// วิธีใช้งาน
DevSwitch btn(34, false, 50, 1000);  // GPIO34, Active Low, 50ms debounce, 1000ms longpress
btn.begin();

// ใน loop()
btn.update();

// ตั้ง Callback
btn.onClick([]() {
    Serial.println("Clicked!");
});
btn.onLongPress([]() {
    Serial.println("Long pressed!");
});
```

**Methods ทั้งหมด:**

| Method | คำอธิบาย |
|--------|----------|
| `begin()` | ตั้งค่า pinMode |
| `update()` | อัปเดตสถานะ — ต้องเรียกทุก loop cycle |
| `readRawState()` | อ่านค่า raw จาก GPIO |
| `isPressed()` | true ถ้าปุ่มกดค้างอยู่ |
| `onPress(fn)` | Callback เมื่อกดลง |
| `onRelease(fn)` | Callback เมื่อปล่อย |
| `onClick(fn)` | Callback เมื่อ click สั้น |
| `onLongPress(fn)` | Callback เมื่อกดค้าง |

**Debounce Algorithm:**
```
อ่าน GPIO → เปรียบเทียบกับค่าล่าสุด
  → ถ้าต่างกัน: บันทึกเวลา (lastDebounceTime)
  → ถ้าผ่านไป debounceDelay ms แล้วยังต่างกัน: ยืนยันการเปลี่ยนสถานะ
```

---

### 4.3 `DevIsoInput.h` — คลาส Isolated Digital Input

**วัตถุประสงค์:** จัดการ Digital Input ที่แยก Ground (Isolated) เช่น Optocoupler Input, รองรับ Debounce และนับจำนวนครั้งที่ Active

```cpp
// วิธีใช้งาน
DevIsoInput isoIn(33, false);   // GPIO33, Active Low
isoIn.begin();

// ใน loop()
isoIn.update();

// อ่านสถานะ
bool active = isoIn.isActive();               // true = Input Active
unsigned long count = isoIn.getActivationCount();  // นับจำนวนครั้ง

// Callback
isoIn.onActive([]() { Serial.println("Input activated"); });
isoIn.onInactive([]() { Serial.println("Input deactivated"); });
```

**Properties:**

| Property | คำอธิบาย |
|----------|----------|
| `pin` | GPIO pin |
| `activeHigh` | false = Active Low (default) |
| `activationCount` | นับจำนวนที่ Input เปลี่ยนเป็น Active |
| `debounceDelay` | ค่า default 50ms |

---

### 4.4 `DevTempHumidity.h` — XY-MD03 Modbus RTU

**วัตถุประสงค์:** อ่านค่าอุณหภูมิและความชื้นจาก XY-MD03 Sensor ผ่าน RS485 Modbus RTU (Serial0)

```cpp
// วิธีใช้งาน
DevTempHumidity xyMD03(&Serial, 1);  // ใช้ Serial0, Slave ID = 1
xyMD03.begin(9600);                  // เริ่มต้นที่ 9600 baud

// ใน loop() หรือ Timer
bool ok = xyMD03.update();           // อ่านค่าจาก Sensor (Modbus RTU)
if (ok) {
    float temp = xyMD03.getTemperature();  // °C
    float hum  = xyMD03.getHumidity();    // %RH
}
bool success = xyMD03.isLastReadSuccess(); // สถานะการอ่านครั้งล่าสุด
```

**Modbus Register Map:**

| Register | Address | Scale | ค่าที่ได้ |
|----------|---------|-------|---------|
| Temperature | 0x0001 | ÷ 10 | °C (เช่น raw 256 = 25.6°C) |
| Humidity | 0x0002 | ÷ 10 | %RH (เช่น raw 653 = 65.3%) |
| Function Code | 04 | — | Read Input Registers |

**XY-MD03 Specifications:**
- Slave ID: 1 (default ปรับได้ผ่าน DIP switch หรือ Software)
- Baud Rate: 9600 (default)
- Protocol: 9600 8N1
- Mode: RS485 Half-duplex

---

### 4.5 `DevPZEM.h` — PZEM-016 AC Power Monitor

**วัตถุประสงค์:** อ่านค่าไฟฟ้า AC จาก PZEM-016 (Voltage, Current, Power, Energy, Frequency, Power Factor) ผ่าน RS485 Modbus RTU

```cpp
// วิธีใช้งาน
DevPZEM pzem(&Serial, 0x01);   // ใช้ Serial0, Slave Address = 0x01
pzem.begin(9600);

// ใน loop()
pzem.update();   // อ่านค่า (มี internal interval 2000ms)

// อ่านค่า
float v  = pzem.getVoltage();      // V  (80-260V AC)
float i  = pzem.getCurrent();      // A
float p  = pzem.getPower();        // W
float e  = pzem.getEnergy();       // kWh
float f  = pzem.getFrequency();    // Hz
float pf = pzem.getPowerFactor();  // 0.00 - 1.00
String json = pzem.toJSON();       // JSON string
```

**PZEM-016 Modbus Register Map:**

| Register | Address | Scale | Unit |
|----------|---------|-------|------|
| Voltage | 0x0000 | × 0.1 | V |
| Current Low | 0x0001 | × 0.001 | A (32-bit) |
| Current High | 0x0002 | — | — |
| Power Low | 0x0003 | × 0.1 | W (32-bit) |
| Power High | 0x0004 | — | — |
| Energy Low | 0x0005 | × 1 | Wh (32-bit) |
| Energy High | 0x0006 | — | — |
| Frequency | 0x0007 | × 0.1 | Hz |
| Power Factor | 0x0008 | × 0.01 | — |
| Alarm Status | 0x0009 | — | — |

**MAX13487 Auto-Direction RS485:**
- ใช้ IC MAX13487 ซึ่งควบคุม TX/RX direction อัตโนมัติ
- ไม่ต้องใช้ DE/RE GPIO pin เพิ่มเติม
- ใช้ `preTransmission()` / `postTransmission()` callbacks ของ ModbusMaster

---

## 5. MQTT Topics และ Pattern

### Topic Pattern

```
thaitechzone/v2/<DEVICE_ID>/<direction>/<property>
                     │           │           │
                     │           │           └─ ชื่อ property เช่น led, relay1, temperature
                     │           └─ "control" = คำสั่งที่ส่งมา
                     │             "state"   = สถานะที่ ESP32 รายงาน
                     │             "sensor"  = ข้อมูลเซนเซอร์
                     └─ ค่าจาก #define DEVICE_NAME "ttz_board_001"
```

### รายการ Topics ทั้งหมด

| Topic | Direction | Retain | Payload | อธิบาย |
|-------|-----------|--------|---------|--------|
| `thaitechzone/v2/<id>/control/led` | Sub | — | `ON` / `OFF` | สั่งเปิด/ปิด LED จาก Backend |
| `thaitechzone/v2/<id>/state/led` | Pub | ✅ | `ON` / `OFF` | รายงานสถานะ LED |
| `thaitechzone/v2/<id>/control/relay1` | Sub | — | `ON` / `OFF` | สั่ง Relay 1 |
| `thaitechzone/v2/<id>/control/relay2` | Sub | — | `ON` / `OFF` | สั่ง Relay 2 |
| `thaitechzone/v2/<id>/control/relay3` | Sub | — | `ON` / `OFF` | สั่ง Relay 3 |
| `thaitechzone/v2/<id>/state/relay1` | Pub | ✅ | `ON` / `OFF` | รายงานสถานะ Relay 1 |
| `thaitechzone/v2/<id>/state/relay2` | Pub | ✅ | `ON` / `OFF` | รายงานสถานะ Relay 2 |
| `thaitechzone/v2/<id>/state/relay3` | Pub | ✅ | `ON` / `OFF` | รายงานสถานะ Relay 3 |
| `thaitechzone/v2/<id>/sensor/temperature` | Pub | — | `"25.6"` | อุณหภูมิ °C จาก XY-MD03 ทุก 5 วินาที |
| `thaitechzone/v2/<id>/sensor/humidity` | Pub | — | `"65.3"` | ความชื้น %RH จาก XY-MD03 ทุก 5 วินาที |
| `thaitechzone/v2/<id>/sensor/data` | Pub | — | JSON | JSON รวม temperature+humidity+device_name ทุก 5 วินาที |
| `thaitechzone/v2/<id>/sensor/ds18b20` | Pub | ✅ | `"28.5"` | อุณหภูมิ °C จาก DS18B20 ทุก 5 วินาที |
| `thaitechzone/v2/<id>/state/isolate_in1` | Pub | ✅ | `ON` / `OFF` | สถานะ Isolated Input 1 (เปลี่ยนทันที + ทุก 2 วินาที) |
| `thaitechzone/v2/<id>/state/isolate_in2` | Pub | ✅ | `ON` / `OFF` | สถานะ Isolated Input 2 (เปลี่ยนทันที + ทุก 2 วินาที) |

### JSON Payload ของ `sensor/data`

```json
{
  "temperature": 25.6,
  "humidity": 65.3,
  "device_name": "ttz_board_001"
}
```

### Retain Flag

Topics ที่มี `retain=true` หมายความว่า:
- Broker จะเก็บ payload ล่าสุดไว้
- Subscriber ที่ Subscribe ใหม่จะ**ได้รับค่าล่าสุดทันที**โดยไม่ต้องรอ
- ใช้สำหรับ State ที่ต้องการรู้ค่าทันทีเมื่อ Dashboard เปิดขึ้น

### Publish Intervals

| ข้อมูล | ความถี่ |
|--------|--------|
| XY-MD03 Temperature/Humidity | ทุก 5,000 ms |
| DS18B20 Temperature | ทุก 5,000 ms |
| Isolated Input (periodic) | ทุก 2,000 ms |
| Relay/LED State | เมื่อมีการเปลี่ยนแปลง |
| Isolated Input (on change) | ทันทีเมื่อ Input เปลี่ยนสถานะ |

---

## 6. Sensor ที่ใช้งาน

### 6.1 XY-MD03 Temp/Humidity Sensor

```
ประเภท:      Industrial RS485 Temperature & Humidity Sensor
Protocol:    Modbus RTU (RS485)
Interface:   Serial0 (UART0) บน ESP32
Baud Rate:   9600 8N1
Slave ID:    0x01 (default)
```

**วงจรต่อ:**
```
ESP32 TX0 ──→ MAX485 DI ──→ RS485 A/B ──→ XY-MD03
ESP32 RX0 ←── MAX485 RO
MAX485 DE/RE ── ต่อกันและต่อกับ GPIO เดิม (Manual Direction)
             หรือใช้ MAX13487 (Auto Direction - ไม่ต้องมี DE/RE GPIO)
```

**ทำงานอย่างไร:**
1. ESP32 ส่ง Modbus Read Input Register (FC04) ไปยัง Slave ID 1
2. ขอ Register 0x0001 (Temperature) และ 0x0002 (Humidity)
3. XY-MD03 ตอบกลับ ค่า raw ÷ 10 = ค่าจริง
4. ถ้าอ่านไม่สำเร็จ (timeout) → คืนค่า `false` และ Temperature/Humidity = 0.0

### 6.2 DS18B20 Temperature Sensor

```
ประเภท:      1-Wire Digital Temperature Sensor
GPIO:        14
Protocol:    1-Wire (Single pin)
Library:     OneWire + DallasTemperature
Precision:   12-bit (0.0625°C resolution)
```

**วงจรต่อ:**
```
GPIO14 ──┬── DS18B20 DATA
         │
        4.7kΩ
         │
        3.3V
         
DS18B20 VCC → 3.3V
DS18B20 GND → GND
DS18B20 DATA → GPIO14 + 4.7kΩ Pull-up
```

**การตรวจสอบ Sensor ที่ต่อ:**
```cpp
int count = ds18b20.getDeviceCount();  // จำนวน DS18B20 บน Bus
// สามารถต่อหลายตัวบน 1 Bus (1-Wire Multi-drop)
// อ่านด้วย Index: ds18b20.getTempCByIndex(0) = ตัวที่ 1
```

**Disconnected Detection:**
```cpp
float temp = ds18b20.getTempCByIndex(0);
if (temp == DEVICE_DISCONNECTED_C) { // = -127.0
    // Sensor ไม่ได้ต่ออยู่
}
```

### 6.3 DHT22 (รอใช้งานในอนาคต)

```
GPIO:    15
Library: DHT.h
ปัจจุบัน: Initialized แต่ไม่ได้อ่านค่าใน loop() หลัก
          XY-MD03 ทำหน้าที่แทนใน Step7
```

### 6.4 PZEM-016 AC Power Monitor (พร้อมใช้งาน)

```
ประเภท:      AC Power Monitor (Voltage, Current, Power, Energy)
Protocol:    Modbus RTU (RS485) — ใช้ Serial เดียวกับ XY-MD03
Slave ID:    0x01
Baud Rate:   9600 8N1
Input:       80-260V AC, 0-100A (ต้องต่อ CT Clamp)
```

---

## 7. Serial / Baud Rate

### ทำไมต้อง 9600?

```
XY-MD03 ค่า default = 9600 baud
PZEM-016 ค่า default = 9600 baud

ทั้งสองตัวใช้ Serial0 (UART0) ร่วมกัน
ต้องใช้ Baud Rate เดียวกัน → 9600
```

> **⚠️ ข้อควรระวัง:** เมื่อ Baud Rate = 9600 และใช้ `Serial.println()` สำหรับ Debug  
> ข้อความ Debug จะส่งผ่าน Serial0 พร้อมกับ Modbus Command  
> อาจทำให้ Modbus อ่านค่าผิดพลาดได้ในบางกรณี  
> **แนะนำ** ให้ใช้ `Serial.println()` น้อยๆ ในช่วงที่อ่าน Sensor Modbus

### Serial ใน Code

```cpp
Serial.begin(9600);          // กำหนดใน setup()

// xyMD03 ใช้ &Serial ตรงๆ
DevTempHumidity xyMD03(&Serial, 1);
xyMD03.begin(9600);          // ยืนยัน baud rate ภายใน ModbusMaster
```

---

## 8. Dynamic Device ID

### ปัญหาที่แก้ไข

ถ้า MQTT Topics เป็นค่า hardcode เช่น `"v2_board1/relay1"` จะเกิดปัญหา:
- Board หลายตัวส่ง MQTT Topics ชนกัน
- Django ไม่รู้ว่าข้อมูลมาจาก Board ไหน

### วิธีการแก้

```cpp
// บรรทัดเดียวที่ต้องแก้เมื่อ Flash บอร์ดใหม่
#define DEVICE_NAME "ttz_board_001"

// ใน setup()
DEVICE_ID = String(DEVICE_NAME);  // กำหนด String ชื่อ Device
String base = String("thaitechzone/v2/") + DEVICE_ID;

// Topics สร้างอัตโนมัติ
RELAY1_CONTROL_TOPIC = base + "/control/relay1";
// → "thaitechzone/v2/ttz_board_001/control/relay1"
```

### ตัวอย่าง Naming Convention

| DEVICE_NAME | ความหมาย |
|-------------|----------|
| `ttz_board_001` | ThaiTechZone Board หมายเลข 001 |
| `ttz_factory_001` | โรงงาน ตัวที่ 1 |
| `ttz_office_002` | ออฟฟิศ ตัวที่ 2 |
| `ttz_warehouse_003` | คลังสินค้า ตัวที่ 3 |

> **⚠️ ต้องเปลี่ยน `DEVICE_NAME` ก่อน Flash ทุกครั้งเมื่อมี Board ใหม่**

### Client ID ป้องกัน Session Conflict

```cpp
// ป้องกัน MQTT session conflict เมื่อ reconnect
String clientId = MQTT_CLIENT_ID + "_" + String(random(0xffff), HEX);
mqttClient.connect(clientId.c_str());
```

---

## 9. Flow การทำงาน

### Startup Sequence

```
power on
  │
  ▼
Serial.begin(9600)       ← ต้อง 9600 สำหรับ Modbus
  │
  ▼
Build DEVICE_ID and MQTT Topics
  │
  ▼
pinMode() ทุก Pin        ← Relay HIGH (OFF), Button INPUT_PULLUP
  │
  ▼
OLED begin()             ← ถ้าไม่มี OLED → oledAvailable = false (ไม่ crash)
  │
  ▼
dht.begin()              ← DHT22 init
xyMD03.begin(9600)       ← XY-MD03 Modbus init
ds18b20.begin()          ← DS18B20 1-Wire init
  │
  ▼
setup_wifi()             ← Blocking จนกว่าจะ connect สำเร็จ
  │
  ▼
mqttClient.setServer()
mqttClient.setCallback()
  │
  ▼
loop() เริ่มทำงาน
```

### Main Loop

```
loop() ─── MQTT ไม่ได้ connect? ──→ reconnectMQTT() ทุก 5 วินาที
              │
              ▼ (connected)
         mqttClient.loop()        ← process incoming messages → callback()
              │
         checkButtons()           ← ทุก loop cycle (debounce ภายใน)
              │
         checkIsolatedInputs()    ← ทุก loop cycle (debounce ภายใน)
              │
         millis() >= 5000ms? ───→ readAndPublishSensorData()   (XY-MD03)
         millis() >= 5000ms? ───→ readAndPublishDS18B20()
         millis() >= 2000ms? ───→ publishIsolatedInputState(1), (2)
         millis() >= 500ms?  ───→ updateDisplay()              (OLED)
```

### MQTT Callback (รับคำสั่งจาก Dashboard)

```
callback(topic, payload, length)
  │
  ├── topic == LED_CONTROL_TOPIC?
  │     └── "ON"/"OFF" → digitalWrite(LED_PIN) → publishLedState()
  │
  ├── topic == RELAY1_CONTROL_TOPIC?
  │     └── "ON"  → digitalWrite(RELAY1_PIN, LOW)   ← Active Low
  │         "OFF" → digitalWrite(RELAY1_PIN, HIGH)
  │         → publishRelayState(1)
  │
  ├── topic == RELAY2_CONTROL_TOPIC? → [เหมือน Relay 1]
  │
  └── topic == RELAY3_CONTROL_TOPIC? → [เหมือน Relay 1]
```

---

## 10. Libraries ที่ต้องติดตั้ง

### Arduino IDE / PlatformIO Libraries

| Library | Version | วัตถุประสงค์ | Author |
|---------|---------|-------------|--------|
| `WiFi` | Built-in | WiFi Connection | Espressif |
| `PubSubClient` | ≥2.8 | MQTT Client | Nick O'Leary |
| `DHT sensor library` | ≥1.4 | DHT22 Sensor | Adafruit |
| `ArduinoJson` | ≥6.x | JSON Serialize/Deserialize | Benoît Blanchon |
| `Wire` | Built-in | I2C (OLED) | Arduino |
| `Adafruit GFX Library` | ≥1.11 | OLED Graphics | Adafruit |
| `Adafruit SSD1306` | ≥2.5 | OLED Driver | Adafruit |
| `OneWire` | ≥2.3 | 1-Wire Bus | Paul Stoffregen |
| `DallasTemperature` | ≥3.9 | DS18B20 | Miles Burton |
| `ModbusMaster` | ≥2.0 | Modbus RTU (XY-MD03, PZEM) | 4-20mA |

### ติดตั้งผ่าน Arduino IDE

```
Tools → Manage Libraries...
ค้นหาและติดตั้งแต่ละ Library ข้างต้น
```

### ติดตั้งผ่าน PlatformIO (platformio.ini)

```ini
[env:esp32dev]
platform = espressif32
board = esp32dev
framework = arduino
lib_deps =
    knolleary/PubSubClient @ ^2.8
    adafruit/DHT sensor library @ ^1.4.6
    bblanchon/ArduinoJson @ ^6.21.3
    adafruit/Adafruit GFX Library @ ^1.11.9
    adafruit/Adafruit SSD1306 @ ^2.5.7
    paulstoffregen/OneWire @ ^2.3.7
    milesburton/DallasTemperature @ ^3.11.0
    4-20ma/ModbusMaster @ ^2.0.1
monitor_speed = 9600
```

---

## 11. วิธี Setup และ Flash

### สิ่งที่ต้องเตรียม

1. **ESP32 Development Board** (ESP32-WROOM-32 หรือ compatible)
2. **สาย USB** Type-A to Micro-USB (หรือ USB-C ขึ้นอยู่กับบอร์ด)
3. **XY-MD03** ต่อผ่าน RS485 Module (MAX485 หรือ MAX13487)
4. **DS18B20** + Resistor 4.7kΩ
5. **3x Relay Module** (5V, Active Low)
6. **OLED SSD1306 128x64** (I2C)
7. **Arduino IDE** ≥ 2.0 หรือ **PlatformIO**

### ขั้นตอน Setup

**Step 1: ติดตั้ง ESP32 Board ใน Arduino IDE**
```
File → Preferences → Additional Boards Manager URLs:
https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json

Tools → Board → Boards Manager → ค้นหา "esp32" → Install
```

**Step 2: เลือก Board**
```
Tools → Board → ESP32 Arduino → ESP32 Dev Module
Tools → Port → เลือก COM Port ของ ESP32
```

**Step 3: แก้ไข WiFi Credentials**
```cpp
// ในไฟล์ ESP32_RELAY_CONTROL_FULL_CODE.ino
const char* WIFI_SSID     = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
```

**Step 4: ตั้งค่า Device ID**
```cpp
// เปลี่ยนทุกครั้งสำหรับ Board ใหม่
#define DEVICE_NAME "ttz_board_001"
```

**Step 5: Upload**
```
กดปุ่ม Upload (→) หรือ Ctrl+U
รอ Compiling และ Uploading เสร็จ
เปิด Serial Monitor (9600 baud) ดู log
```

### ตรวจสอบผ่าน Serial Monitor

```
=== ESP32 MQTT LED Controller Starting ===
Device ID  : ttz_board_001
Base Topic : thaitechzone/v2/ttz_board_001
LED initialized (OFF)
Relay 1, 2, 3 initialized (OFF)
Buttons SW1, SW2, SW3 initialized
Isolated Inputs IN1, IN2 initialized
OLED Display initialized
DHT sensor initialized
XY-MD03 sensor initialized (Modbus RTU, Slave ID=1, 9600 baud)
DS18B20 sensors found: 1
Connecting to WiFi: myHome_2.4GHz
....
WiFi connected successfully!
IP address: 192.168.1.105
Attempting MQTT connection... connected!
Subscribed to: thaitechzone/v2/ttz_board_001/control/led
[XY-MD03] Temperature: 25.6 °C, Humidity: 65.3 %
DS18B20: 28.5 °C
```

---

## 12. ข้อควรระวัง

### ⚠️ Modbus Sharing (Serial0)

XY-MD03 และ PZEM-016 ใช้ Serial0 ร่วมกัน:
- **ต้องไม่อ่านทั้งสองพร้อมกัน** — ใช้ Slave ID ต่างกัน อ่านสลับกัน
- ถ้าต้องใช้ทั้งสองพร้อมกัน ควรแยก Serial Port (ใช้ Serial2)

### ⚠️ GPIO 34, 35 ไม่มี Internal Pull-up

```
GPIO34 (SW1), GPIO35 (SW2) → ต้องต่อ External Pull-up 10kΩ → 3.3V
ถ้าไม่ต่อ → ค่า floating → ปุ่มทำงานผิดปกติ
```

### ⚠️ Active Low Logic (Relay)

```
Relay ON  = digitalWrite(pin, LOW)   ← ยิง HIGH จะปิด
Relay OFF = digitalWrite(pin, HIGH)  ← ยิง LOW จะเปิด
→ อย่าสับสับนกับ Active High Relay Module
```

### ⚠️ WiFi Credentials ใน Code

```
⛔ อย่า Commit WiFi Password ขึ้น GitHub
✅ ใช้ .env หรือ ตั้งค่าใน defines แยกไฟล์ที่อยู่ใน .gitignore
```

### ⚠️ MQTT Broker สาธารณะ

```
HiveMQ Public Broker (broker.hivemq.com)
→ ไม่มี Authentication
→ ใครก็ Subscribe หรือ Publish ได้
→ สำหรับ Production ควรใช้ Private Broker (Mosquitto, HiveMQ Cloud)
```

### ⚠️ Serial Monitor Baud Rate

```
เปิด Serial Monitor ต้องตั้งค่า 9600 baud ให้ตรงกับ Serial.begin(9600)
ถ้าตั้ง 115200 → เห็น garbage characters
```

---

*เอกสารนี้อัปเดตล่าสุดตาม Branch `Step7_AddXY-MD03_To_Dashboard`*  
*ESP32 Repo: https://github.com/thaitechzone/ESP32TestDashbordDjango*
