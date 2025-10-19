# 🔄 Auto-Update Feature - Real-time Dashboard

## 📋 สรุปการอัพเดท

เพิ่มฟีเจอร์ **Auto-Update แบบ Real-time** ให้กับ Dashboard โดยไม่ต้อง reload หน้าเว็บ

## ✨ คุณสมบัติที่เพิ่มเข้ามา

### 1. **Automatic Data Refresh (ทุก 5 วินาที)**

Dashboard จะอัพเดทข้อมูลอัตโนมัติทุก 5 วินาที โดยใช้ AJAX เรียก API:

```javascript
// Auto-update data every 5 seconds
setInterval(fetchLatestData, 5000);
```

**สิ่งที่ถูกอัพเดท:**
- ✅ Temperature Card (ค่าและเวลา)
- ✅ Humidity Card (ค่าและเวลา)
- ✅ Temperature Chart (กราฟเคลื่อนไหว smooth)
- ✅ Humidity Chart (กราฟเคลื่อนไหว smooth)
- ✅ Recent Readings Table (10 รายการล่าสุด)

### 2. **Visual Update Indicator**

แสดง indicator ตำแหน่งมุมขวาบนของหน้าจอ:

```
📡 Updating...  → กำลังอัพเดท
✅ Updated      → อัพเดทสำเร็จ
❌ Update failed → อัพเดทไม่สำเร็จ
```

**คุณสมบัติ:**
- แสดงผลด้วย animation fade in/out
- Auto-hide หลังจาก 2-3 วินาที
- สีเขียวสำหรับ success, สีแดงสำหรับ error

### 3. **Manual Refresh Button**

ปุ่ม "🔄 Refresh Now" สำหรับ refresh ข้อมูลทันที:

**คุณสมบัติ:**
- แสดงสถานะ "⏳ Updating..." ขณะกำลัง refresh
- ปุ่มจะ disable ขณะกำลังอัพเดท (ป้องกันการกดซ้ำ)
- กลับมาเป็น "🔄 Refresh Now" หลังเสร็จ

### 4. **Real-time Clock**

แสดงเวลาปัจจุบันที่อัพเดททุกวินาที:

```javascript
setInterval(updateTime, 1000);
```

### 5. **Status Display**

แสดงสถานะการทำงานของ Auto-update ที่ header:

```
🔄 Auto-update: ON (every 5s)
```

## 🔧 การทำงานภายใน

### API Endpoints ที่ใช้:

1. **`/api/chart-data/`** - ดึงข้อมูลสำหรับกราฟและ cards
   ```json
   {
     "success": true,
     "chart_data": {
       "labels": ["15:30:00", "15:30:05", ...],
       "temperature": [27.5, 26.8, ...],
       "humidity": [65.2, 64.1, ...]
     },
     "latest": {
       "temperature": 27.5,
       "humidity": 65.2,
       "timestamp": "2025-10-19 15:30:05"
     }
   }
   ```

2. **`/api/sensor-data/?limit=10`** - ดึงข้อมูลสำหรับตาราง
   ```json
   {
     "success": true,
     "data": [
       {
         "id": 123,
         "temperature": 27.5,
         "humidity": 65.2,
         "timestamp": "2025-10-19 15:30:05",
         "device_name": "ESP32_DHT22"
       },
       ...
     ]
   }
   ```

### JavaScript Functions:

```javascript
// ฟังก์ชันหลัก
fetchLatestData()        // ดึงข้อมูลใหม่จาก API
updateSensorCards()      // อัพเดท Temperature/Humidity cards
updateCharts()           // อัพเดทกราฟ (smooth animation)
updateReadingsTable()    // อัพเดทตาราง
refreshData()            // Manual refresh พร้อม visual feedback

// Helper functions
formatTime()             // แปลงเวลาเป็นรูปแบบ HH:MM:SS
formatDateTime()         // แปลงวันเวลาเป็นรูปแบบเต็ม
updateTime()             // อัพเดทนาฬิกา
```

## 🎯 วิธีทดสอบ

### ขั้นตอนที่ 1: เริ่ม Django Server

```bash
cd D:\GitHub\DjangoDashboardFramework\django_iot_dashboard
python manage.py runserver
```

### ขั้นตอนที่ 2: สร้างข้อมูลทดสอบ

**วิธีที่ 1: สร้างข้อมูลครั้งเดียว**
```bash
python manage.py generate_simple_data --clear --count 50 --minutes 60
```

**วิธีที่ 2: สร้างข้อมูลอย่างต่อเนื่อง (แนะนำสำหรับทดสอบ Auto-update)**

