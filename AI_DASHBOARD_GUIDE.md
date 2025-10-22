# 🤖 AI Agent Dashboard - User Guide

## 📖 ภาพรวม

AI Agent Dashboard เป็นหน้าเว็บที่แสดงผลการทำงานและการวิเคราะห์ของ AI Agent ที่ใช้ Google Gemini AI ควบคุม Relay 2 โดยอัตโนมัติตามสภาพอากาศ

---

## 🌟 ฟีเจอร์หลัก

### 1. **Real-time Status Monitoring**
แสดงสถานะแบบเรียลไทม์:
- ✅ AI Agent Status (กำลังทำงาน/หยุดทำงาน)
- ⚡ Relay 2 Status (เปิด/ปิด)
- 🎯 Last Decision (การตัดสินใจล่าสุด)
- 📊 Confidence Score (ความมั่นใจในการตัดสินใจ)

### 2. **Weather Information**
แสดงข้อมูลสภาพอากาศ Nakhon Si Thammarat แบบเรียลไทม์:
- 🌡️ อุณหภูมิ (Temperature)
- 💧 ความชื้น (Humidity)
- ☁️ สภาพอากาศ (Weather Condition)
- 🌧️ โอกาสฝนตก (Rain Probability)

### 3. **Decision Timeline**
แสดงประวัติการตัดสินใจของ AI Agent:
- 📜 10 การตัดสินใจล่าสุด
- ⏰ เวลาที่ตัดสินใจ
- 💭 เหตุผล (AI Reasoning)
- 🎯 ระดับความมั่นใจ (Confidence Score)
- 📊 Confidence Bar (แสดงเป็น Progress Bar)

### 4. **Statistics**
สถิติการทำงาน 7 วันล่าสุด:
- 📊 Total Decisions - จำนวนการตัดสินใจทั้งหมด
- 🟢 ON Decisions - จำนวนครั้งที่ตัดสินใจเปิด
- ⚫ OFF Decisions - จำนวนครั้งที่ตัดสินใจปิด
- 🎯 Average Confidence - ความมั่นใจเฉลี่ย

### 5. **Charts & Graphs**
กราฟแสดงแนวโน้ม:
- 📈 Decision Trends - กราฟแท่งแสดงการตัดสินใจรายวัน (7 วัน)
- 🎯 Confidence Trend - กราฟเส้นแสดงค่าความมั่นใจเฉลี่ยรายวัน

### 6. **Manual Control**
ปุ่มควบคุมด้วยตนเอง:
- 🤖 **Trigger AI Analysis** - สั่งให้ AI วิเคราะห์ทันที
- 📋 **View All Decisions** - ดูประวัติการตัดสินใจทั้งหมด (JSON)
- 📊 **View Statistics** - ดูสถิติแบบละเอียด (JSON)

---

## 🚀 การเข้าใช้งาน

### วิธีที่ 1: จากหน้า Main Dashboard
```
http://localhost:8000/
```
คลิกปุ่ม **🤖 AI Agent Dashboard** ที่มุมขวาบน

### วิธีที่ 2: เข้าโดยตรง
```
http://localhost:8000/ai/
```

---

## 📊 การอ่านค่าต่างๆ

### AI Agent Status
- ✅ **ACTIVE** (สีเขียว) - AI กำลังทำงาน วิเคราะห์ทุก 15 นาที
- ❌ **INACTIVE** (สีแดง) - AI ไม่ทำงาน ตรวจสอบ console logs

### Relay 2 Status
- 🟢 **ON** (สีเหลือง) - Relay 2 เปิดอยู่
- ⚫ **OFF** (สีเทา) - Relay 2 ปิดอยู่

### Last Decision
- 🟢 **Turn ON** (สีเขียว) - AI ตัดสินใจเปิด Relay 2
- ⚫ **Turn OFF** (สีแดง) - AI ตัดสินใจปิด Relay 2

### Confidence Score
- 🎯 **80-100%** - ความมั่นใจสูงมาก (AI มั่นใจในการตัดสินใจ)
- 🎯 **60-79%** - ความมั่นใจปานกลาง
- 🎯 **0-59%** - ความมั่นใจต่ำ (อาจใช้ fallback logic)

---

## 🔄 Auto-Update Feature

Dashboard จะอัปเดทข้อมูลอัตโนมัติทุก **10 วินาที**:
- ✅ AI Status
- ✅ Relay Status
- ✅ Decision Timeline
- ✅ Statistics
- ✅ Charts

คุณสามารถกด **🔄 Refresh Now** เพื่ออัปเดททันทีได้

