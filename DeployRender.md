# Deploy Django IoT Dashboard บน Render

## สิ่งที่ต้องมีก่อน Deploy

- GitHub account ที่มี repo นี้อยู่
- Supabase account + PostgreSQL database พร้อมใช้งาน
- Render account (สมัครฟรีที่ render.com)

---

## ขั้นตอนที่ 1: เตรียม Code ให้พร้อม

### 1.1 ตรวจสอบ requirements.txt

ไฟล์ `django_iot_dashboard/requirements.txt` ต้องมี package เหล่านี้:

```
gunicorn>=21.0
whitenoise>=6.7
psycopg2-binary>=2.9
```

### 1.2 ตรวจสอบ settings.py

ต้องมีการตั้งค่าเหล่านี้:

```python
# อ่านค่าจาก environment variables
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')

# WhiteNoise สำหรับ Static Files
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    ...
]

STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'postgres'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'DISABLE_SERVER_SIDE_CURSORS': True,  # จำเป็นสำหรับ Supabase Pooler
    }
}
```

### 1.3 ตรวจสอบ .gitignore

ต้องมีบรรทัดเหล่านี้เพื่อไม่ให้ไฟล์ secret ขึ้น GitHub:

```
.env
.env.*
!.env.example
```

### 1.4 Push Code ขึ้น GitHub

```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin 16_AddN8NAnalyzer
```

---

## ขั้นตอนที่ 2: สร้าง Web Service บน Render

1. ไปที่ [render.com](https://render.com) → Login
2. กด **New +** → เลือก **Web Service**
3. เลือก **Connect a repository** → เลือก `DjangoDashboardFramework`
4. ตั้งค่าดังนี้:

| Setting | Value |
|---|---|
| **Name** | `djangodashboardframework` (หรือชื่อที่ต้องการ) |
| **Branch** | `16_AddN8NAnalyzer` |
| **Root Directory** | `django_iot_dashboard` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt && python manage.py collectstatic --noinput` |
| **Start Command** | `python manage.py migrate && gunicorn dashboard_project.wsgi:application` |
| **Instance Type** | `Free` |

---

## ขั้นตอนที่ 3: ตั้งค่า Environment Variables

ไปที่ tab **Environment** → กด **Add Environment Variable** ใส่ทีละตัว:

### Django Settings

| Key | Value |
|---|---|
| `SECRET_KEY` | `^$*9-c($14-($)=gmn20gcbh-%ixu54o$_j)!r(@mb!hq2tpat` |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `your-app-name.onrender.com` *(ใส่ตามชื่อจริงหลัง deploy)* |

### PostgreSQL (Supabase)

| Key | Value |
|---|---|
| `DB_NAME` | `postgres` |
| `DB_USER` | `postgres.xyyqcrdldswoifcrwtfc` |
| `DB_PASSWORD` | `Pam-6395959` |
| `DB_HOST` | `aws-1-ap-southeast-2.pooler.supabase.com` |
| `DB_PORT` | `6543` |

> **หมายเหตุ:** ใช้ **Transaction Pooler** (port 6543) ของ Supabase ไม่ใช่ port 5432

### Django Superuser (สำหรับสร้าง admin ครั้งแรก)

| Key | Value |
|---|---|
| `DJANGO_SUPERUSER_USERNAME` | `admin` |
| `DJANGO_SUPERUSER_PASSWORD` | `admin1234` |
| `DJANGO_SUPERUSER_EMAIL` | `admin@example.com` |

> **หมายเหตุ:** ลบ 3 บรรทัดนี้ออกหลัง login admin ครั้งแรกสำเร็จแล้ว

### Weather & AI

| Key | Value |
|---|---|
| `OPENWEATHER_API_KEY` | `1bef650d2c6ea7a91f58252948c2d325` |
| `WEATHER_LOCATION` | `Tha Sala,TH` |
| `OPENROUTER_API_KEY` | `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` |
| `AI_AGENT_INTERVAL_MINUTES` | `60` |

### N8N Push Webhooks

| Key | Value |
|---|---|
| `N8N_PUSH_ENABLED` | `false` |
| `N8N_PUSH_TIMEOUT` | `60` |
| `N8N_WEBHOOK_SNAPSHOT` | *(ว่างไว้ก่อน หรือใส่ URL จริงเมื่อตั้งค่า N8N)* |

---

## ขั้นตอนที่ 4: Deploy

1. กด **Create Web Service**
2. Render จะเริ่ม build อัตโนมัติ ใช้เวลาประมาณ 3-5 นาที
3. ดู log ที่แถบ **Logs** หากมี error จะแสดงที่นี่

### ตัวอย่าง Build Log ที่สำเร็จ

```
==> Installing dependencies...
Successfully installed Django gunicorn whitenoise psycopg2-binary ...
==> Running collectstatic...
==> Starting server...
==> Running migrations...
==> Your service is live at https://your-app.onrender.com
```

---

## ขั้นตอนที่ 5: หลัง Deploy สำเร็จ

### 5.1 แก้ ALLOWED_HOSTS

หาก Deploy แล้วเจอ error:
```
DisallowedHost at /
Invalid HTTP_HOST header: 'your-app.onrender.com'
```

ให้ไปที่ Render Dashboard → **Environment** → แก้ค่า `ALLOWED_HOSTS` เป็น domain จริง เช่น:
```
djangodashboardframework.onrender.com
```
กด **Save Changes** → Render จะ redeploy อัตโนมัติ

### 5.2 เข้าใช้งาน

| URL | คำอธิบาย |
|---|---|
| `https://your-app.onrender.com/` | Dashboard หน้าหลัก |
| `https://your-app.onrender.com/admin/` | Django Admin |

Login Admin ด้วย: `admin` / `admin1234`

### 5.3 ลบ Superuser Credentials

หลัง login admin สำเร็จแล้ว ให้ลบ environment variables ออก:
- `DJANGO_SUPERUSER_USERNAME`
- `DJANGO_SUPERUSER_PASSWORD`
- `DJANGO_SUPERUSER_EMAIL`

---

## การ Redeploy เมื่อมีการแก้ Code

Render จะ redeploy อัตโนมัติทุกครั้งที่ push code ขึ้น GitHub branch ที่เลือกไว้

หากต้องการ redeploy ด้วยตนเอง: Render Dashboard → **Manual Deploy** → **Deploy latest commit**

---

## Troubleshooting

### ❌ Cannot connect to database

ตรวจสอบ:
- `DB_HOST` ต้องเป็น Supabase pooler hostname (ไม่ใช่ localhost)
- `DB_PORT` ต้องเป็น `6543` สำหรับ Transaction Pooler

### ❌ Static files ไม่โหลด (CSS/JS หาย)

ตรวจสอบ Build Command มี `python manage.py collectstatic --noinput` ด้วย

### ❌ ModuleNotFoundError

ตรวจสอบ `requirements.txt` มี package ครบ แล้ว redeploy

### ❌ Application Error / 500

ดู Log ใน Render Dashboard → **Logs** tab เพื่อหาสาเหตุ

---

## สรุป Commands สำคัญ

```bash
# Build Command (Render)
pip install -r requirements.txt && python manage.py collectstatic --noinput

# Start Command (Render)
python manage.py migrate && gunicorn dashboard_project.wsgi:application

# สร้าง SECRET_KEY ใหม่ (รันใน local)
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
