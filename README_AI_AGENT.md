# 🤖 AI Agent Feature - Branch: Step8AddAIAgentSimple

## 🎯 Overview

เพิ่มฟีเจอร์ **AI Agent** ที่ใช้ **Google Gemini AI** วิเคราะห์ข้อมูลเซนเซอร์และพยากรณ์อากาศเพื่อควบคุม **Relay 2** อัตโนมัติ

### ความสามารถหลัก:
- 🧠 **AI Decision Making** - ใช้ Gemini AI วิเคราะห์แบบ real-time
- 🌦️ **Weather Integration** - พิจารณาพยากรณ์อากาศนครศรีธรรมราช (OpenWeatherMap)
- ⏰ **Scheduled Analysis** - ทำงานอัตโนมัติทุก 15 นาที
- 📊 **Decision Logging** - บันทึกทุกการตัดสินใจพร้อมเหตุผล (ภาษาไทย)
- 🔄 **Fallback Mode** - ใช้กฎอัตโนมัติถ้า AI ไม่พร้อม
- 📡 **REST APIs** - ควบคุมและดูสถิติผ่าน API

---

## 📁 ไฟล์ที่เพิ่มเข้ามา

### 🆕 ไฟล์ใหม่:

1. **`.env`** - Environment variables (API Keys)
2. **`iot_dashboard/ai_agent/__init__.py`** - Package initialization
3. **`iot_dashboard/ai_agent/weather_service.py`** - Weather forecast service
4. **`iot_dashboard/ai_agent/gemini_agent.py`** - AI decision engine
5. **`iot_dashboard/ai_agent/scheduler.py`** - Background task scheduler
6. **`AI_AGENT_GUIDE.md`** - คู่มือการใช้งานฉบับสมบูรณ์
7. **`AI_Agent_APIs.postman_collection.json`** - Postman collection
8. **`AI_Agent_Environment.postman_environment.json`** - Postman environment
9. **`POSTMAN_TESTING_GUIDE.md`** - คู่มือทดสอบด้วย Postman
10. **`QUICK_START_TESTING.md`** - คู่มือทดสอบด่วนด้วย curl
11. **`README_AI_AGENT.md`** - สรุปฟีเจอร์ AI Agent (ไฟล์นี้)

### ✏️ ไฟล์ที่แก้ไข:

1. **`iot_dashboard/models.py`** - เพิ่ม `AIDecisionLog` model
2. **`iot_dashboard/views_simple.py`** - เพิ่ม 4 AI API endpoints
3. **`iot_dashboard/urls.py`** - เพิ่ม routes สำหรับ AI APIs
4. **`iot_dashboard/apps.py`** - เริ่ม AI Scheduler ตอน Django start
5. **`iot_dashboard/migrations/0006_aidecisionlog.py`** - Database migration

---

## 🚀 Quick Start

### 1. ตรวจสอบ API Keys (✅ ตั้งค่าแล้ว)

```env
GEMINI_API_KEY=AIzaSyDS2wKByNE0QIDMTJegqaamZgENUNs00xc
OPENWEATHER_API_KEY=1bef650d2c6ea7a91f58252948c2d325
```

### 2. รัน Django Server

```bash
cd d:\GitHub\DjangoDashboardFramework\django_iot_dashboard
D:/GitHub/DjangoDashboardFramework/.venv/Scripts/python.exe manage.py runserver
```

ดู console ควรเห็น:
```
✅ MQTT Manager initialized successfully!
✅ AI Agent Scheduler started successfully!
⏰ Next AI analysis at: 2024-10-22 11:00:00
```

### 3. ทดสอบ API (เลือก 1 ใน 2 วิธี)

#### วิธีที่ 1: ใช้ curl (รวดเร็ว)

```bash
# ดูสถานะ AI Agent
curl http://localhost:8000/api/v1/ai/status/

# สั่งให้ AI วิเคราะห์ทันที
curl -X POST http://localhost:8000/api/v1/ai/analyze-now/

# ดูสถิติ 7 วัน
curl "http://localhost:8000/api/v1/ai/stats/?days=7"
```

📖 **คู่มือเต็ม:** `QUICK_START_TESTING.md`

#### วิธีที่ 2: ใช้ Postman (ครบครัน)

1. Import `AI_Agent_APIs.postman_collection.json`
2. Import `AI_Agent_Environment.postman_environment.json`
3. เลือก Environment: **"AI Agent - Local Development"**
4. รัน Collection หรือ request ทีละตัว

📖 **คู่มือเต็ม:** `POSTMAN_TESTING_GUIDE.md`

---

## 🌟 API Endpoints

### 1. ดูสถานะ AI Agent
```http
GET /api/v1/ai/status/
```

### 2. ดูประวัติการตัดสินใจ
```http
GET /api/v1/ai/decisions/?limit=20&offset=0
```

### 3. สั่งให้ AI วิเคราะห์ทันที
```http
POST /api/v1/ai/analyze-now/
```

