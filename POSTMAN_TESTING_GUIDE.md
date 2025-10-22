# 🧪 คู่มือการทดสอบ AI Agent APIs ด้วย Postman

## 📦 ไฟล์ที่ต้องใช้

1. **`AI_Agent_APIs.postman_collection.json`** - Postman Collection หลัก
2. **`AI_Agent_Environment.postman_environment.json`** - Environment settings

---

## 🚀 วิธี Import เข้า Postman

### ขั้นตอนที่ 1: Import Collection

1. เปิด **Postman**
2. คลิกปุ่ม **Import** (มุมซ้ายบน)
3. เลือก **Upload Files**
4. เลือกไฟล์ `AI_Agent_APIs.postman_collection.json`
5. คลิก **Import**

### ขั้นตอนที่ 2: Import Environment

1. คลิกปุ่ม **Import** อีกครั้ง
2. เลือกไฟล์ `AI_Agent_Environment.postman_environment.json`
3. คลิก **Import**

### ขั้นตอนที่ 3: เลือก Environment

1. ดูมุมขวาบน จะมี dropdown **Environment**
2. เลือก **"AI Agent - Local Development"**

---

## 📋 รายการ APIs ใน Collection

### 1. AI Agent APIs

#### 🟢 GET - Get AI Agent Status
```
GET /api/v1/ai/status/
```
**วัตถุประสงค์:** ดูสถานะ AI Agent Scheduler และการตัดสินใจล่าสุด 5 รายการ

**ตัวอย่าง Response:**
```json
{
  "success": true,
  "data": {
    "scheduler": {
      "is_running": true,
      "interval_minutes": 15,
      "next_run": "2024-10-22 11:00:00"
    },
    "recent_decisions": [...]
  }
}
```

---

#### 🟢 GET - Get AI Decisions History
```
GET /api/v1/ai/decisions/?limit=20&offset=0
```
**วัตถุประสงค์:** ดูประวัติการตัดสินใจทั้งหมด พร้อม pagination

**Query Parameters:**
- `limit` - จำนวนรายการต่อหน้า (default=20)
- `offset` - เริ่มจากรายการที่ (default=0)

**ตัวอย่าง Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 5,
      "decision": "ON",
      "confidence": 0.85,
      "reasoning": "อุณหภูมิสูง...",
      "current_temperature": 33.5,
      "current_humidity": 78.0,
      "weather_forecast": {...},
      "action_taken": true,
      "timestamp": "2024-10-22 10:45:00"
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

---

#### 🔵 POST - Trigger AI Analysis Now (Manual)
```
POST /api/v1/ai/analyze-now/
```
**วัตถุประสงค์:** สั่งให้ AI วิเคราะห์ทันที (ไม่รอ schedule 15 นาที)

**Body:** ไม่ต้องส่ง

**ตัวอย่าง Response:**
```json
{
  "success": true,
  "message": "AI analysis triggered successfully",
  "data": {
    "latest_decision": {
      "id": 6,
      "decision": "OFF",
      "confidence": 0.75,
      "reasoning": "อุณหภูมิต่ำ...",
      "timestamp": "2024-10-22 10:50:15"
    }
  }
}
```

---

#### 🟢 GET - Get AI Statistics
```
GET /api/v1/ai/stats/?days=7
```
**วัตถุประสงค์:** ดูสถิติการทำงานของ AI Agent

**Query Parameters:**
- `days` - จำนวนวันย้อนหลัง (default=7)

**ตัวอย่าง Response:**
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

### 2. System Status API

#### 🟢 GET - Get System Status (with AI)
```
GET /api/v1/system/status/
```
**วัตถุประสงค์:** ดูสถานะระบบทั้งหมด รวมถึง Relay 2 ที่ควบคุมโดย AI

---

### 3. Quick Tests (ทดสอบแบบครบวงจร)

**Full AI Agent Test Flow** - folder ที่มี test scripts ครบชุด

รัน folder นี้เพื่อทดสอบ:
1. ✅ ตรวจสอบสถานะระบบ
2. ✅ ตรวจสอบสถานะ AI Agent
3. ✅ สั่ง AI วิเคราะห์ทันที
4. ✅ ดูสถิติการทำงาน
5. ✅ ดูประวัติการตัดสินใจ

**วิธีรัน:**
1. เปิด folder **"Quick Tests"**
2. คลิกขวาที่ **"Full AI Agent Test Flow"**
3. เลือก **"Run folder"**
4. ดูผลการทดสอบใน **Test Results**

---

## 🎯 การทดสอบแบบ Step-by-Step

### Scenario 1: ตรวจสอบว่า AI Agent ทำงานหรือไม่

```bash
1. GET /api/v1/ai/status/
   ✅ ตรวจสอบ scheduler.is_running = true
   ✅ ตรวจสอบ next_run มีค่า
```

### Scenario 2: บังคับให้ AI ตัดสินใจทันที

```bash
1. POST /api/v1/ai/analyze-now/
   ✅ ดู latest_decision
   ✅ เช็ค confidence level
   ✅ อ่าน reasoning (เหตุผล)

2. GET /api/v1/system/status/
   ✅ เช็คว่า relay2 เปลี่ยนหรือไม่
```

### Scenario 3: ดูสถิติการทำงานย้อนหลัง

