# 🚀 Django IoT Dashboard - REST API Documentation

## 📋 สารบัญ
1. [Overview](#-overview)
2. [Base URL](#-base-url)
3. [Import Postman Collection](#-import-postman-collection)
4. [API Endpoints](#-api-endpoints)
5. [Response Format](#-response-format)
6. [Error Handling](#️-error-handling)
7. [Examples](#-examples)
8. [Testing with Postman](#-testing-with-postman)

---

## 🎯 Overview

REST API สำหรับควบคุมและอ่านข้อมูลจาก Django IoT Dashboard

### ✨ Features:
- ✅ **LED Control** - เปิด/ปิด LED ผ่าน MQTT
- ✅ **Relay Control** - ควบคุม Relay 3 ช่อง
- ✅ **Sensor Data Management** - CRUD operations สำหรับข้อมูล sensor
- ✅ **System Status** - ดูสถานะระบบทั้งหมด
- ✅ **Statistics** - วิเคราะห์ข้อมูล sensor
- ✅ **No Authentication Required** - ใช้งานได้ทันทีโดยไม่ต้อง login

### 🔑 API Version:
- **Current Version:** v1
- **Base Path:** `/api/v1/`

---

## 🌐 Base URL

### Development:
```
http://localhost:8000
```

### Production:
```
http://your-server-ip:8000
```

หรือ

```
http://your-domain.com
```

---

## 📥 Import Postman Collection

### ขั้นตอนที่ 1: เปิด Postman

1. เปิดแอพ Postman (หรือไปที่ https://www.postman.com/)
2. คลิก **"Import"** (มุมบนซ้าย)

### ขั้นตอนที่ 2: Import ไฟล์

**วิธีที่ 1: Import จากไฟล์**
1. คลิก **"Upload Files"**
2. เลือกไฟล์ `Django_IoT_Dashboard_API.postman_collection.json`
3. คลิก **"Import"**

**วิธีที่ 2: Drag & Drop**
1. ลากไฟล์ `Django_IoT_Dashboard_API.postman_collection.json`
2. วางลงในหน้าต่าง Postman

### ขั้นตอนที่ 3: ตั้งค่า Base URL

1. คลิกที่ **"Django IoT Dashboard API"** collection
2. ไปที่แท็บ **"Variables"**
3. แก้ไข `base_url` เป็น URL ของเซิร์ฟเวอร์
   - Development: `http://localhost:8000`
   - Production: `http://your-ip:8000`
4. คลิก **"Save"**

### ขั้นตอนที่ 4: ทดสอบ

1. เปิด request **"Get System Status"**
2. คลิก **"Send"**
3. ดูผลลัพธ์ด้านล่าง

---

## 📡 API Endpoints

### 1. LED Control

#### Get LED Status
```http
GET /api/v1/led/
```

**Response:**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "name": "Onboard LED",
        "is_on": false,
        "last_updated": "2025-10-22 14:30:00"
    }
}
```

#### Control LED
```http
POST /api/v1/led/
Content-Type: application/json

{
    "command": "ON"  // "ON", "OFF", or "TOGGLE"
}
```

**Response:**
```json
{
    "success": true,
    "message": "LED turned ON",
    "data": {
        "id": 1,
        "name": "Onboard LED",
        "is_on": true,
        "command_sent": "ON",
        "last_updated": "2025-10-22 14:30:15"
    }
}
```

---

### 2. Relay Control

#### Get All Relays Status
```http
GET /api/v1/relay/
```

**Response:**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "name": "ESP32 Relay Controller",
        "relay1": false,
        "relay2": true,
        "relay3": false,
        "last_updated": "2025-10-22 14:30:00"
    }
}
```

#### Control Relay
```http
POST /api/v1/relay/
Content-Type: application/json

{
    "relay_num": 1,      // 1, 2, or 3
    "command": "ON"      // "ON", "OFF", or "TOGGLE"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Relay 1 turned ON",
    "data": {
        "id": 1,
        "relay_num": 1,
        "status": true,
        "command_sent": "ON",
        "last_updated": "2025-10-22 14:30:25"
    }
}
```

---

### 3. Sensor Data Management

#### Get Latest Sensor Data
```http
GET /api/v1/sensors/latest/
```

**Response:**
```json
{
    "success": true,
    "data": {
        "id": 100,
        "temperature": 28.5,
        "humidity": 65.3,
        "timestamp": "2025-10-22 14:30:00",
        "device_name": "ESP32_DHT22"
    }
}
```

#### Get Sensor List (with Pagination)
```http
GET /api/v1/sensors/?limit=10&offset=0
```

**Query Parameters:**
- `limit` (optional, default: 20) - จำนวนรายการต่อหน้า
- `offset` (optional, default: 0) - ตำแหน่งเริ่มต้น

**Response:**
```json
{
    "success": true,
    "data": [
        {
            "id": 100,
            "temperature": 28.5,
            "humidity": 65.3,
            "timestamp": "2025-10-22 14:30:00",
            "device_name": "ESP32_DHT22"
        },
        {
            "id": 99,
            "temperature": 28.3,
            "humidity": 64.8,
            "timestamp": "2025-10-22 14:29:55",
            "device_name": "ESP32_DHT22"
        }
    ],
    "pagination": {
        "total": 150,
        "limit": 10,
        "offset": 0,
        "count": 10
    }
}
```

#### Get Sensor Statistics
```http
GET /api/v1/sensors/stats/
```

**Response:**
```json
{
    "success": true,
    "data": {
        "total_readings": 150,
        "temperature": {
            "average": 28.45,
            "max": 32.5,
            "min": 24.0
        },
        "humidity": {
            "average": 65.30,
            "max": 80.0,
            "min": 50.0
        },
        "latest_reading": "2025-10-22 14:30:00",
        "oldest_reading": "2025-10-21 08:00:00"
    }
}
```

#### Create Sensor Data
```http
POST /api/v1/sensors/
Content-Type: application/json

{
    "temperature": 28.5,
    "humidity": 65.3,
    "device_name": "Test_Device"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Sensor data created successfully",
    "data": {
        "id": 101,
        "temperature": 28.5,
        "humidity": 65.3,
        "device_name": "Test_Device",
        "timestamp": "2025-10-22 14:31:00"
    }
}
```

#### Get Sensor by ID
```http
GET /api/v1/sensors/{id}/
```

**Example:**
```http
GET /api/v1/sensors/100/
```

**Response:**
```json
{
    "success": true,
    "data": {
        "id": 100,
        "temperature": 28.5,
        "humidity": 65.3,
        "timestamp": "2025-10-22 14:30:00",
        "device_name": "ESP32_DHT22"
    }
}
```

#### Update Sensor Data (Full Update)
```http
PUT /api/v1/sensors/{id}/
Content-Type: application/json

{
    "temperature": 30.0,
    "humidity": 70.5,
    "device_name": "Updated_Device"
}
```

#### Update Sensor Data (Partial Update)
```http
PATCH /api/v1/sensors/{id}/
Content-Type: application/json

{
    "temperature": 29.0
}
```

**Response:**
```json
{
    "success": true,
    "message": "Sensor data updated successfully",
    "data": {
        "id": 100,
        "temperature": 29.0,
        "humidity": 65.3,
        "timestamp": "2025-10-22 14:30:00",
        "device_name": "ESP32_DHT22"
    }
}
```

#### Delete Sensor Data
```http
DELETE /api/v1/sensors/{id}/
```

**Response:**
```json
{
    "success": true,
    "message": "Sensor data deleted successfully",
    "deleted_data": {
        "id": 100,
        "temperature": 28.5,
        "humidity": 65.3,
        "timestamp": "2025-10-22 14:30:00"
    }
}
```

---

### 4. System Status

#### Get Complete System Status
```http
GET /api/v1/system/status/
```

**Response:**
```json
{
    "success": true,
    "data": {
        "led": {
            "is_on": false,
            "last_updated": "2025-10-22 14:30:00"
        },
        "relays": {
            "relay1": false,
            "relay2": true,
            "relay3": false,
            "last_updated": "2025-10-22 14:30:15"
        },
        "sensors": {
            "total_readings": 150,
            "latest": {
                "temperature": 28.5,
                "humidity": 65.3,
                "timestamp": "2025-10-22 14:30:00"
            }
        },
        "mqtt": {
            "connected": true,
            "broker": "broker.hivemq.com",
            "port": 1883
        },
        "server_time": "2025-10-22 14:31:00"
    }
}
```

---

## 📝 Response Format

### Success Response
```json
{
    "success": true,
    "data": { ... },
    "message": "Optional success message"
}
```

### Error Response
```json
{
    "success": false,
    "error": "Error message description"
}
```

---

## ⚠️ Error Handling

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request สำเร็จ |
| 201 | Created | สร้างข้อมูลสำเร็จ |
| 400 | Bad Request | ข้อมูลไม่ถูกต้อง |
| 404 | Not Found | ไม่พบข้อมูล |
| 405 | Method Not Allowed | Method ไม่ถูกต้อง |
| 500 | Internal Server Error | Server error |

### Common Errors

#### Invalid JSON
```json
{
    "success": false,
    "error": "Invalid JSON body"
}
```

#### Invalid Command
```json
{
    "success": false,
    "error": "Invalid command. Use: ON, OFF, or TOGGLE"
}
```

#### Not Found
```json
{
    "success": false,
    "error": "Sensor with ID 999 not found"
}
```

#### MQTT Error
```json
{
    "success": false,
    "error": "MQTT command failed: Connection timeout"
}
```

---

## 💡 Examples

### Example 1: เปิด LED และ Relay 1
```bash
# 1. เปิด LED
curl -X POST http://localhost:8000/api/v1/led/ \
  -H "Content-Type: application/json" \
  -d '{"command":"ON"}'

# 2. เปิด Relay 1
curl -X POST http://localhost:8000/api/v1/relay/ \
  -H "Content-Type: application/json" \
  -d '{"relay_num":1,"command":"ON"}'
```

### Example 2: อ่านข้อมูล Sensor ล่าสุด
```bash
curl http://localhost:8000/api/v1/sensors/latest/
```

### Example 3: สร้างข้อมูล Sensor ทดสอบ
```bash
curl -X POST http://localhost:8000/api/v1/sensors/ \
  -H "Content-Type: application/json" \
  -d '{
    "temperature": 28.5,
    "humidity": 65.3,
    "device_name": "Test_Device"
  }'
```

### Example 4: ดึงข้อมูล Sensor แบบ Pagination
```bash
# หน้าแรก (10 รายการ)
curl "http://localhost:8000/api/v1/sensors/?limit=10&offset=0"

# หน้าที่ 2 (10 รายการถัดไป)
curl "http://localhost:8000/api/v1/sensors/?limit=10&offset=10"
```

### Example 5: ดูสถานะระบบทั้งหมด
```bash
curl http://localhost:8000/api/v1/system/status/
```

---

## 🧪 Testing with Postman

### Quick Start

1. **Import Collection**
   - Import `Django_IoT_Dashboard_API.postman_collection.json`

2. **Set Base URL**
   - ไปที่ Variables tab
   - ตั้งค่า `base_url` = `http://localhost:8000`

3. **Test System Status**
   - เปิด "Get System Status"
   - คลิก "Send"
   - ตรวจสอบว่าได้ response กลับมา

4. **Test LED Control**
   - เปิด "Turn LED ON"
   - คลิก "Send"
   - ตรวจสอบว่า LED เปิดสำเร็จ

### Test Scenarios

#### Scenario 1: ทดสอบ LED
```
1. GET /api/v1/led/              → ดูสถานะปัจจุบัน
2. POST /api/v1/led/ (ON)        → เปิด LED
3. GET /api/v1/led/              → ตรวจสอบว่าเปลี่ยนเป็น ON
4. POST /api/v1/led/ (OFF)       → ปิด LED
5. GET /api/v1/led/              → ตรวจสอบว่าเปลี่ยนเป็น OFF
```

#### Scenario 2: ทดสอบ Relay
```
1. GET /api/v1/relay/                    → ดูสถานะ relay ทั้งหมด
2. POST /api/v1/relay/ (relay1, ON)      → เปิด Relay 1
3. POST /api/v1/relay/ (relay2, ON)      → เปิด Relay 2
4. GET /api/v1/relay/                    → ตรวจสอบว่าทั้ง 2 ตัวเปิด
5. POST /api/v1/relay/ (relay1, TOGGLE)  → Toggle Relay 1
```

#### Scenario 3: ทดสอบ CRUD Sensor
```
1. GET /api/v1/sensors/                  → ดูรายการทั้งหมด
2. POST /api/v1/sensors/                 → สร้างข้อมูลใหม่
3. GET /api/v1/sensors/{id}/             → ดูข้อมูลที่สร้าง
4. PATCH /api/v1/sensors/{id}/           → แก้ไขบางส่วน
5. DELETE /api/v1/sensors/{id}/          → ลบข้อมูล
```

---

## 🎯 Use Cases

### Use Case 1: Mobile App Integration
```javascript
// React Native / Flutter
fetch('http://192.168.1.100:8000/api/v1/led/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    command: 'TOGGLE'
  })
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));
```

### Use Case 2: Python Script Automation
```python
import requests

# ควบคุม LED
response = requests.post(
    'http://localhost:8000/api/v1/led/',
    json={'command': 'ON'}
)
print(response.json())

# อ่านข้อมูล Sensor
response = requests.get('http://localhost:8000/api/v1/sensors/latest/')
data = response.json()
print(f"Temperature: {data['data']['temperature']}°C")
```

### Use Case 3: Node.js Integration
```javascript
const axios = require('axios');

async function controlRelay(relay_num, command) {
  try {
    const response = await axios.post('http://localhost:8000/api/v1/relay/', {
      relay_num: relay_num,
      command: command
    });
    console.log(response.data);
  } catch (error) {
    console.error('Error:', error.response.data);
  }
}

controlRelay(1, 'ON');
```

---

## 🔒 Security Notes

### Current Setup:
- ✅ CSRF disabled for API endpoints (`@csrf_exempt`)
- ✅ No authentication required

### Production Recommendations:
1. **Enable Authentication**
   - Add Token-based authentication (JWT)
   - Use Django REST Framework with authentication classes

2. **Add Rate Limiting**
   - Prevent API abuse
   - Use django-ratelimit

3. **Enable HTTPS**
   - Use SSL certificate
   - Force HTTPS in production

4. **Restrict CORS**
   - Allow only specific domains
   - Use django-cors-headers

---

## 📚 Additional Resources

- 📖 [Django Documentation](https://docs.djangoproject.com/)
- 🔗 [MQTT Protocol](https://mqtt.org/)
- 📱 [Postman Documentation](https://learning.postman.com/)
- 🎓 [REST API Best Practices](https://restfulapi.net/)

---

## 💬 Support

หากมีปัญหาหรือคำถาม:
1. ตรวจสอบ Django server ทำงานหรือไม่ (`http://localhost:8000/`)
2. ตรวจสอบ logs ใน terminal
3. ทดสอบด้วย `curl` ก่อนใช้ Postman
4. ตรวจสอบ MQTT connection status

---

## ✅ Checklist

- [ ] Import Postman Collection
- [ ] ตั้งค่า Base URL
- [ ] ทดสอบ GET System Status
- [ ] ทดสอบ LED Control (ON/OFF/TOGGLE)
- [ ] ทดสอบ Relay Control (1, 2, 3)
- [ ] ทดสอบ Get Sensor Data
- [ ] ทดสอบ Create Sensor Data
- [ ] ทดสอบ Update/Delete Sensor

---

**🎉 พร้อมใช้งาน!** เริ่มทดสอบ API กับ Postman ได้เลย!
