# 🚀 Quick Start: ทดสอบ AI Agent ด้วย curl (5 นาที)

## เริ่มต้นใช้งานด่วน (ไม่ต้องใช้ Postman)

### 1️⃣ ตรวจสอบว่า Django Server กำลังรัน

```bash
# เปิด Terminal และรัน
cd d:\GitHub\DjangoDashboardFramework\django_iot_dashboard
D:/GitHub/DjangoDashboardFramework/.venv/Scripts/python.exe manage.py runserver
```

ดู output ควรเห็น:
```
✅ MQTT Manager initialized successfully!
✅ AI Agent Scheduler started successfully!
Starting development server at http://127.0.0.1:8000/
```

---

## 🧪 ทดสอบ APIs ด้วย curl

### Test 1: ดูสถานะ AI Agent ⏰

```bash
curl http://localhost:8000/api/v1/ai/status/
```

**ผลที่ควรได้:**
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

✅ **ถ้าเห็น `"is_running": true`** = AI Agent ทำงานปกติ!

---

### Test 2: สั่งให้ AI วิเคราะห์ทันที 🤖

```bash
curl -X POST http://localhost:8000/api/v1/ai/analyze-now/
```

**ผลที่ควรได้:**
```json
{
  "success": true,
  "message": "AI analysis triggered successfully",
  "data": {
    "latest_decision": {
      "decision": "OFF",
      "confidence": 0.75,
      "reasoning": "อุณหภูมิต่ำ (27.5°C) อยู่ในเกณฑ์ปกติ...",
      "current_temperature": 27.5,
      "current_humidity": 65.0,
      "timestamp": "2024-10-22 10:50:15"
    }
  }
}
```

✅ **ดูที่:**
- `decision`: ON หรือ OFF
- `confidence`: ความมั่นใจ (0.0-1.0)
- `reasoning`: เหตุผลภาษาไทย

---

### Test 3: ดูสถิติการทำงาน 7 วัน 📊

```bash
curl "http://localhost:8000/api/v1/ai/stats/?days=7"
```

**ผลที่ควรได้:**
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

✅ **ดูที่:**
- `total_decisions`: จำนวนการตัดสินใจทั้งหมด
- `actions_taken`: จำนวนครั้งที่เปลี่ยน Relay 2
- `avg_confidence`: ความมั่นใจเฉลี่ย

---

### Test 4: ดูประวัติการตัดสินใจ 10 รายการล่าสุด 📋

```bash
curl "http://localhost:8000/api/v1/ai/decisions/?limit=10&offset=0"
```

**ผลที่ควรได้:**
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
      "action_taken": true,
      "timestamp": "2024-10-22 10:45:00"
    }
  ],
  "pagination": {
    "total": 100,
    "limit": 10,
    "offset": 0,
    "count": 10
  }
}
```

---

### Test 5: ตรวจสอบสถานะระบบทั้งหมด 🖥️

```bash
curl http://localhost:8000/api/v1/system/status/
```

**ผลที่ควรได้:**
```json
{
  "success": true,
  "data": {
    "led": {...},
    "relays": {
      "relay1": false,
      "relay2": true,  ← ถูกควบคุมโดย AI
      "relay3": false
    },
    "sensors": {...},
    "mqtt": {
      "connected": true
    }
  }
}
```

---

## 📈 ทดสอบแบบ Pretty Print (Windows PowerShell)

```powershell
# ติดตั้ง jq (optional - สำหรับ format JSON สวยๆ)
# หรือใช้ PowerShell แบบนี้:

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/ai/status/" -Method Get
$response | ConvertTo-Json -Depth 10
```

---

## 🔥 ทดสอบแบบต่อเนื่อง (Loop Test)

### ทดสอบ Manual Trigger ทุก 30 วินาที:

**Windows CMD:**
```cmd
@echo off
:loop
curl -X POST http://localhost:8000/api/v1/ai/analyze-now/
echo.
echo Waiting 30 seconds...
timeout /t 30 /nobreak
goto loop
```

**PowerShell:**
```powershell
while ($true) {
    Write-Host "=== Triggering AI Analysis ===" -ForegroundColor Green
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/ai/analyze-now/" -Method Post
    Write-Host "Decision: $($response.data.latest_decision.decision)" -ForegroundColor Yellow
    Write-Host "Confidence: $($response.data.latest_decision.confidence)" -ForegroundColor Yellow
    Write-Host "Reasoning: $($response.data.latest_decision.reasoning)" -ForegroundColor Cyan
    Write-Host ""
    Start-Sleep -Seconds 30
}
```

---

## ✅ Checklist การทดสอบ

**ก่อนเริ่มทดสอบ:**
- [ ] Django Server กำลังรัน
- [ ] เห็นข้อความ `✅ AI Agent Scheduler started successfully!`
- [ ] ตั้งค่า API Keys ใน `.env` แล้ว
  - `GEMINI_API_KEY=xxx`
  - `OPENWEATHER_API_KEY=xxx`

**ทดสอบ APIs:**
- [ ] Test 1: ✅ AI Status - `is_running: true`
- [ ] Test 2: ✅ Manual Trigger - ได้ `latest_decision`
- [ ] Test 3: ✅ Statistics - ได้ `total_decisions`
- [ ] Test 4: ✅ Decision History - ได้ `data` array
- [ ] Test 5: ✅ System Status - ได้ `relays.relay2`

---

## 🐛 แก้ปัญหาเบื้องต้น

### ❌ Connection Refused
```bash
# แก้: เปิด Django Server
cd d:\GitHub\DjangoDashboardFramework\django_iot_dashboard
D:/GitHub/DjangoDashboardFramework/.venv/Scripts/python.exe manage.py runserver
```

### ❌ "is_running": false
```bash
# แก้: Restart Django Server
# ตรวจสอบ logs หา "AI Agent Scheduler started"
```

### ❌ 500 Internal Server Error
```bash
# แก้: ตั้งค่า API Keys
# เปิดไฟล์ .env และใส่:
GEMINI_API_KEY=your_actual_key_here
OPENWEATHER_API_KEY=your_actual_key_here
```

### ⚠️ AI ใช้ Fallback Mode
```json
{
  "reasoning": "ใช้กฎอัตโนมัติ: อุณหภูมิสูง..."
}
```
**สาเหตุ:** `GEMINI_API_KEY` ไม่ถูกต้อง  
**วิธีแก้:** ขอ API Key ใหม่จาก https://makersuite.google.com/app/apikey

---

## 📚 เอกสารเพิ่มเติม

- **คู่มือ AI Agent ฉบับสมบูรณ์:** `AI_AGENT_GUIDE.md`
- **คู่มือทดสอบด้วย Postman:** `POSTMAN_TESTING_GUIDE.md`
- **Postman Collection:** `AI_Agent_APIs.postman_collection.json`

---

## 🎯 Next Steps

1. ✅ ทดสอบ APIs ทั้ง 5 ตัวสำเร็จ
2. 📦 Import Postman Collection (`AI_Agent_APIs.postman_collection.json`)
3. 🔄 รอ 15 นาที ดู AI วิเคราะห์อัตโนมัติ
4. 📊 ตรวจสอบ logs ใน Django Console
5. 🎨 (Optional) สร้าง Dashboard แสดงสถิติ AI

---

**Happy Testing! 🚀**
