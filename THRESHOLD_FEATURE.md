# 🚨 Threshold Alarm System Documentation

## 📋 Overview

ระบบ Threshold Alarm ช่วยให้คุณสามารถกำหนดค่าขีดจำกัดสูงสุด/ต่ำสุดของ **Temperature** และ **Humidity** เพื่อควบคุม **Relay 1** อัตโนมัติเมื่อค่าเกินที่กำหนด

### ✨ คุณสมบัติหลัก

- ✅ **Auto/Manual Mode**: เลือกควบคุมอัตโนมัติหรือด้วยมือ
- ✅ **Threshold Configuration**: กำหนดค่าขีดจำกัดของ Temperature และ Humidity
- ✅ **Automatic Relay Control**: เปิด/ปิด Relay 1 อัตโนมัติเมื่อเกิน Threshold
- ✅ **Hysteresis Support**: ป้องกันการเปิด-ปิด Relay บ่อยเกินไป
- ✅ **Average Calculation**: คำนวณค่าเฉลี่ยจากข้อมูลล่าสุด
- ✅ **Alarm Status Tracking**: ติดตามสถานะการแจ้งเตือน
- ✅ **REST API**: จัดการผ่าน API ได้

---

## 🏗️ Architecture

### 1. **Database Model** (`models.py`)

```python
class ThresholdSetting(models.Model):
    # Threshold values
    temperature_high = 35.0°C  # อุณหภูมิสูงสุด
    temperature_low = 20.0°C   # อุณหภูมิต่ำสุด
    humidity_high = 80.0%      # ความชื้นสูงสุด
    humidity_low = 30.0%       # ความชื้นต่ำสุด
    
    # Mode
    mode = 'MANUAL' or 'AUTO'  # โหมดการทำงาน
    
    # Relay control
    relay1_auto_enabled = True # เปิด/ปิดการควบคุม Relay 1
    
    # Alarm status
    alarm_active = False       # สถานะ Alarm
    alarm_reason = ""          # เหตุผลที่ Alarm เปิด
    last_triggered = None      # เวลาที่ Alarm เปิดล่าสุด
    
    # Advanced settings
    hysteresis_percentage = 2.0  # ช่วง hysteresis (%)
    average_window = 10          # จำนวน readings สำหรับค่าเฉลี่ย
```

### 2. **MQTT Auto-Control** (`mqtt_callbacks.py`)

เมื่อ ESP32 ส่ง sensor data มา ระบบจะ:

```python
def handle_sensor_data_message(topic, message):
    # 1. Save sensor data
    sensor_data = SensorData.objects.create(...)
    
    # 2. Check threshold (if AUTO mode)
    threshold = ThresholdSetting.get_or_create_default()
    
    if threshold.mode == 'AUTO':
        check_result = threshold.check_threshold(sensor_data)
        
        # 3. Control Relay 1 automatically
        if check_result['should_trigger'] and not threshold.alarm_active:
            send_relay_command(1, 'ON')  # เปิด Relay 1
            threshold.activate_alarm(reason=check_result['reason'])
        
        elif not check_result['should_trigger'] and threshold.alarm_active:
            send_relay_command(1, 'OFF')  # ปิด Relay 1
            threshold.deactivate_alarm()
```

### 3. **REST API Endpoints** (`views_simple.py`)

#### 📡 **GET/POST /api/v1/threshold/**
- **GET**: ดึงข้อมูล Threshold ปัจจุบัน พร้อมค่าเฉลี่ย
- **POST**: อัพเดท Threshold Settings

#### 📡 **GET /api/v1/threshold/check/**
- ตรวจสอบว่า Sensor Data ล่าสุดเกิน Threshold หรือไม่

#### 📡 **POST /api/v1/threshold/reset/**
- รีเซ็ต Alarm และปิด Relay 1 ทันที

---

## 🔧 Installation & Setup

### Step 1: Migration (✅ สำเร็จแล้ว)

