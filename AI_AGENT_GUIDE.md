# AI Agent สำหรับควบคุม Relay 2 อัตโนมัติ

## 📋 สารบัญ
- [ภาพรวมระบบ](#ภาพรวมระบบ)
- [การติดตั้งและการตั้งค่า](#การติดตั้งและการตั้งค่า)
- [วิธีใช้งาน](#วิธีใช้งาน)
- [API Endpoints](#api-endpoints)
- [ตัวอย่างการใช้งาน](#ตัวอย่างการใช้งาน)

---

## 🎯 ภาพรวมระบบ

AI Agent ระบบนี้ใช้ **Google Gemini AI** ในการวิเคราะห์ข้อมูล:
- **ข้อมูลเซนเซอร์** (อุณหภูมิและความชื้นภายในอาคาร)
- **ข้อมูลพยากรณ์อากาศ** จากจังหวัดนครศรีธรรมราช (OpenWeatherMap API)

เพื่อตัดสินใจควบคุม **Relay 2** อัตโนมัติ (เปิด/ปิด) ทุก **15 นาที** โดยพิจารณาจาก:
- อุณหภูมิและความชื้นปัจจุบัน
- แนวโน้มอุณหภูมิในอนาคต (6 ชั่วโมงข้างหน้า)
- โอกาสการเกิดฝน

---

## 🚀 การติดตั้งและการตั้งค่า

### 1. ติดตั้ง Python Packages (เสร็จแล้ว ✅)
```bash
pip install google-generativeai requests python-dotenv apscheduler
```

### 2. ตั้งค่า API Keys ในไฟล์ `.env`

แก้ไขไฟล์ `.env` ในโฟลเดอร์รากของโปรเจค:

```env
# Google Gemini AI API Key
# Get your API key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_actual_gemini_api_key_here

# OpenWeatherMap API Key
# Get your API key from: https://home.openweathermap.org/api_keys
OPENWEATHER_API_KEY=your_actual_openweather_api_key_here

# Weather Location for Forecast
WEATHER_LOCATION=Nakhon Si Thammarat,TH

# AI Agent Settings
AI_AGENT_INTERVAL_MINUTES=15
```

#### วิธีขอ API Keys:

**Google Gemini API Key:**
1. ไปที่ https://makersuite.google.com/app/apikey
2. Sign in ด้วย Google Account
3. คลิก "Create API Key"
4. คัดลอก API Key และใส่ใน `.env`

**OpenWeatherMap API Key:**
1. ไปที่ https://home.openweathermap.org/users/sign_up
2. สมัครสมาชิก (ฟรี)
3. ไปที่ https://home.openweathermap.org/api_keys
4. คัดลอก API Key และใส่ใน `.env`

### 3. รัน Migration (เสร็จแล้ว ✅)
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. เริ่มใช้งาน Django Server
```bash
python manage.py runserver
```

AI Agent Scheduler จะเริ่มทำงานอัตโนมัติทันทีที่ Django Server รัน!

---

## 📖 วิธีใช้งาน

### การทำงานอัตโนมัติ (Automatic Mode)

AI Agent จะทำงานทุก **15 นาที** โดยอัตโนมัติ:

1. **ดึงข้อมูลเซนเซอร์ล่าสุด** (อุณหภูมิ + ความชื้น)
2. **ดึงข้อมูลพยากรณ์อากาศ** นครศรีธรรมราช (6 ชั่วโมงข้างหน้า)
3. **ใช้ Gemini AI วิเคราะห์** และตัดสินใจว่าควรเปิดหรือปิด Relay 2
4. **บันทึกผลการตัดสินใจ** ลงฐานข้อมูล พร้อมเหตุผล (ภาษาไทย)
5. **ส่งคำสั่ง MQTT** ไปยัง ESP32 (ถ้าสถานะเปลี่ยน)

### กฎการตัดสินใจของ AI:

AI จะพิจารณาจากหลายปัจจัย:

| เงื่อนไข | การตัดสินใจ |
|---------|------------|
| อุณหภูมิ > 32°C **และ** ความชื้น > 75% | **เปิด** Relay 2 (ON) |
| แนวโน้มอุณหภูมิ **เพิ่มขึ้น** | พิจารณา **เปิด** Relay 2 |
| อุณหภูมิ < 28°C | **ปิด** Relay 2 (OFF) |
| มี**โอกาสฝนตก** > 30% | พิจารณา **ปิด** Relay 2 (อุณหภูมิจะลดลง) |

**หมายเหตุ:** ถ้า Gemini AI ไม่สามารถทำงานได้ (เช่น API Key ไม่ถูกต้อง) ระบบจะใช้กฎข้างต้นแบบอัตโนมัติ

---

## 🔌 API Endpoints

### 1. ดูสถานะ AI Agent
**GET** `/api/v1/ai/status/`

**Response:**
```json
{
  "success": true,
  "data": {
    "scheduler": {
      "is_running": true,
      "interval_minutes": 15,
      "next_run": "2024-01-15 11:00:00"
    },
    "recent_decisions": [
      {
        "id": 123,
        "decision": "ON",
        "confidence": 0.85,
        "reasoning": "อุณหภูมิสูง (33.5°C) และความชื้นสูง (78%), แนวโน้มอุณหภูมิเพิ่มขึ้น",
        "current_temperature": 33.5,
        "current_humidity": 78.0,
        "action_taken": true,
        "timestamp": "2024-01-15 10:45:00"
      }
    ]
  }
}
```

### 2. ดูประวัติการตัดสินใจ
**GET** `/api/v1/ai/decisions/?limit=20&offset=0`

**Query Parameters:**
- `limit`: จำนวนรายการต่อหน้า (default=20)
- `offset`: เริ่มจากรายการที่ (default=0)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 123,
      "decision": "ON",
      "confidence": 0.85,
      "reasoning": "อุณหภูมิสูง...",
      "current_temperature": 33.5,
      "current_humidity": 78.0,
      "weather_forecast": {
        "temperature_trend": "increasing",
        "will_rain": false
      },
      "relay2_previous_status": false,
      "relay2_new_status": true,
      "action_taken": true,
      "timestamp": "2024-01-15 10:45:00"
    }
  ],
  "pagination": {
    "total": 100,
    "limit": 20,
    "offset": 0,
    "count": 20
  }
}
```

### 3. สั่งให้ AI วิเคราะห์ทันที (Manual Trigger)
**POST** `/api/v1/ai/analyze-now/`

**Response:**
```json
{
  "success": true,
  "message": "AI analysis triggered successfully",
  "data": {
    "latest_decision": {
      "id": 124,
      "decision": "OFF",
      "confidence": 0.75,
      "reasoning": "อุณหภูมิต่ำ (27.5°C) อยู่ในเกณฑ์ปกติ",
      "timestamp": "2024-01-15 10:50:00"
    }
  }
}
```

### 4. ดูสถิติการทำงาน
**GET** `/api/v1/ai/stats/?days=7`

**Query Parameters:**
- `days`: จำนวนวันย้อนหลัง (default=7)

**Response:**
```json
{
  "success": true,
  "data": {
    "total_decisions": 100,
    "actions_taken": 25,
    "on_decisions": 60,
    "off_decisions": 40,
    "avg_confidence": 0.82,
    "period_days": 7
  }
}
```

---

## 💡 ตัวอย่างการใช้งาน

### ตัวอย่างที่ 1: ตรวจสอบสถานะ AI Agent ด้วย curl

```bash
curl -X GET http://localhost:8000/api/v1/ai/status/
```

### ตัวอย่างที่ 2: สั่งให้ AI วิเคราะห์ทันที

```bash
curl -X POST http://localhost:8000/api/v1/ai/analyze-now/
```

### ตัวอย่างที่ 3: ดูสถิติ AI ย้อนหลัง 30 วัน

```bash
curl -X GET "http://localhost:8000/api/v1/ai/stats/?days=30"
```

### ตัวอย่างที่ 4: ดูประวัติการตัดสินใจ

```bash
curl -X GET "http://localhost:8000/api/v1/ai/decisions/?limit=10&offset=0"
```

### ตัวอย่างที่ 5: ใช้ Postman

1. Import Postman Collection: `IoT_Dashboard_APIs.postman_collection.json`
2. ใน Collection จะมี folder ชื่อ **"AI Agent"**
3. ทดสอบ API ทั้ง 4 endpoints ได้เลย

---

## 🔧 การแก้ไขปัญหา (Troubleshooting)

### ปัญหา: AI Agent ไม่ทำงาน
**วิธีแก้:**
1. ตรวจสอบว่า API Keys ถูกต้องใน `.env`
2. ตรวจสอบ logs:
```bash
python manage.py runserver
```
ดู output ใน console หา `✅ AI Agent Scheduler started successfully!`

### ปัญหา: ไม่มีข้อมูลพยากรณ์อากาศ
**วิธีแก้:**
1. ตรวจสอบ `OPENWEATHER_API_KEY` ใน `.env`
2. ทดสอบ API Key ด้วย:
```bash
curl "https://api.openweathermap.org/data/2.5/weather?q=Nakhon%20Si%20Thammarat,TH&appid=YOUR_API_KEY"
```

### ปัญหา: AI ใช้กฎอัตโนมัติแทนที่จะใช้ Gemini
**วิธีแก้:**
1. ตรวจสอบ `GEMINI_API_KEY` ใน `.env`
2. ตรวจสอบ logs หาคำว่า `Gemini AI initialized successfully`
3. ถ้าไม่มี แสดงว่า API Key ไม่ถูกต้อง

---

## 📊 โครงสร้างโค้ด

```
iot_dashboard/
├── ai_agent/
│   ├── __init__.py              # Package initialization
│   ├── weather_service.py       # WeatherService (OpenWeatherMap)
│   ├── gemini_agent.py          # GeminiRelayAgent (AI Decision)
│   └── scheduler.py             # AIAgentScheduler (Background Task)
├── models.py                    # AIDecisionLog Model
├── views_simple.py              # AI Agent API Endpoints
├── urls.py                      # URL Routes
└── apps.py                      # Django App Config (เริ่ม Scheduler)
```

---

## 🎓 ข้อมูลเพิ่มเติม

### ความแตกต่างระหว่าง Relay 1 และ Relay 2:

| Feature | Relay 1 (Threshold Alarm) | Relay 2 (AI Agent) |
|---------|---------------------------|-------------------|
| **วิธีควบคุม** | Threshold Auto/Manual Mode | AI Decision (Gemini) |
| **พิจารณาจาก** | ค่าเซนเซอร์เพียงอย่างเดียว | เซนเซอร์ + พยากรณ์อากาศ |
| **ความถี่การตรวจสอบ** | ทุกครั้งที่มีข้อมูลใหม่ | ทุก 15 นาที (กำหนดเองได้) |
| **เหตุผลการตัดสินใจ** | กฎตายตัว (>/<) | AI วิเคราะห์แบบ Dynamic |
| **บันทึกข้อมูล** | Alarm Log | AIDecisionLog |

### ตั้งค่าเวลาตรวจสอบใหม่:

แก้ไขใน `.env`:
```env
AI_AGENT_INTERVAL_MINUTES=30  # เปลี่ยนเป็น 30 นาที
```

---

## ✅ สรุป

คุณสมบัติหลัก:
- ✅ AI วิเคราะห์และตัดสินใจอัตโนมัติ (Gemini)
- ✅ พิจารณาข้อมูลพยากรณ์อากาศ (OpenWeatherMap)
- ✅ ทำงานทุก 15 นาที (กำหนดเองได้)
- ✅ บันทึกประวัติและเหตุผลการตัดสินใจ
- ✅ Fallback เป็นกฎอัตโนมัติถ้า AI ล้มเหลว
- ✅ REST API สำหรับควบคุมและดูสถิติ

---

**เอกสารนี้สร้างโดย:** GitHub Copilot  
**วันที่:** 2024  
**เวอร์ชัน:** 1.0.0
