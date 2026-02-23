# MQTT Topics Reference

> **Last Updated:** 2026-02-23  
> **Firmware File:** `src/main.cpp`  
> **MQTT Broker:** `broker.hivemq.com:1883`

---

## Device Identity

| Key | Value |
|-----|-------|
| `DEVICE_NAME` (define) | `tti_board_001` |
| `DEVICE_ID` (runtime) | `tti_board_001` |
| `MQTT_CLIENT_ID` | `ThaiTechZone_tti_board_001` |

> **หากมีหลายบอร์ด** ให้เปลี่ยน `#define DEVICE_NAME` ใน `src/main.cpp` ก่อน flash
> ```
> tti_board_001  →  Board 1
> tti_board_002  →  Board 2
> tti_board_003  →  Board 3
> ```

---

## Topic Pattern

```
thaitechzone/v2/<DEVICE_ID>/<direction>/<property>
```

---

## Topics ทั้งหมด (ตัวอย่าง: DEVICE_NAME = "tti_board_001")

### LED

| Topic | Direction | Payload | หมายเหตุ |
|-------|-----------|---------|----------|
| `thaitechzone/v2/tti_board_001/control/led` | **SUBSCRIBE** (ESP รับคำสั่ง) | `ON` / `OFF` | Django → ESP32 |
| `thaitechzone/v2/tti_board_001/state/led` | **PUBLISH** (ESP ส่งสถานะ) | `ON` / `OFF` | ESP32 → Django (retain=true) |

---

### Relay

| Topic | Direction | Payload | หมายเหตุ |
|-------|-----------|---------|----------|
| `thaitechzone/v2/tti_board_001/control/relay1` | **SUBSCRIBE** | `ON` / `OFF` | Django → ESP32 |
| `thaitechzone/v2/tti_board_001/control/relay2` | **SUBSCRIBE** | `ON` / `OFF` | Django → ESP32 |
| `thaitechzone/v2/tti_board_001/control/relay3` | **SUBSCRIBE** | `ON` / `OFF` | Django → ESP32 |
| `thaitechzone/v2/tti_board_001/state/relay1` | **PUBLISH** | `ON` / `OFF` | ESP32 → Django (retain=true) |
| `thaitechzone/v2/tti_board_001/state/relay2` | **PUBLISH** | `ON` / `OFF` | ESP32 → Django (retain=true) |
| `thaitechzone/v2/tti_board_001/state/relay3` | **PUBLISH** | `ON` / `OFF` | ESP32 → Django (retain=true) |

> **Active Low:** Relay จริงบน PCB คือ LOW = ON, HIGH = OFF  
> แต่ Payload ที่ ESP32 ส่ง/รับ คือ `"ON"`/`"OFF"` ตรงตัว (firmware แปลงให้แล้ว)

---

### Sensor (DHT22)

| Topic | Direction | Payload | หมายเหตุ |
|-------|-----------|---------|----------|
| `thaitechzone/v2/tti_board_001/sensor/temperature` | **PUBLISH** | `"27.5"` (string, °C) | ทศนิยม 1 ตำแหน่ง |
| `thaitechzone/v2/tti_board_001/sensor/humidity` | **PUBLISH** | `"65.3"` (string, %) | ทศนิยม 1 ตำแหน่ง |
| `thaitechzone/v2/tti_board_001/sensor/data` | **PUBLISH** | JSON (ดูด้านล่าง) | ส่งทุก 5 วินาที |

#### JSON Payload — `sensor/data`
```json
{
  "temperature": 27.5,
  "humidity": 65.3,
  "device_name": "ESP_01"
}
```

---

### Isolated Digital Input (DI)

| Topic | Direction | Payload | หมายเหตุ |
|-------|-----------|---------|----------|
| `thaitechzone/v2/tti_board_001/state/isolate_in1` | **PUBLISH** | `ON` / `OFF` | ESP32 → Django (retain=true) |
| `thaitechzone/v2/tti_board_001/state/isolate_in2` | **PUBLISH** | `ON` / `OFF` | ESP32 → Django (retain=true) |

> **Active LOW:** สัญญาณ LOW บน GPIO = `"ON"`, HIGH = `"OFF"`  
> ส่งทันทีเมื่อ state เปลี่ยน + ส่งซ้ำทุก 2 วินาที (periodic publish)

---

## Publish Intervals

| ข้อมูล | Interval |
|--------|----------|
| Sensor data (temp/humidity/JSON) | ทุก **5000 ms** |
| Isolated Input (periodic) | ทุก **2000 ms** |
| Relay / LED state | ทันทีเมื่อมีการเปลี่ยน + ตอน reconnect |

---

## Wildcard Subscriptions สำหรับ Django Dashboard

```
# รับ sensor จากทุกบอร์ด
thaitechzone/v2/+/sensor/data

# รับสถานะทุก relay จากทุกบอร์ด
thaitechzone/v2/+/state/relay1
thaitechzone/v2/+/state/relay2
thaitechzone/v2/+/state/relay3

# รับสถานะ Isolated Input จากทุกบอร์ด
thaitechzone/v2/+/state/isolate_in1
thaitechzone/v2/+/state/isolate_in2

# ดูทุกอย่างจากบอร์ดเดียว (debug)
thaitechzone/v2/tti_board_001/#

# ดูทุกอย่างจากทุกบอร์ด (debug)
thaitechzone/v2/#
```

---

## ตัวอย่าง Topics สำหรับระบบหลายบอร์ด

| Board | DEVICE_NAME | Base Topic |
|-------|-------------|-----------|
| Board 1 | `tti_board_001` | `thaitechzone/v2/tti_board_001/` |
| Board 2 | `tti_board_002` | `thaitechzone/v2/tti_board_002/` |
| Board 3 | `tti_board_003` | `thaitechzone/v2/tti_board_003/` |
