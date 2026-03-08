# ตั้งค่า Supabase สำหรับ Django IoT Dashboard

## Supabase คืออะไร

Supabase คือ PostgreSQL database ที่ใช้ฟรีได้ตลอด (ไม่หมดอายุเหมือน Render) มาพร้อม Dashboard สำหรับดูและจัดการข้อมูลในแบบ Table View และ SQL Editor

---

## ขั้นตอนที่ 1: สร้าง Supabase Project

1. ไปที่ [supabase.com](https://supabase.com) → **Start your project** → Login ด้วย GitHub
2. กด **New project**
3. ตั้งค่า:

| Field | Value |
|---|---|
| **Organization** | เลือก organization ที่มีอยู่ หรือสร้างใหม่ |
| **Project name** | `iot-dashboard` (หรือชื่อที่ต้องการ) |
| **Database Password** | ตั้งรหัสผ่านที่คาดเดายาก — **จดไว้ให้ดี** |
| **Region** | `Southeast Asia (Singapore)` |

4. กด **Create new project** รอประมาณ 1-2 นาที

---

## ขั้นตอนที่ 2: ดึงข้อมูล Connection

1. ไปที่ **Project Settings** (ไอคอนฟัน ⚙️ ด้านซ้าย)
2. เลือก **Database**
3. เลื่อนลงหาส่วน **Connection parameters** → เลือก tab **Transaction pooler**

ข้อมูลที่ต้องการ:

| Field | ตัวอย่าง |
|---|---|
| **Host** | `aws-1-ap-southeast-2.pooler.supabase.com` |
| **Port** | `6543` |
| **Database name** | `postgres` |
| **User** | `postgres.xyyqcrdldswoifcrwtfc` |
| **Password** | รหัสที่ตั้งไว้ตอนสร้าง project |

---

## ขั้นตอนที่ 3: ตั้งค่าใน .env

แก้ไขไฟล์ `.env` ที่ root ของ project:

```dotenv
# ─── PostgreSQL (Supabase) ────────────────────────────────────────────────────
DB_NAME=postgres
DB_USER=postgres.xyyqcrdldswoifcrwtfc
DB_PASSWORD=your-database-password
DB_HOST=aws-1-ap-southeast-2.pooler.supabase.com
DB_PORT=6543
```

> **หมายเหตุ:** ใช้ **Transaction Pooler (port 6543)** ไม่ใช่ Direct Connection (port 5432)
> เพราะ Render ต้องการ connection pooling สำหรับ production

---

## ขั้นตอนที่ 4: ตั้งค่า settings.py

`settings.py` ต้องมี `DISABLE_SERVER_SIDE_CURSORS = True` เพราะ Supabase Transaction Pooler ใช้ pgBouncer ที่ไม่รองรับ server-side cursors:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'postgres'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'OPTIONS': {
            'options': '-c default_transaction_isolation=read committed',
        },
        'DISABLE_SERVER_SIDE_CURSORS': True,
    }
}
```

---

## ขั้นตอนที่ 5: Run Migrations

รัน migration ครั้งแรกเพื่อสร้างตารางทั้งหมดใน Supabase:

```powershell
# เข้า project directory
cd django_iot_dashboard

# รัน migration
python manage.py migrate
```

ผลลัพธ์ที่ถูกต้อง:
```
Applying iot_dashboard.0001_initial... OK
Applying iot_dashboard.0002_device_created_at_device_last_updated... OK
...
Applying iot_dashboard.0024_remove_push_all_from_n8npushsettings... OK
Applying sessions.0001_initial... OK
```

---

## ขั้นตอนที่ 6: สร้าง Superuser

```powershell
python manage.py createsuperuser --noinput
```

> ต้องมี environment variables `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_PASSWORD`, `DJANGO_SUPERUSER_EMAIL` ใน `.env` ก่อน

---

## ขั้นตอนที่ 7: ดูข้อมูลใน Supabase Dashboard

1. ไปที่ Supabase Dashboard → เลือก project
2. คลิกที่ **Table Editor** (ไอคอนตาราง) ด้านซ้าย
3. จะเห็นตารางทั้งหมดที่ Django สร้างขึ้น เช่น:
   - `iot_dashboard_device`
   - `iot_dashboard_sensordata`
   - `iot_dashboard_relay`
   - `iot_dashboard_relaylog`
   - `iot_dashboard_thresholdsetting`
   - `iot_dashboard_aidecisionlog`
   - `iot_dashboard_geminiaisettings`
   - `iot_dashboard_weatherlog`
   - `iot_dashboard_n8npushsettings`
   - `auth_user` (Django users)

---

## การตั้งค่าบน Render (Production)

เมื่อ deploy บน Render ให้ใส่ Environment Variables เดียวกัน แต่เปลี่ยน host/port ตามนี้:

| Key | Value (Production บน Render) |
|---|---|
| `DB_HOST` | `aws-1-ap-southeast-2.pooler.supabase.com` |
| `DB_PORT` | `6543` |

> Render และ Supabase อยู่คนละ cloud provider ดังนั้นต้องใช้ **External/Pooler hostname** เสมอ (ไม่มี internal hostname)

---

## Supabase Free Tier ข้อจำกัด

| รายการ | ข้อจำกัด |
|---|---|
| **Storage** | 500 MB |
| **Database** | ฟรีตลอด (ไม่หมดอายุ) |
| **Auto Pause** | Database จะ pause หากไม่มีการใช้งาน 1 สัปดาห์ (wake up อัตโนมัติเมื่อมี request) |
| **Connections** | 60 direct connections, unlimited ผ่าน pooler |
| **Bandwidth** | 5 GB/เดือน |

---

## Troubleshooting

### ❌ connection to server at "localhost" failed

แสดงว่า `.env` หรือ Environment Variables บน Render ยังไม่มีค่า `DB_HOST` ที่ถูกต้อง
ตรวจสอบว่า `DB_HOST` ไม่ใช่ `localhost`

### ❌ SSL connection required

เพิ่มใน `DATABASES OPTIONS`:
```python
'OPTIONS': {
    'sslmode': 'require',
}
```

### ❌ Database is paused (Supabase Free Tier)

Supabase หยุด database หลังไม่มีการใช้งาน 1 สัปดาห์
แก้โดย: ไป Supabase Dashboard → กด **Restore project**
หรือตั้ง cron job ping database ทุกๆ 5 วัน

### ❌ too many connections

เปลี่ยนจาก Direct Connection (port 5432) เป็น Transaction Pooler (port 6543)