---

## 🎮 การใช้งานปุ่มควบคุม

### 1. Trigger AI Analysis
```javascript
// คลิกปุ่ม "🤖 Trigger AI Analysis"
// AI จะ:
1. ดึงข้อมูลสภาพอากาศจาก OpenWeatherMap
2. ส่งข้อมูลให้ Gemini AI วิเคราะห์
3. ตัดสินใจเปิด/ปิด Relay 2
4. บันทึกผลลงฐานข้อมูล
5. อัปเดท Dashboard ทันที
```

**เมื่อใช้:**
- ต้องการให้ AI วิเคราะห์ทันที (ไม่รอ 15 นาที)
- ทดสอบการทำงานของ AI
- ดูผลการตัดสินใจทันทีหลังเปลี่ยนแปลงสภาพอากาศ

### 2. View All Decisions
```javascript
// คลิกปุ่ม "📋 View All Decisions"
// จะเปิด API endpoint ใหม่แสดง:
{
  "status": "success",
  "data": [...],      // ประวัติการตัดสินใจทั้งหมด
  "pagination": {...} // ข้อมูล pagination
}
```

**เมื่อใช้:**
- ต้องการดูประวัติการตัดสินใจทั้งหมดแบบละเอียด
- Export ข้อมูลเพื่อวิเคราะห์เพิ่มเติม
- Debug ปัญหาการตัดสินใจของ AI

### 3. View Statistics
```javascript
// คลิกปุ่ม "📊 View Statistics"
// จะเปิด API endpoint ใหม่แสดง:
{
  "status": "success",
  "data": {
    "total_decisions": 120,
    "on_decisions": 68,
    "off_decisions": 52,
    "avg_confidence": 0.87,
    "daily_breakdown": [...]
  }
}
```

**เมื่อใช้:**
- ต้องการดูสถิติแบบละเอียด
- วิเคราะห์ประสิทธิภาพของ AI
- สร้างรายงานการทำงาน

---

## 📈 การอ่านกราฟ

### Decision Trends Chart (กราฟแท่ง)
- **แกน X**: วันที่ (7 วันล่าสุด)
- **แกน Y**: จำนวนการตัดสินใจ
- **แท่งสีเขียว**: จำนวนครั้งที่ตัดสินใจเปิด (ON)
- **แท่งสีแดง**: จำนวนครั้งที่ตัดสินใจปิด (OFF)

**การแปลผล:**
- แท่งสูง = AI ตัดสินใจบ่อยในวันนั้น
- สีเขียวสูง = สภาพอากาศร้อนหรือฝนตก (ตัดสินใจเปิดบ่อย)
- สีแดงสูง = สภาพอากาศดี (ตัดสินใจปิดบ่อย)

### Confidence Score Trend Chart (กราฟเส้น)
- **แกน X**: วันที่ (7 วันล่าสุด)
- **แกน Y**: ความมั่นใจเฉลี่ย (0-100%)
- **เส้นสีเหลือง**: ค่าเฉลี่ยความมั่นใจในแต่ละวัน

**การแปลผล:**
- เส้นสูง (>80%) = AI มั่นใจในการตัดสินใจ
- เส้นต่ำ (<60%) = สภาพอากาศยากต่อการตัดสินใจ
- เส้นขึ้นๆ ลงๆ = สภาพอากาศเปลี่ยนแปลงบ่อย

---

## 💡 Tips & Best Practices

### 1. ติดตามสถานะ
✅ เช็ค AI Status เป็นระยะว่า ACTIVE
✅ ดู Confidence Score หากต่ำกว่า 60% บ่อย อาจต้องปรับ prompt
✅ ตรวจสอบ Relay Status ว่าตรงกับการตัดสินใจของ AI

### 2. วิเคราะห์ Decision Timeline
✅ อ่าน AI Reasoning เพื่อเข้าใจเหตุผลการตัดสินใจ
✅ ดู Confidence Bar เพื่อประเมินความมั่นใจ
✅ เปรียบเทียบกับสภาพอากาศจริง

### 3. ใช้ Manual Trigger อย่างชาญฉลาด
⚠️ อย่าใช้บ่อยเกินไป (อาจเกิน API quota)
✅ ใช้เมื่อต้องการทดสอบหรือสภาพอากาศเปลี่ยนแปลงกะทันหัน
✅ ตรวจสอบผลลัพธ์หลัง Trigger