รัน cell ใน Jupyter Notebook:
```python
# สร้างข้อมูลใหม่ทุก 3 วินาที เป็นเวลา 1 นาที
# Dashboard จะอัพเดทอัตโนมัติทุก 5 วินาที
```

### ขั้นตอนที่ 3: เปิด Dashboard

เข้าไปที่: **http://localhost:8000/**

### ขั้นตอนที่ 4: สังเกตการอัพเดท

1. เปิด Browser Console (F12) เพื่อดู log
2. สังเกต indicator มุมขวาบน จะแสดง "📡 Updating..." ทุก 5 วินาที
3. ดู Temperature/Humidity cards เปลี่ยนค่าอัตโนมัติ
4. ดูกราฟเคลื่อนไหว smooth
5. ดูตารางมีแถวใหม่เพิ่มขึ้นมา

## 📊 Console Logs

เมื่อ Dashboard ทำงาน จะเห็น logs แบบนี้:

```
Chart data loaded: {labels: Array(20), temperatures: Array(20), humidities: Array(20)}
✅ Charts created successfully
🚀 Auto-update enabled: refreshing every 5 seconds
✅ Data updated successfully
📊 Charts updated with new data
📋 Readings table updated
✅ Data updated successfully
...
```

## ⚙️ การปรับแต่ง

### เปลี่ยนความถี่ในการอัพเดท

แก้ไขใน `dashboard_simple.html`:

```javascript
// เปลี่ยนจาก 5000 (5 วินาที) เป็นค่าที่ต้องการ (มิลลิวินาที)
setInterval(fetchLatestData, 5000);  // ← แก้ตรงนี้
```

ตัวอย่าง:
- `3000` = 3 วินาที (faster)
- `10000` = 10 วินาที (slower)
- `1000` = 1 วินาที (very fast, not recommended)

### ปิด Auto-update

ถ้าต้องการปิด auto-update:

```javascript
// Comment out หรือลบบรรทัดนี้
// setInterval(fetchLatestData, 5000);
```

### เปลี่ยน Chart Animation

ใน function `updateCharts()`:

```javascript
// 'none' = ไม่มี animation (instant update)
temperatureChart.update('none');

// ลบ 'none' = มี animation (smooth update)
temperatureChart.update();
```

## 🔍 Troubleshooting

### ปัญหา: Auto-update ไม่ทำงาน

**แก้ไข:**
1. เปิด Browser Console (F12)
2. ดู error messages
3. ตรวจสอบว่า API endpoints ทำงานได้:
   - http://localhost:8000/api/chart-data/
   - http://localhost:8000/api/sensor-data/

### ปัญหา: Charts ไม่อัพเดท

**แก้ไข:**
1. ดู console logs
2. ตรวจสอบว่ามีข้อมูลใหม่ในฐานข้อมูล
3. ลอง Manual refresh (กดปุ่ม 🔄)

### ปัญหา: Indicator ไม่แสดง

**แก้ไข:**
1. ตรวจสอบ CSS ของ `.update-indicator`
2. ดูว่า element มี class `show` หรือไม่
3. ลองปรับ `z-index` ให้สูงขึ้น

## 📝 หมายเหตุ

### Performance

- Auto-update ทุก 5 วินาทีเหมาะสำหรับข้อมูล sensor ทั่วไป
- ถ้ามีข้อมูลเปลี่ยนแปลงบ่อยมาก อาจต้องเพิ่มความถี่
- ถ้าข้อมูลเปลี่ยนช้า อาจลดความถี่เพื่อประหยัด resources

### Network Usage

- แต่ละครั้งที่ update จะมีการเรียก API 2 ครั้ง:
  - `/api/chart-data/` (~5-10 KB)
  - `/api/sensor-data/?limit=10` (~2-5 KB)
- ใน 1 นาทีจะใช้ bandwidth ประมาณ 100-200 KB

### Browser Compatibility

ใช้งานได้กับ:
- ✅ Chrome/Edge (Recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Opera

## 🎉 ผลลัพธ์

เมื่อทดสอบเสร็จ คุณจะได้:

1. ✅ Dashboard ที่อัพเดทอัตโนมัติทุก 5 วินาที
2. ✅ ไม่ต้อง reload หน้าเว็บ
3. ✅ การแสดงผลที่ smooth ไม่กระตุก
4. ✅ Visual feedback ชัดเจน
5. ✅ Manual refresh พร้อมใช้งาน
6. ✅ Real-time experience ที่ดี

---

**อัพเดทโดย:** GitHub Copilot  
**วันที่:** 19 ตุลาคม 2025  
**Feature:** Real-time Auto-Update Dashboard  
**Update Frequency:** Every 5 seconds