### 4. ดูสถิติการทำงาน
```http
GET /api/v1/ai/stats/?days=7
```

📖 **API Documentation:** ดูรายละเอียดครบใน `AI_AGENT_GUIDE.md`

---

## 📊 Database Schema

### ตาราง: `AIDecisionLog`

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary Key |
| current_temperature | Float | อุณหภูมิ ณ เวลาตัดสินใจ (°C) |
| current_humidity | Float | ความชื้น ณ เวลาตัดสินใจ (%) |
| weather_forecast | JSON | ข้อมูลพยากรณ์อากาศ |
| decision | Char(3) | 'ON' หรือ 'OFF' |
| confidence | Float | ความมั่นใจ (0.0-1.0) |
| reasoning | Text | เหตุผลภาษาไทย |
| relay2_previous_status | Boolean | สถานะ Relay 2 ก่อนหน้า |
| relay2_new_status | Boolean | สถานะ Relay 2 ใหม่ |
| action_taken | Boolean | มีการเปลี่ยนแปลงหรือไม่ |
| timestamp | DateTime | เวลาที่บันทึก |

---

## 🧠 AI Decision Logic

### กฎการตัดสินใจ:

| เงื่อนไข | การตัดสินใจ |
|---------|------------|
| อุณหภูมิ > 32°C **และ** ความชื้น > 75% | ⚡ **เปิด** Relay 2 (ON) |
| แนวโน้มอุณหภูมิ **เพิ่มขึ้น** | 🔥 พิจารณา **เปิด** Relay 2 |
| อุณหภูมิ < 28°C | ❄️ **ปิด** Relay 2 (OFF) |
| มี**โอกาสฝนตก** > 30% | 🌧️ พิจารณา **ปิด** Relay 2 |

**หมายเหตุ:** AI จะพิจารณาปัจจัยหลายอย่างร่วมกัน ไม่ใช่กฎตายตัว

---

## 🔄 Workflow

```
1. ⏰ Scheduler ทำงานทุก 15 นาที
   │
   ├─> 📊 ดึงข้อมูลเซนเซอร์ล่าสุด (Temperature + Humidity)
   │
   ├─> 🌦️ ดึงพยากรณ์อากาศนครศรีธรรมราช (6 ชั่วโมงข้างหน้า)
   │
   ├─> 🧠 Gemini AI วิเคราะห์และตัดสินใจ
   │   ├─ Success → ได้ decision + confidence + reasoning
   │   └─ Failed  → ใช้กฎ Fallback (อัตโนมัติ)
   │
   ├─> 📝 บันทึกผลลง AIDecisionLog
   │
   ├─> 🔍 เช็คว่า Relay 2 ต้องเปลี่ยนหรือไม่
   │
   └─> 📡 ถ้าเปลี่ยน → ส่ง MQTT command ไป ESP32
```

---

## 📈 ตัวอย่าง Response

### GET /api/v1/ai/status/

```json
{
  "success": true,
  "data": {
    "scheduler": {
      "is_running": true,
      "interval_minutes": 15,
      "next_run": "2024-10-22 11:00:00"
    },
    "recent_decisions": [
      {
        "id": 5,
        "decision": "ON",
        "confidence": 0.85,
        "reasoning": "อุณหภูมิสูง (33.5°C) และความชื้นสูง (78%), แนวโน้มอุณหภูมิเพิ่มขึ้น ควรเปิด Relay 2",
        "current_temperature": 33.5,
        "current_humidity": 78.0,
        "action_taken": true,
        "timestamp": "2024-10-22 10:45:00"
      }
    ]
  }
}
```

### POST /api/v1/ai/analyze-now/

```json
{
  "success": true,
  "message": "AI analysis triggered successfully",
  "data": {
    "latest_decision": {
      "id": 6,
      "decision": "OFF",
      "confidence": 0.75,
      "reasoning": "อุณหภูมิต่ำ (27.5°C) อยู่ในเกณฑ์ปกติ มีโอกาสฝนตก ควรปิด Relay 2",
      "timestamp": "2024-10-22 10:50:15"
    }
  }
}
```

### GET /api/v1/ai/stats/?days=7

```json
{
  "success": true,
  "data": {
    "total_decisions": 672,
    "actions_taken": 45,
    "on_decisions": 320,
    "off_decisions": 352,
    "avg_confidence": 0.815,
    "period_days": 7
  }
}
```

---

## 🔧 Configuration

### ตั้งค่าเวลาตรวจสอบ (default: 15 นาที)

แก้ไขในไฟล์ `.env`:
```env
AI_AGENT_INTERVAL_MINUTES=30  # เปลี่ยนเป็น 30 นาที
```

### เปลี่ยนสถานที่พยากรณ์อากาศ

```env
WEATHER_LOCATION=Bangkok,TH  # เปลี่ยนเป็นกรุงเทพฯ
```

---

## 📦 Dependencies