### 4. วิเคราะห์กราฟ
✅ ดูแนวโน้ม 7 วัน เพื่อเข้าใจพฤติกรรม AI
✅ หาจุดผิดปกติ (anomaly) เช่น ON/OFF ผิดปกติ
✅ เปรียบเทียบกับสถิติเดือนก่อนหน้า

---

## 🔧 Troubleshooting

### ปัญหา: AI Status แสดง INACTIVE
**สาเหตุ:**
- Scheduler ไม่เริ่มทำงาน
- มี error ใน console

**วิธีแก้:**
1. ตรวจสอบ Django console logs
2. หา error message ที่มี "AI Agent Scheduler"
3. Restart Django server: `python manage.py runserver`
4. ตรวจสอบ API keys ใน `.env`

### ปัญหา: Weather ไม่แสดงข้อมูล
**สาเหตุ:**
- API key ไม่ถูกต้อง
- Network error

**วิธีแก้:**
1. ตรวจสอบ `OPENWEATHER_API_KEY` ใน `.env`
2. Test API manually:
   ```bash
   curl "http://api.openweathermap.org/data/2.5/weather?q=Nakhon%20Si%20Thammarat,TH&appid=YOUR_API_KEY"
   ```

### ปัญหา: Dashboard ไม่ Auto-update
**สาเหตุ:**
- JavaScript error
- API endpoint ไม่ตอบสนอง

**วิธีแก้:**
1. เปิด Browser Console (F12)
2. ดู error messages
3. ตรวจสอบ Network tab
4. กด Refresh Now เพื่อ force update

### ปัญหา: Confidence Score ต่ำ (<50%) บ่อย
**สาเหตุ:**
- Gemini AI ไม่มั่นใจในการตัดสินใจ
- ข้อมูลสภาพอากาศไม่ชัดเจน

**วิธีแก้:**
1. ตรวจสอบ AI Reasoning ว่าคิดอย่างไร
2. ปรับ prompt ใน `gemini_agent.py`
3. เพิ่ม context ให้ชัดเจนขึ้น

### ปัญหา: Charts ไม่แสดง
**สาเหตุ:**
- Chart.js ไม่โหลด
- ข้อมูลไม่เพียงพอ

**วิธีแก้:**
1. ตรวจสอบ internet connection (Chart.js load จาก CDN)
2. ดู Browser Console สำหรับ Chart.js errors
3. ตรวจสอบว่ามีข้อมูลอย่างน้อย 2 วัน

---

## 📱 Mobile Responsive

Dashboard รองรับ Mobile devices:
- ✅ Auto-adjust layout สำหรับหน้าจอเล็ก
- ✅ Touch-friendly buttons
- ✅ Readable charts on small screens
- ✅ Optimized for tablets and phones

**แนะนำ:**
- ใช้ landscape mode สำหรับ charts
- Pinch to zoom ได้ที่กราฟ

---

## 🔐 Security Notes

### API Endpoints ที่ Dashboard ใช้
```
GET  /api/v1/ai/status/      - ดูสถานะ AI Agent
GET  /api/v1/ai/decisions/   - ดูประวัติการตัดสินใจ
POST /api/v1/ai/analyze-now/ - Trigger AI วิเคราะห์
GET  /api/v1/ai/stats/       - ดูสถิติ
GET  /api/v1/relay/          - ดูสถานะ Relay
```

### ⚠️ ข้อควรระวัง
- Dashboard เป็น read-mostly (อ่านมากกว่าเขียน)
- มีเพียง "Trigger AI Analysis" เท่านั้นที่เปลี่ยนแปลงสถานะ
- อย่าเปิดให้ public access ถ้าไม่ได้ตั้ง authentication
- พิจารณาใช้ Django authentication เพื่อป้องกัน

---

## 📊 Performance Tips

### การลด API Calls
- Auto-update ทุก 10 วินาที (ปรับได้ที่ JavaScript)
- Trigger AI Analysis ควรใช้ไม่เกิน 4 ครั้ง/ชั่วโมง (API quota)

### การปรับปรุงประสิทธิภาพ
```javascript
// ปรับ refresh interval ใน JavaScript
// เปลี่ยนจาก 10000 (10 วินาที) เป็น 30000 (30 วินาที)
setInterval(refreshData, 30000);
```

---

## 🎨 Customization

### เปลี่ยนสี Theme
แก้ไข CSS ใน `ai_dashboard.html`:
```css
/* เปลี่ยนสีพื้นหลัง */
background: linear-gradient(135deg, #YOUR_COLOR_1, #YOUR_COLOR_2);

/* เปลี่ยนสีปุ่ม */
.btn-primary {
    background: #YOUR_COLOR;
}
```

