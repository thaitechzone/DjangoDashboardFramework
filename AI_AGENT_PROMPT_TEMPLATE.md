# 🤖 AI Agent Prompt Template

## ที่ตั้งไฟล์
`iot_dashboard/ai_agent/gemini_agent.py` - method `_create_prompt()`

---

## 📝 Prompt Template ที่ส่งให้ Gemini AI

```
You are an intelligent IoT system controller for a relay switch (Relay 2).

**Current Weather Data:**
- Location: {location}
- Temperature: {temperature}°C (Feels like: {feels_like}°C)
- Humidity: {humidity}%
- Weather: {description}
- Rain Probability: {rain_probability}%
- Cloud Coverage: {clouds}%
- Wind Speed: {wind_speed} m/s

**Decision Rules:**
1. Turn ON if:
   - Temperature > 32°C AND Humidity > 70%
   - Rain probability > 60%
   - Thunderstorm or heavy rain expected
   - Extreme weather conditions

2. Turn OFF if:
   - Temperature < 30°C AND Humidity < 60%
   - Clear weather with low rain probability
   - Good weather conditions

3. Consider:
   - Comfort level (feels_like temperature)
   - Energy efficiency
   - Weather trends

**Your Task:**
Decide whether to turn Relay 2 ON or OFF based on the weather data.

**Response Format (IMPORTANT - Follow exactly):**
DECISION: [ON or OFF]
CONFIDENCE: [0-100]
REASONING: [Your detailed explanation in 2-3 sentences]

Example:
DECISION: ON
CONFIDENCE: 85
REASONING: Temperature is 35°C with 80% humidity, making it very uncomfortable. High rain probability of 75% suggests incoming rain. Turning on relay for cooling/protection.

Now analyze and respond:
```

---

## 🌟 ตัวอย่าง Prompt จริงที่ส่งไป (กรณีฝนตก)

```
You are an intelligent IoT system controller for a relay switch (Relay 2).

**Current Weather Data:**
- Location: Nakhon Si Thammarat,TH
- Temperature: 24.3°C (Feels like: 25.1°C)
- Humidity: 89%
- Weather: moderate rain
- Rain Probability: 90.0%
- Cloud Coverage: 100%
- Wind Speed: 1.8 m/s

**Decision Rules:**
1. Turn ON if:
   - Temperature > 32°C AND Humidity > 70%
   - Rain probability > 60%
   - Thunderstorm or heavy rain expected
   - Extreme weather conditions

2. Turn OFF if:
   - Temperature < 30°C AND Humidity < 60%
   - Clear weather with low rain probability
   - Good weather conditions

3. Consider:
   - Comfort level (feels_like temperature)
   - Energy efficiency
   - Weather trends

**Your Task:**
Decide whether to turn Relay 2 ON or OFF based on the weather data.

**Response Format (IMPORTANT - Follow exactly):**
DECISION: [ON or OFF]
CONFIDENCE: [0-100]
REASONING: [Your detailed explanation in 2-3 sentences]

Example:
DECISION: ON
CONFIDENCE: 85
REASONING: Temperature is 35°C with 80% humidity, making it very uncomfortable. High rain probability of 75% suggests incoming rain. Turning on relay for cooling/protection.

Now analyze and respond:
```

---

## 🎯 ตัวอย่างคำตอบจาก Gemini AI

**กรณีฝนตก:**
```
DECISION: ON
CONFIDENCE: 95
REASONING: Heavy rain is currently occurring with 90% rain probability and 100% cloud coverage. High humidity at 89% also suggests continued wet conditions. Relay activation is recommended for protection.
```

**กรณีอากาศดี:**
```
DECISION: OFF
CONFIDENCE: 80
REASONING: Temperature is comfortable at 28°C with moderate humidity of 55%. Clear weather with only 10% rain probability indicates no need for relay activation. Energy efficiency suggests keeping relay off.
```

**กรณีร้อนจัด:**
```
DECISION: ON
CONFIDENCE: 90
REASONING: Extreme temperature of 35°C with high humidity of 75% creates uncomfortable conditions. Feels-like temperature of 40°C indicates heat stress risk. Relay activation recommended for cooling or ventilation.
```

---

## 🔧 Fallback Logic (เมื่อ AI ไม่พร้อมใช้งาน)

ระบบมี rule-based logic สำรอง:

