# 🚀 API Quick Reference

## 📥 Import to Postman

1. เปิด Postman
2. Click **Import**
3. เลือกไฟล์ `Django_IoT_Dashboard_API.postman_collection.json`
4. ตั้งค่า `base_url` = `http://localhost:8000`

---

## 🔗 API Endpoints Summary

### Base URL
```
http://localhost:8000/api/v1
```

### LED Control
| Method | Endpoint | Body | Description |
|--------|----------|------|-------------|
| GET | `/led/` | - | Get LED status |
| POST | `/led/` | `{"command": "ON"}` | Turn LED ON |
| POST | `/led/` | `{"command": "OFF"}` | Turn LED OFF |
| POST | `/led/` | `{"command": "TOGGLE"}` | Toggle LED |

### Relay Control
| Method | Endpoint | Body | Description |
|--------|----------|------|-------------|
| GET | `/relay/` | - | Get all relays status |
| POST | `/relay/` | `{"relay_num": 1, "command": "ON"}` | Turn Relay 1 ON |
| POST | `/relay/` | `{"relay_num": 2, "command": "OFF"}` | Turn Relay 2 OFF |
| POST | `/relay/` | `{"relay_num": 3, "command": "TOGGLE"}` | Toggle Relay 3 |

### Sensor Data
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/sensors/latest/` | Get latest reading |
| GET | `/sensors/?limit=10&offset=0` | Get list (pagination) |
| GET | `/sensors/stats/` | Get statistics |
| POST | `/sensors/` | Create new data |
| GET | `/sensors/{id}/` | Get by ID |
| PUT/PATCH | `/sensors/{id}/` | Update data |
| DELETE | `/sensors/{id}/` | Delete data |

### System Status
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/system/status/` | Get complete system status |

---

## 💡 Quick Examples

### Control LED
```bash
# Turn ON
curl -X POST http://localhost:8000/api/v1/led/ \
  -H "Content-Type: application/json" \
  -d '{"command":"ON"}'

# Turn OFF
curl -X POST http://localhost:8000/api/v1/led/ \
  -H "Content-Type: application/json" \
  -d '{"command":"OFF"}'
```

### Control Relay
```bash
# Turn Relay 1 ON
curl -X POST http://localhost:8000/api/v1/relay/ \
  -H "Content-Type: application/json" \
  -d '{"relay_num":1,"command":"ON"}'
```

### Get Latest Sensor
```bash
curl http://localhost:8000/api/v1/sensors/latest/
```

### Create Sensor Data
```bash
curl -X POST http://localhost:8000/api/v1/sensors/ \
  -H "Content-Type: application/json" \
  -d '{"temperature":28.5,"humidity":65.3,"device_name":"Test"}'
```

### Get System Status
```bash
curl http://localhost:8000/api/v1/system/status/
```

---

## 🐍 Python Example

```python
import requests

# Control LED
response = requests.post(
    'http://localhost:8000/api/v1/led/',
    json={'command': 'ON'}
)
print(response.json())

# Get latest sensor
response = requests.get('http://localhost:8000/api/v1/sensors/latest/')
print(response.json())
```

**Run full examples:**
```bash
python api_examples.py
```

---

## 🌐 JavaScript Example

```javascript
// Control LED
const response = await fetch('http://localhost:8000/api/v1/led/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({command: 'ON'})
});
const data = await response.json();
console.log(data);
```

**Run in browser:**
- Open `api_examples.js` in browser console
- Call `runExamples()` to test all APIs

---

## 📁 ไฟล์ที่สร้าง

- ✅ `Django_IoT_Dashboard_API.postman_collection.json` - Postman Collection (21 requests)
- ✅ `API_GUIDE.md` - เอกสารคู่มือแบบละเอียด
- ✅ `api_examples.py` - ตัวอย่าง Python พร้อม functions ครบ
- ✅ `api_examples.js` - ตัวอย่าง JavaScript พร้อม HTML demo
- ✅ `API_QUICK_REFERENCE.md` - ไฟล์นี้ (สำหรับอ้างอิงรวดเร็ว)

---

## ✅ Testing Checklist

- [ ] Import Postman Collection
- [ ] ตั้งค่า base_url
- [ ] Test "Get System Status"
- [ ] Test LED Control (ON/OFF/TOGGLE)
- [ ] Test Relay Control (1, 2, 3)
- [ ] Test Get Latest Sensor
- [ ] Test Create Sensor Data
- [ ] Test Get Sensor Statistics
- [ ] Test Update Sensor
- [ ] Test Delete Sensor

---

## 📚 เอกสารเพิ่มเติม

- 📖 **API_GUIDE.md** - คู่มือใช้งานแบบละเอียด
- 🐍 **api_examples.py** - ตัวอย่าง Python
- 🌐 **api_examples.js** - ตัวอย่าง JavaScript
- 📡 **Postman Collection** - พร้อม import

---

**🎉 พร้อมใช้งาน!** Import ไฟล์ .json เข้า Postman แล้วเริ่มทดสอบได้เลย!