### เปลี่ยนจำนวน Decisions ที่แสดง
แก้ไข JavaScript:
```javascript
// จาก 10 เป็น 20
const response = await fetch('/api/v1/ai/decisions/?limit=20');
```

### เปลี่ยนช่วงเวลาสถิติ
```javascript
// จาก 7 วัน เป็น 30 วัน
const response = await fetch('/api/v1/ai/stats/?days=30');
```

---

## 🌐 Integration with Other Systems

### Export ข้อมูลเป็น JSON
```bash
# ดึงข้อมูล decisions ทั้งหมด
curl http://localhost:8000/api/v1/ai/decisions/?limit=1000 > decisions.json

# ดึงสถิติ
curl http://localhost:8000/api/v1/ai/stats/?days=30 > stats.json
```

### Webhook Integration
สามารถเพิ่ม webhook เพื่อส่งการตัดสินใจไป external system:
```python
# ใน gemini_agent.py หลัง save decision
import requests
requests.post('YOUR_WEBHOOK_URL', json={
    'decision': decision,
    'confidence': confidence,
    'timestamp': timezone.now()
})
```

---

## 📚 Related Documentation

- **AI_AGENT_GUIDE.md** - คู่มือผู้ใช้ AI Agent ฉบับสมบูรณ์
- **README_AI_AGENT.md** - สรุปฟีเจอร์ AI Agent
- **POSTMAN_TESTING_GUIDE.md** - ทดสอบ API ด้วย Postman
- **QUICK_START_TESTING.md** - ทดสอบด้วย curl commands

---

## 🎯 Use Cases

### 1. Monitoring AI Performance
```
1. เปิด Dashboard
2. ดู Confidence Score trend
3. ถ้าต่ำเกินไป → ตรวจสอบ AI Reasoning
4. ปรับ prompt หรือ logic ตามความเหมาะสม
```

### 2. Debugging AI Decisions
```
1. ดู Decision Timeline
2. อ่าน AI Reasoning
3. เปรียบเทียบกับ Weather data
4. ตรวจสอบว่า decision สมเหตุสมผลหรือไม่
```

### 3. Analyzing Weather Patterns
```
1. ดูกราฟ Decision Trends
2. สังเกตรูปแบบการตัดสินใจ
3. วิเคราะห์ว่าสภาพอากาศมีผลอย่างไร
4. ปรับเกณฑ์การตัดสินใจถ้าจำเป็น
```

### 4. Demo & Presentation
```
1. เปิด Dashboard บนจอใหญ่
2. Trigger AI Analysis เพื่อ demo
3. แสดง real-time update
4. อธิบาย AI Reasoning ให้ผู้ชมเห็น
```

---

## 🚀 Next Steps

หลังจากใช้งาน Dashboard แล้ว คุณสามารถ:

1. **เพิ่ม Alerts** - สร้าง notification เมื่อ confidence ต่ำ
2. **Export Reports** - สร้างรายงานประจำวัน/สัปดาห์
3. **Add More Charts** - เพิ่มกราฟอื่นๆ เช่น weather correlation
4. **Mobile App** - สร้าง mobile app เชื่อมต่อกับ API
5. **Machine Learning** - วิเคราะห์ข้อมูลเพื่อปรับปรุง AI

---

## ✅ Checklist: First Time Using Dashboard

- [ ] เปิด Django server (`python manage.py runserver`)
- [ ] เข้า http://localhost:8000/ai/
- [ ] ตรวจสอบ AI Status เป็น ACTIVE
- [ ] ดู Weather ว่าแสดงข้อมูล
- [ ] คลิก "Trigger AI Analysis" เพื่อทดสอบ
- [ ] ดู Decision Timeline มี entry ใหม่
- [ ] ตรวจสอบ Statistics มีค่าขึ้นมา
- [ ] ดูกราฟว่าแสดงผลถูกต้อง
- [ ] ทดสอบ Auto-update (รอ 10 วินาที)
- [ ] ตรวจสอบ Relay Status ตรงกับ Last Decision

---

## 📞 Support

หากพบปัญหาหรือต้องการความช่วยเหลือ:
1. ตรวจสอบ Django console logs
2. เปิด Browser Console (F12) ดู JavaScript errors
3. อ่าน Troubleshooting section ด้านบน
4. ตรวจสอบ API responses ใน Network tab
5. ดู related documentation สำหรับข้อมูลเพิ่มเติม

---

**Created:** December 2024  
**Version:** 1.0  
**Status:** Production Ready ✅  
**Dashboard URL:** `http://localhost:8000/ai/`