```txt
google-generativeai==0.3.0+    # Gemini AI SDK
requests==2.31.0+              # HTTP requests
python-dotenv==1.0.0+          # Environment variables
apscheduler==3.10.0+           # Task scheduler
Django==5.2.7                  # Web framework
```

---

## 🆚 Relay 1 vs Relay 2

| Feature | Relay 1 (Threshold Alarm) | Relay 2 (AI Agent) |
|---------|---------------------------|-------------------|
| **วิธีควบคุม** | Threshold Auto/Manual Mode | AI Decision (Gemini) |
| **พิจารณาจาก** | ค่าเซนเซอร์เพียงอย่างเดียว | เซนเซอร์ + พยากรณ์อากาศ |
| **ความถี่** | ทุกครั้งที่มีข้อมูลใหม่ | ทุก 15 นาที |
| **การตัดสินใจ** | กฎตายตัว (>/<) | AI วิเคราะห์แบบ Dynamic |
| **บันทึกข้อมูล** | Alarm Log | AIDecisionLog |
| **เหตุผล** | ระบุเงื่อนไขที่เกิน | AI อธิบายภาษาไทย |

---

## 🐛 Troubleshooting

### ❌ AI Scheduler ไม่ start

**อาการ:** ไม่เห็นข้อความ `✅ AI Agent Scheduler started successfully!`

**วิธีแก้:**
1. ตรวจสอบว่าไม่มี syntax error ใน `scheduler.py`
2. Restart Django Server
3. ดู error logs

### ⚠️ AI ใช้ Fallback Mode

**อาการ:** Reasoning ขึ้นว่า "ใช้กฎอัตโนมัติ: ..."

**วิธีแก้:**
1. ตรวจสอบ `GEMINI_API_KEY` ใน `.env`
2. ทดสอบ API Key:
```bash
curl -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Hello"}]}]}'
```

### 🌧️ ไม่มีข้อมูลพยากรณ์อากาศ

**อาการ:** `weather_forecast` เป็น `{}`

**วิธีแก้:**
1. ตรวจสอบ `OPENWEATHER_API_KEY` ใน `.env`
2. ทดสอบ API Key:
```bash
curl "https://api.openweathermap.org/data/2.5/weather?q=Nakhon%20Si%20Thammarat,TH&appid=YOUR_KEY"
```

---

## 📚 Documentation

| ไฟล์ | คำอธิบาย |
|------|----------|
| `AI_AGENT_GUIDE.md` | 📖 คู่มือการใช้งานฉบับสมบูรณ์ |
| `POSTMAN_TESTING_GUIDE.md` | 🧪 คู่มือทดสอบด้วย Postman |
| `QUICK_START_TESTING.md` | ⚡ คู่มือทดสอบด่วนด้วย curl |
| `README_AI_AGENT.md` | 📄 สรุปฟีเจอร์ (ไฟล์นี้) |

---

## ✅ Checklist

- [x] ติดตั้ง Python packages
- [x] ตั้งค่า API Keys ใน `.env`
- [x] สร้าง Database Migration
- [x] เพิ่ม AIDecisionLog Model
- [x] สร้าง AI Agent APIs
- [x] เพิ่ม URL routes
- [x] เริ่ม Scheduler ใน apps.py
- [x] สร้าง Postman Collection
- [x] เขียน Documentation

---

## 🎯 Features Summary

✅ **AI-Powered Decision Making** - ใช้ Gemini AI วิเคราะห์แบบอัจฉริยะ  
✅ **Weather Integration** - พิจารณาพยากรณ์อากาศ  
✅ **Automatic Scheduling** - ทำงานอัตโนมัติทุก 15 นาที  
✅ **Decision Logging** - บันทึกทุกการตัดสินใจพร้อมเหตุผล  
✅ **Fallback Mode** - ใช้กฎอัตโนมัติถ้า AI ล้มเหลว  
✅ **REST APIs** - ควบคุมและดูสถิติผ่าน API  
✅ **Manual Trigger** - สั่งให้ AI วิเคราะห์ทันที  
✅ **Statistics** - ดูสถิติการทำงานย้อนหลัง  
✅ **Postman Collection** - ทดสอบง่ายด้วย Postman  
✅ **Comprehensive Docs** - เอกสารครบครัน  

---

## 🚀 Next Steps

1. ✅ ทดสอบ APIs ทั้งหมด
2. 📊 สร้าง Dashboard แสดงสถิติ AI
3. 📱 เพิ่ม Mobile App สำหรับดูการตัดสินใจ
4. 🔔 เพิ่ม Alert/Notification เมื่อ AI ตัดสินใจ
5. 📈 เพิ่ม Chart แสดงประวัติการตัดสินใจ
6. 🤖 ปรับแต่งกฎการตัดสินใจให้เหมาะกับสถานการณ์

---

**สร้างโดย:** GitHub Copilot  
**Branch:** Step8AddAIAgentSimple  
**วันที่:** 22 ตุลาคม 2025  
**เวอร์ชัน:** 1.0.0