### เปิด Relay (ON):
- `อุณหภูมิ > 32°C` **และ** `ความชื้น > 70%`
- `โอกาสฝนตก > 60%`

### ปิด Relay (OFF):
- `อุณหภูมิ < 30°C` **และ** `ความชื้น < 60%`
- สภาพอากาศปานกลาง

**ตัวอย่างการทำงาน:**
```python
# อุณหภูมิ 33°C, ความชื้น 75%
Decision: ON
Confidence: 70%
Reasoning: "High temperature (33°C) and humidity (75%). Using fallback logic."

# อุณหภูมิ 28°C, ความชื้น 55%
Decision: OFF
Confidence: 70%
Reasoning: "Comfortable temperature (28°C) and humidity (55%). Using fallback logic."

# โอกาสฝนตก 85%
Decision: ON
Confidence: 60%
Reasoning: "High rain probability (85%). Using fallback logic."
```

---

## 📊 วิธีการ Parse คำตอบจาก AI

ระบบจะอ่านคำตอบจาก Gemini และแยกข้อมูล:

```python
def _parse_response(self, response_text: str):
    # หา DECISION: ON หรือ OFF
    if line.startswith('DECISION:'):
        decision = 'on' if 'on' in line.lower() else 'off'
    
    # หา CONFIDENCE: 0-100
    elif line.startswith('CONFIDENCE:'):
        confidence = float(number) / 100.0  # แปลงเป็น 0.0-1.0
    
    # หา REASONING: คำอธิบาย
    elif line.startswith('REASONING:'):
        reasoning = line.replace('REASONING:', '').strip()
```

---

## 🎨 การปรับแต่ง Prompt

### เพิ่มเงื่อนไขใหม่:
แก้ไขในส่วน **Decision Rules** ของ prompt:

```python
# ตัวอย่าง: เพิ่มเงื่อนไขลมแรง
**Decision Rules:**
1. Turn ON if:
   - Temperature > 32°C AND Humidity > 70%
   - Rain probability > 60%
   - Wind speed > 10 m/s  # ← เพิ่มใหม่
   - Thunderstorm or heavy rain expected
   - Extreme weather conditions
```

### เปลี่ยนค่า Threshold:
```python
# อุณหภูมิเดิม: > 32°C
# เปลี่ยนเป็น: > 30°C
- Temperature > 30°C AND Humidity > 70%
```

### เพิ่มบริบทเฉพาะ:
```python
**System Purpose:**
This relay controls a cooling fan in a server room.
Priority: Prevent overheating over energy saving.
```

---

## 🔍 ดู Logs การทำงาน

ตรวจสอบ logs ใน Django console:

```
🤖 Starting AI Weather Analysis...
==================================================
📡 Fetching weather from OpenWeatherMap...
✅ Weather data fetched successfully
🧠 Asking Gemini AI for decision...
✅ AI Decision: ON (Confidence: 95.0%)
💭 Reasoning: Heavy rain is currently occurring...
📡 Sending command to Relay 2: ON
✅ Relay command successful
✅ Decision logged to database
==================================================
🎯 Summary: ON | Confidence: 95.0% | Success: True
==================================================
```

---

## 📚 ไฟล์ที่เกี่ยวข้อง

1. **Prompt Creation:** `iot_dashboard/ai_agent/gemini_agent.py` (line 68-115)
2. **Response Parsing:** `iot_dashboard/ai_agent/gemini_agent.py` (line 117-155)
3. **Fallback Logic:** `iot_dashboard/ai_agent/gemini_agent.py` (line 157-185)
4. **Scheduler:** `iot_dashboard/ai_agent/scheduler.py`
5. **API Endpoints:** `iot_dashboard/views_simple.py` (line 1200+)

---

## 🎯 สรุป

**Prompt นี้ทำให้ Gemini AI:**
- ✅ เข้าใจบทบาทเป็น IoT Controller
- ✅ รับข้อมูลสภาพอากาศแบบละเอียด
- ✅ ใช้กฎการตัดสินใจที่ชัดเจน
- ✅ ตอบกลับในรูปแบบที่กำหนด (DECISION, CONFIDENCE, REASONING)
- ✅ คำนึงถึง comfort, energy efficiency, และสภาพอากาศ

**ผลลัพธ์:** AI ตัดสินใจได้อย่างสมเหตุสมผลและอธิบายได้!