```bash
cd d:\GitHub\DjangoDashboardFramework\django_iot_dashboard
python manage.py makemigrations
python manage.py migrate
```

**Output:**
```
Migrations for 'iot_dashboard':
  iot_dashboard\migrations\0005_thresholdsetting.py
    + Create model ThresholdSetting

Operations to perform:
  Apply all migrations: admin, auth, contenttypes, iot_dashboard, sessions
Running migrations:
  Applying iot_dashboard.0005_thresholdsetting... OK
```

### Step 2: Update Views (✅ สำเร็จแล้ว)

เพิ่ม 3 API endpoints ใน `views_simple.py`:
- ✅ `api_threshold_settings(request)` - GET/POST config
- ✅ `api_threshold_check(request)` - GET status
- ✅ `api_threshold_reset(request)` - POST reset

### Step 3: Update URLs (✅ สำเร็จแล้ว)

เพิ่ม URL patterns ใน `urls.py`:
```python
path('api/v1/threshold/', views_simple.api_threshold_settings),
path('api/v1/threshold/check/', views_simple.api_threshold_check),
path('api/v1/threshold/reset/', views_simple.api_threshold_reset),
```

### Step 4: Update MQTT Callbacks (✅ สำเร็จแล้ว)

แก้ไข `handle_sensor_data_message()` ใน `mqtt_callbacks.py` เพื่อ:
- ✅ ตรวจสอบ Threshold อัตโนมัติ
- ✅ ควบคุม Relay 1 ตามโหมด AUTO/MANUAL
- ✅ รองรับ Hysteresis เพื่อป้องกัน Relay chattering

### Step 5: Update Dashboard UI (🔄 ต่อไป)