```bash
1. GET /api/v1/ai/stats/?days=7
   ✅ ดู total_decisions
   ✅ ดู actions_taken (กี่ครั้งที่เปลี่ยนจริง)
   ✅ ดู avg_confidence

2. GET /api/v1/ai/stats/?days=30
   ✅ เปรียบเทียบกับ 7 วัน
```

### Scenario 4: ดูประวัติการตัดสินใจ

```bash
1. GET /api/v1/ai/decisions/?limit=10&offset=0
   ✅ ดูหน้าแรก 10 รายการ

2. GET /api/v1/ai/decisions/?limit=10&offset=10
   ✅ ดูหน้าที่ 2
```

---

## 🧪 Test Scripts ที่รวมอยู่ใน Collection

Collection นี้มี **Automated Tests** สำหรับทุก request:

### ตัวอย่าง Test Scripts:

```javascript
// Test 1: ตรวจสอบ Status Code
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

// Test 2: ตรวจสอบ Response Structure
pm.test("Response has success true", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.success).to.eql(true);
});

// Test 3: ตรวจสอบ Scheduler กำลังทำงาน
pm.test("AI Scheduler is running", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.data.scheduler.is_running).to.eql(true);
});
```

**วิธีดูผล Test:**
1. รัน request
2. ไปที่แท็บ **Test Results** ด้านล่าง
3. ดูว่า ✅ (passed) หรือ ❌ (failed)

---

## 🔧 แก้ไข Base URL (ถ้าต้องการ)

### วิธีที่ 1: แก้ใน Environment
1. คลิก **Environments** ทางซ้าย
2. เลือก **AI Agent - Local Development**
3. แก้ `base_url` เป็น URL ใหม่ (เช่น `http://192.168.1.100:8000`)

### วิธีที่ 2: แก้ใน Collection Variable
1. คลิกขวาที่ Collection **"AI Agent APIs"**
2. เลือก **Edit**
3. ไปแท็บ **Variables**
4. แก้ `base_url`

---

## 📊 ตัวอย่างผลลัพธ์ที่ควรได้

### ✅ กรณี AI Agent ทำงานปกติ:

```json
{
  "success": true,
  "data": {
    "scheduler": {
      "is_running": true,
      "interval_minutes": 15,
      "next_run": "2024-10-22 11:00:00"
    }
  }
}
```

### ❌ กรณี API Key ไม่ถูกต้อง:

AI จะใช้ **Fallback Mode** (กฎอัตโนมัติ) แทน:

```json
{
  "success": true,
  "data": {
    "latest_decision": {
      "reasoning": "ใช้กฎอัตโนมัติ: อุณหภูมิสูง (33.5°C), ความชื้นสูง (78%)",
      "confidence": 0.7
    }
  }
}
```

---

## 🐛 Troubleshooting

### ปัญหา: Connection Refused
**สาเหตุ:** Django Server ไม่ได้เปิด

**วิธีแก้:**
```bash
cd d:\GitHub\DjangoDashboardFramework\django_iot_dashboard
D:/GitHub/DjangoDashboardFramework/.venv/Scripts/python.exe manage.py runserver
```

### ปัญหา: 500 Internal Server Error
**สาเหตุ:** API Keys ไม่ได้ตั้งค่า

**วิธีแก้:**
1. เปิดไฟล์ `.env`
2. ใส่ `GEMINI_API_KEY` และ `OPENWEATHER_API_KEY`
3. Restart Django Server

### ปัญหา: scheduler.is_running = false
**สาเหตุ:** Scheduler ยังไม่ start

**วิธีแก้:**
- Restart Django Server
- ตรวจสอบ logs หา `✅ AI Agent Scheduler started successfully!`

---

## 📚 เอกสารเพิ่มเติม

- **AI Agent Guide:** `AI_AGENT_GUIDE.md`
- **Main Documentation:** `README.md`

---

## ✅ Checklist ก่อนทดสอบ

- [ ] Django Server กำลังรัน (`python manage.py runserver`)
- [ ] ตั้งค่า `GEMINI_API_KEY` ใน `.env`
- [ ] ตั้งค่า `OPENWEATHER_API_KEY` ใน `.env`
- [ ] Import Collection และ Environment เรียบร้อย
- [ ] เลือก Environment: **"AI Agent - Local Development"**
- [ ] MQTT Broker เชื่อมต่อ (ถ้าต้องการทดสอบ Relay 2 จริง)

---

## 🎓 Tips การใช้งาน

1. **ใช้ Console เพื่อดู logs:**
   - เปิด **Postman Console** (View → Show Postman Console)
   - ดู request/response ละเอียด

2. **Save Response เป็น Example:**
   - รัน request
   - คลิก **Save Response** → **Save as Example**
   - ใช้เป็นตัวอย่างในภายหลัง

3. **Collection Runner:**
   - เปิด Collection
   - คลิก **Run** เพื่อรันทุก request ทีเดียว
   - ดูผลสรุปแบบ overview

4. **Monitor:**
   - ตั้ง Monitor เพื่อรัน tests อัตโนมัติทุกๆ 15 นาที
   - จับ performance และความถูกต้องของ AI

---

**สร้างโดย:** GitHub Copilot  
**วันที่:** 22 ตุลาคม 2025  
**เวอร์ชัน:** 1.0.0