เพิ่ม Threshold Configuration Card ใน `dashboard_simple.html` ดู: [UI_INSTRUCTIONS.md](#dashboard-ui-update-instructions)

---

## 📚 API Documentation

### 1. GET Threshold Settings

```bash
curl -X GET http://localhost:8000/api/v1/threshold/
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "temperature_high": 35.0,
    "temperature_low": 20.0,
    "humidity_high": 80.0,
    "humidity_low": 30.0,
    "mode": "MANUAL",
    "mode_display": "👤 MANUAL - ควบคุมด้วยมือ",
    "relay1_auto_enabled": true,
    "alarm_active": false,
    "alarm_status_display": "✅ ปกติ (Normal)",
    "alarm_reason": "",
    "last_triggered": null,
    "hysteresis_percentage": 2.0,
    "average_window": 10,
    "current_averages": {
      "temperature": 28.5,
      "humidity": 65.2
    },
    "latest_sensor": {
      "temperature": 29.0,
      "humidity": 66.0,
      "timestamp": "2024-01-15 10:30:00"
    },
    "created_at": "2024-01-15 09:00:00",
    "updated_at": "2024-01-15 10:00:00"
  }
}
```

### 2. Update Threshold Settings

```bash
curl -X POST http://localhost:8000/api/v1/threshold/ \
  -H "Content-Type: application/json" \
  -d '{
    "temperature_high": 36.0,
    "temperature_low": 18.0,
    "humidity_high": 85.0,
    "humidity_low": 25.0,
    "mode": "AUTO",
    "relay1_auto_enabled": true
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Threshold settings updated successfully",
  "data": { ... }
}
```

### 3. Check Threshold Status

```bash
curl -X GET http://localhost:8000/api/v1/threshold/check/
```

**Response:**
```json
{
  "success": true,
  "data": {
    "threshold_exceeded": true,
    "should_trigger_alarm": true,
    "reason": "🌡️ อุณหภูมิสูง: 36.5°C > 35.0°C",
    "current_sensor": {
      "temperature": 36.5,
      "humidity": 75.0,
      "timestamp": "2024-01-15 10:30:00"
    },
    "averages": {
      "temperature": 30.2,
      "humidity": 68.5
    },
    "threshold_settings": {
      "temperature_high": 35.0,
      "temperature_low": 20.0,
      "humidity_high": 80.0,
      "humidity_low": 30.0,
      "mode": "AUTO"
    }
  }
}
```

### 4. Reset Alarm

```bash
curl -X POST http://localhost:8000/api/v1/threshold/reset/
```

**Response:**
```json
{
  "success": true,
  "message": "Alarm reset successfully. Relay 1 turned OFF.",
  "data": {
    "alarm_active": false,
    "relay1_status": false
  }
}
```

---

## 🎯 How It Works

### Scenario 1: AUTO Mode - Temperature Exceeds High Threshold

1. **ESP32** ส่ง sensor data: `{"temperature": 37.0, "humidity": 70.0}`
2. **MQTT Callback** รับข้อมูลและบันทึกลง database
3. **Threshold Check** ตรวจสอบพบว่า: `37.0°C > 35.0°C (threshold_high)`
4. **Auto-Control**: ส่งคำสั่ง `send_relay_command(1, 'ON')` → Relay 1 เปิด
5. **Alarm Activated**: บันทึกสถานะ `alarm_active = True`, `alarm_reason = "🌡️ อุณหภูมิสูง: 37.0°C > 35.0°C"`
6. **Log Output**:
   ```
   🚨 THRESHOLD EXCEEDED: 🌡️ อุณหภูมิสูง: 37.0°C > 35.0°C
   ✅ Auto-Control: Relay 1 turned ON (Alarm Activated)
   ```

### Scenario 2: AUTO Mode - Values Return to Normal

1. **ESP32** ส่ง sensor data: `{"temperature": 33.0, "humidity": 65.0}`
2. **Threshold Check** ตรวจสอบพบว่า: ค่ากลับมาต่ำกว่า `35.0 - (35.0 * 2% hysteresis) = 34.3°C`
3. **Auto-Control**: ส่งคำสั่ง `send_relay_command(1, 'OFF')` → Relay 1 ปิด
4. **Alarm Deactivated**: บันทึกสถานะ `alarm_active = False`
5. **Log Output**:
   ```
   ✅ THRESHOLD NORMALIZED: ค่ากลับสู่สภาวะปกติ (Hysteresis)
   ✅ Auto-Control: Relay 1 turned OFF (Alarm Deactivated)
   ```

### Scenario 3: MANUAL Mode - No Automatic Control

1. **ESP32** ส่ง sensor data: `{"temperature": 38.0, "humidity": 75.0}`
2. **Threshold Check** ตรวจสอบพบว่าเกิน threshold
3. **Mode Check**: `mode = MANUAL` → **ไม่ควบคุม Relay อัตโนมัติ**
4. **Log Output**:
   ```
   📊 Sensor data saved: Temp=38.0°C, Hum=75.0%
   ```
5. **User Manual Control**: ผู้ใช้ต้องเปิด/ปิด Relay 1 เองผ่าน Dashboard

---

## ⚙️ Configuration Options

### Threshold Values
- `temperature_high`: อุณหภูมิสูงสุด (°C)
- `temperature_low`: อุณหภูมิต่ำสุด (°C)
- `humidity_high`: ความชื้นสูงสุด (%)
- `humidity_low`: ความชื้นต่ำสุด (%)

### Mode Selection
- **AUTO**: ควบคุม Relay 1 อัตโนมัติเมื่อเกิน Threshold
- **MANUAL**: ผู้ใช้ควบคุม Relay 1 เองผ่าน Dashboard

### Advanced Settings
- `hysteresis_percentage`: ช่วง hysteresis (default: 2.0%)
  - ป้องกันการเปิด-ปิด Relay บ่อยเกินไป
  - ตัวอย่าง: ถ้า threshold_high = 35°C, hysteresis = 2%
    - เปิด Relay เมื่อ: `T > 35.0°C`
    - ปิด Relay เมื่อ: `T < 34.3°C` (35.0 - 2%)

- `average_window`: จำนวน readings สำหรับคำนวณค่าเฉลี่ย (default: 10)
  - ใช้ข้อมูล 10 readings ล่าสุดในการคำนวณค่าเฉลี่ย

---

## 🎨 Dashboard UI Update Instructions

เพิ่ม **Threshold Configuration Card** ใน `dashboard_simple.html` หลัง Relay Controller Section:

### Step 1: เพิ่ม CSS (ใน `<style>` tag ก่อน `</style>`)

```css
/* Threshold Configuration Card */
.threshold-section {
    background: white;
    border-radius: 15px;
    padding: 25px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    margin-bottom: 30px;
}

.threshold-section h2 {
    color: #333;
    margin-bottom: 20px;
    text-align: center;
}

.threshold-config-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin-bottom: 20px;
}

.threshold-input-group {
    display: flex;
    flex-direction: column;
}

.threshold-input-group label {
    font-weight: bold;
    margin-bottom: 5px;
    color: #555;
}

.threshold-input-group input {
    padding: 10px;
    border: 2px solid #ddd;
    border-radius: 8px;
    font-size: 16px;
    transition: border-color 0.3s ease;
}

.threshold-input-group input:focus {
    outline: none;
    border-color: #4ecdc4;
}

.mode-selector {
    display: flex;
    gap: 15px;
    align-items: center;
    justify-content: center;
    margin: 20px 0;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 10px;
}

.mode-button {
    padding: 12px 30px;
    border: 2px solid #ddd;
    border-radius: 8px;
    background: white;
    cursor: pointer;
    font-size: 16px;
    font-weight: bold;
    transition: all 0.3s ease;
}

.mode-button.active {
    background: #28a745;
    color: white;
    border-color: #28a745;
}

.mode-button.auto.active {
    background: #007bff;
    border-color: #007bff;
}

.alarm-status {
    text-align: center;
    padding: 15px;
    margin: 15px 0;
    border-radius: 10px;
    font-size: 18px;
    font-weight: bold;
}

.alarm-status.active {
    background: #dc3545;
    color: white;
}

.alarm-status.normal {
    background: #28a745;
    color: white;
}

.threshold-averages {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 15px;
    margin: 15px 0;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 10px;
}

.average-item {
    text-align: center;
}

.average-value {
    font-size: 24px;
    font-weight: bold;
    margin: 5px 0;
}

.average-value.temp {
    color: #ff6b6b;
}

.average-value.hum {
    color: #4ecdc4;
}

.threshold-actions {
    display: flex;
    gap: 15px;
    justify-content: center;
    margin-top: 20px;
}

@media (max-width: 768px) {
    .threshold-config-grid {
        grid-template-columns: 1fr;
    }
    
    .mode-selector {
        flex-direction: column;
    }
}
```

### Step 2: เพิ่ม HTML (หลัง Relay Controller Section ประมาณบรรทัด 558)

```html
<!-- Threshold Configuration Section -->
<div class="threshold-section">
    <h2>🚨 Threshold Alarm Configuration</h2>
    
    <!-- Current Averages -->
    <div class="threshold-averages" id="threshold-averages">
        <div class="average-item">
            <div style="font-size: 14px; color: #666;">📊 Average Temperature</div>
            <div class="average-value temp" id="avg-temp">--°C</div>
        </div>
        <div class="average-item">
            <div style="font-size: 14px; color: #666;">📊 Average Humidity</div>
            <div class="average-value hum" id="avg-hum">--%</div>
        </div>
    </div>
    
    <!-- Alarm Status -->
    <div class="alarm-status normal" id="alarm-status">
        ✅ ปกติ (Normal)
    </div>
    
    <!-- Mode Selector -->
    <div class="mode-selector">
        <span style="font-weight: bold;">โหมดการทำงาน:</span>
        <button class="mode-button" id="mode-manual" onclick="setMode('MANUAL')">
            👤 MANUAL
        </button>
        <button class="mode-button auto" id="mode-auto" onclick="setMode('AUTO')">
            🤖 AUTO
        </button>
    </div>
    
    <!-- Threshold Configuration -->
    <div class="threshold-config-grid">
        <!-- Temperature High -->
        <div class="threshold-input-group">
            <label for="temp-high">🌡️ อุณหภูมิสูงสุด (°C)</label>
            <input type="number" id="temp-high" step="0.1" value="35.0" />
        </div>
        
        <!-- Temperature Low -->
        <div class="threshold-input-group">
            <label for="temp-low">❄️ อุณหภูมิต่ำสุด (°C)</label>
            <input type="number" id="temp-low" step="0.1" value="20.0" />
        </div>
        
        <!-- Humidity High -->
        <div class="threshold-input-group">
            <label for="hum-high">💧 ความชื้นสูงสุด (%)</label>
            <input type="number" id="hum-high" step="0.1" value="80.0" />
        </div>
        
        <!-- Humidity Low -->
        <div class="threshold-input-group">
            <label for="hum-low">🏜️ ความชื้นต่ำสุด (%)</label>
            <input type="number" id="hum-low" step="0.1" value="30.0" />
        </div>
    </div>
    
    <!-- Actions -->
    <div class="threshold-actions">
        <button class="btn btn-success" onclick="saveThresholdSettings()">
            💾 Save Settings
        </button>
        <button class="btn btn-warning" onclick="loadThresholdSettings()">
            🔄 Reload
        </button>
        <button class="btn btn-danger" onclick="resetAlarm()">
            🔕 Reset Alarm
        </button>
    </div>
    
    <div style="margin-top: 15px; text-align: center; font-size: 12px; color: #999;">
        💡 AUTO mode: Relay 1 จะเปิดอัตโนมัติเมื่อค่าเกิน Threshold | MANUAL mode: ควบคุมด้วยมือ
    </div>
</div>
```

### Step 3: เพิ่ม JavaScript Functions (ก่อน `</body>`)

```javascript
// ========================================
// Threshold Management Functions
// ========================================

let currentMode = 'MANUAL';

// Load threshold settings from API
async function loadThresholdSettings() {
    try {
        const response = await fetch('/api/v1/threshold/');
        const result = await response.json();
        
        if (result.success) {
            const data = result.data;
            
            // Update input fields
            document.getElementById('temp-high').value = data.temperature_high;
            document.getElementById('temp-low').value = data.temperature_low;
            document.getElementById('hum-high').value = data.humidity_high;
            document.getElementById('hum-low').value = data.humidity_low;
            
            // Update mode
            currentMode = data.mode;
            updateModeButtons(data.mode);
            
            // Update averages
            if (data.current_averages.temperature) {
                document.getElementById('avg-temp').textContent = 
                    data.current_averages.temperature.toFixed(1) + '°C';
            }
            if (data.current_averages.humidity) {
                document.getElementById('avg-hum').textContent = 
                    data.current_averages.humidity.toFixed(1) + '%';
            }
            
            // Update alarm status
            const alarmDiv = document.getElementById('alarm-status');
            if (data.alarm_active) {
                alarmDiv.className = 'alarm-status active';
                alarmDiv.innerHTML = '🚨 กำลังแจ้งเตือน (Alarm Active)<br>' +
                    '<small style="font-size: 14px;">' + data.alarm_reason + '</small>';
            } else {
                alarmDiv.className = 'alarm-status normal';
                alarmDiv.textContent = '✅ ปกติ (Normal)';
            }
            
            console.log('✅ Threshold settings loaded');
        }
    } catch (error) {
        console.error('❌ Load threshold error:', error);
        showUpdateIndicator('❌ Load failed', 'error');
    }
}

// Save threshold settings
async function saveThresholdSettings() {
    try {
        const settings = {
            temperature_high: parseFloat(document.getElementById('temp-high').value),
            temperature_low: parseFloat(document.getElementById('temp-low').value),
            humidity_high: parseFloat(document.getElementById('hum-high').value),
            humidity_low: parseFloat(document.getElementById('hum-low').value),
            mode: currentMode,
            relay1_auto_enabled: true
        };
        
        const response = await fetch('/api/v1/threshold/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(settings)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showUpdateIndicator('✅ Settings saved', 'success');
            loadThresholdSettings(); // Reload to get updated values
        } else {
            showUpdateIndicator('❌ Save failed: ' + result.error, 'error');
        }
    } catch (error) {
        console.error('❌ Save threshold error:', error);
        showUpdateIndicator('❌ Save failed', 'error');
    }
}

// Set mode (AUTO/MANUAL)
function setMode(mode) {
    currentMode = mode;
    updateModeButtons(mode);
}

// Update mode button styles
function updateModeButtons(mode) {
    const manualBtn = document.getElementById('mode-manual');
    const autoBtn = document.getElementById('mode-auto');
    
    manualBtn.classList.remove('active');
    autoBtn.classList.remove('active');
    
    if (mode === 'MANUAL') {
        manualBtn.classList.add('active');
    } else {
        autoBtn.classList.add('active');
    }
}

// Reset alarm
async function resetAlarm() {
    if (!confirm('ต้องการรีเซ็ต Alarm และปิด Relay 1 หรือไม่?')) {
        return;
    }
    
    try {
        const response = await fetch('/api/v1/threshold/reset/', {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showUpdateIndicator('✅ Alarm reset', 'success');
            loadThresholdSettings(); // Reload to get updated status
            refreshData(); // Refresh all data
        } else {
            showUpdateIndicator('❌ Reset failed: ' + result.error, 'error');
        }
    } catch (error) {
        console.error('❌ Reset alarm error:', error);
        showUpdateIndicator('❌ Reset failed', 'error');
    }
}

// Load threshold settings on page load
document.addEventListener('DOMContentLoaded', function() {
    loadThresholdSettings();
    
    // Reload threshold settings every 10 seconds
    setInterval(loadThresholdSettings, 10000);
});
```

---

## ✅ Testing Checklist

### 1. API Testing (ใช้ Postman หรือ curl)

- [ ] GET `/api/v1/threshold/` - ดึงข้อมูล Threshold
- [ ] POST `/api/v1/threshold/` - อัพเดท Threshold (mode: MANUAL)
- [ ] POST `/api/v1/threshold/` - อัพเดท Threshold (mode: AUTO)
- [ ] GET `/api/v1/threshold/check/` - ตรวจสอบสถานะ Threshold
- [ ] POST `/api/v1/threshold/reset/` - รีเซ็ต Alarm

### 2. MANUAL Mode Testing

- [ ] ตั้งค่า Mode = MANUAL
- [ ] ส่ง sensor data ที่เกิน Threshold
- [ ] ตรวจสอบว่า Relay 1 **ไม่เปิดอัตโนมัติ**
- [ ] เปิด/ปิด Relay 1 ด้วยมือผ่าน Dashboard

### 3. AUTO Mode Testing

- [ ] ตั้งค่า Mode = AUTO
- [ ] ตั้งค่า `temperature_high = 35.0°C`
- [ ] ส่ง sensor data: `{"temperature": 37.0, "humidity": 70.0}`
- [ ] ตรวจสอบ Log ว่ามีข้อความ: `🚨 THRESHOLD EXCEEDED`
- [ ] ตรวจสอบว่า Relay 1 **เปิดอัตโนมัติ**
- [ ] ตรวจสอบสถานะ `alarm_active = True`

### 4. Hysteresis Testing

- [ ] Alarm เปิดอยู่ (temp = 37.0°C, threshold_high = 35.0°C)
- [ ] ส่ง sensor data: `{"temperature": 34.5, "humidity": 65.0}`
- [ ] ตรวจสอบว่า Relay 1 ยังเปิดอยู่ (ยังไม่ถึง hysteresis threshold)
- [ ] ส่ง sensor data: `{"temperature": 33.0, "humidity": 65.0}`
- [ ] ตรวจสอบ Log ว่ามีข้อความ: `✅ THRESHOLD NORMALIZED`
- [ ] ตรวจสอบว่า Relay 1 **ปิดอัตโนมัติ**
- [ ] ตรวจสอบสถานะ `alarm_active = False`

### 5. Dashboard UI Testing (หลังเพิ่ม UI)

- [ ] เปิด Dashboard แล้วเห็น Threshold Configuration Card
- [ ] แสดงค่าเฉลี่ย Temperature/Humidity
- [ ] แสดงสถานะ Alarm (Normal/Active)
- [ ] Toggle Mode ระหว่าง AUTO/MANUAL
- [ ] แก้ไขค่า Threshold และกด Save
- [ ] กด Reset Alarm แล้ว Relay 1 ปิด

---

## 🐛 Troubleshooting

### ปัญหา: Relay 1 ไม่เปิดอัตโนมัติ

**วิธีแก้:**
1. ตรวจสอบ Mode: `GET /api/v1/threshold/` → `mode = "AUTO"`
2. ตรวจสอบ relay1_auto_enabled: `relay1_auto_enabled = true`
3. ดู Django logs: `python manage.py runserver` แล้วส่ง sensor data
4. ตรวจสอบว่ามี log: `🚨 THRESHOLD EXCEEDED`

### ปัญหา: Relay 1 เปิด-ปิดบ่อยเกินไป (Chattering)

**วิธีแก้:**
1. เพิ่มค่า `hysteresis_percentage`: `POST /api/v1/threshold/` → `{"hysteresis_percentage": 5.0}`
2. เพิ่ม `average_window`: `{"average_window": 20}`

### ปัญหา: ค่าเฉลี่ยไม่แสดง

**วิธีแก้:**
1. ตรวจสอบว่ามีข้อมูล SensorData ใน database: `GET /api/v1/sensors/latest/`
2. ตรวจสอบ `average_window` ไม่ใหญ่เกินจำนวนข้อมูลที่มี

---

## 📊 Log Examples

### Normal Operation (AUTO Mode)

```
📊 Sensor data saved: Temp=28.0°C, Hum=65.0%
✅ Normal: No action needed (Temp=28.0°C, Hum=65.0%)
```

### Threshold Exceeded (AUTO Mode)

```
📊 Sensor data saved: Temp=37.0°C, Hum=75.0%
🚨 THRESHOLD EXCEEDED: 🌡️ อุณหภูมิสูง: 37.0°C > 35.0°C
✅ Auto-Control: Relay 1 turned ON (Alarm Activated)
```

### Threshold Normalized (AUTO Mode)

```
📊 Sensor data saved: Temp=33.0°C, Hum=65.0%
✅ THRESHOLD NORMALIZED: ค่ากลับสู่สภาวะปกติ (Hysteresis)
✅ Auto-Control: Relay 1 turned OFF (Alarm Deactivated)
```

### MANUAL Mode (No Action)

```
📊 Sensor data saved: Temp=38.0°C, Hum=75.0%
```

---

## 🎉 Summary

### ✅ สำเร็จแล้ว:
1. ✅ สร้าง ThresholdSetting Model พร้อม fields ครบถ้วน
2. ✅ เพิ่ม Auto-control logic ใน mqtt_callbacks.py
3. ✅ สร้าง 3 API endpoints พร้อม documentation
4. ✅ อัพเดท URL routing
5. ✅ Migration และ apply database

### 🔄 ต่อไป:
1. เพิ่ม Threshold Configuration Card ใน Dashboard UI
2. ทดสอบระบบทั้งหมด
3. อัพเดท Postman Collection ด้วย Threshold endpoints

---

## 📞 Support

หากมีปัญหาหรือคำถาม:
1. ตรวจสอบ Log ใน Django console
2. ใช้ API endpoint `/api/v1/threshold/check/` เพื่อดูสถานะปัจจุบัน
3. ดู API documentation ใน `API_GUIDE.md`

**Created:** 2024-01-15  
**Version:** 1.0.0  
**Author:** GitHub Copilot
