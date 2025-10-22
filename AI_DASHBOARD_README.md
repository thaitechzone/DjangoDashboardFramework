# 📊 AI Agent Dashboard - Quick Reference

## 🎯 What is AI Agent Dashboard?

A **real-time web dashboard** that visualizes AI Agent's weather-based decision making process for controlling Relay 2 using Google Gemini AI.

---

## 🚀 Quick Start

### 1. Start Django Server
```bash
python manage.py runserver
```

### 2. Access Dashboard
```
Main Dashboard:    http://localhost:8000/
AI Dashboard:      http://localhost:8000/ai/
```

### 3. Navigate
From Main Dashboard → Click **"🤖 AI Agent Dashboard"** button

---

## 📸 Dashboard Components

### 🎛️ Status Cards (4 cards)
| Card | Shows | Values |
|------|-------|--------|
| 🤖 AI Agent Status | Scheduler status | ✅ ACTIVE / ❌ INACTIVE |
| ⚡ Relay 2 Status | Current relay state | 🟢 ON / ⚫ OFF |
| 🎯 Last Decision | Most recent AI decision | Turn ON / Turn OFF |
| 📊 Confidence Score | AI decision confidence | 0-100% |

### 🌤️ Weather Card
Real-time weather for Nakhon Si Thammarat:
- 🌡️ Temperature
- 💧 Humidity
- ☁️ Weather Condition
- 🌧️ Rain Probability

### 📜 Decision Timeline
- Last 10 AI decisions
- Timestamp for each decision
- 💭 AI Reasoning
- 🎯 Confidence score with progress bar

### 📊 Statistics (7 days)
- Total Decisions
- ON Decisions (green)
- OFF Decisions (red)
- Average Confidence

### 📈 Charts
1. **Decision Trends** - Bar chart showing ON/OFF decisions per day
2. **Confidence Trend** - Line chart showing average confidence

---

## 🎮 Control Panel

| Button | Action | When to Use |
|--------|--------|-------------|
| 🤖 Trigger AI Analysis | Force AI to analyze immediately | Testing, weather changed suddenly |
| 📋 View All Decisions | Open decisions API (JSON) | Export data, detailed analysis |
| 📊 View Statistics | Open stats API (JSON) | Generate reports, debugging |

---

## 🔄 Auto-Update

Dashboard automatically refreshes every **10 seconds**:
- ✅ AI Status
- ✅ Relay Status  
- ✅ Decision Timeline
- ✅ Statistics & Charts

Manual refresh: Click **"🔄 Refresh Now"**

---

## 📖 Reading the Dashboard

### AI Status Indicators
```
✅ ACTIVE (green)   = AI is running, analyzing every 15 minutes
❌ INACTIVE (red)   = AI stopped, check console logs
```

### Confidence Score Guide
```
80-100% = High confidence (AI is very sure)
60-79%  = Medium confidence
0-59%   = Low confidence (may use fallback logic)
```

### Decision Timeline Format
```
[Time] 2024-12-21 14:30:00
[Decision] 🟢 Turn ON
[Reasoning] Temperature is 35°C and humidity is 85%. 
            High chance of rain (80%). Turn ON to prepare.
[Confidence] 🎯 89.5%
[Progress Bar] ████████░░ (89.5%)
```

---

## 📈 Understanding Charts

### Decision Trends Chart (Bar)
- **Green bars** = ON decisions
- **Red bars** = OFF decisions
- **Taller bars** = More decisions on that day

**What to look for:**
- Many green bars → Hot/rainy weather
- Many red bars → Good weather
- No bars → No data or AI inactive

### Confidence Score Trend (Line)
- **High line (>80%)** = AI confident in decisions
- **Low line (<60%)** = Uncertain conditions
- **Fluctuating** = Changing weather patterns

---

## 💡 Common Tasks

### Task 1: Check if AI is Working
```
1. Open Dashboard
2. Look at "🤖 AI Agent Status" card
3. Should show "✅ ACTIVE"
4. Check "Last Decision" has recent timestamp
```

### Task 2: Trigger Manual Analysis
```
1. Click "🤖 Trigger AI Analysis"
2. Confirm the popup
3. Wait 3-5 seconds
4. Check "Last Decision" updated
5. See new entry in Timeline
```

### Task 3: View Decision History
```
1. Scroll to "Decision Timeline" section
2. Read last 10 decisions
3. Check AI Reasoning for each
4. OR click "📋 View All Decisions" for full JSON
```

### Task 4: Analyze Performance
```
1. Look at Statistics section
2. Check ON vs OFF ratio
3. Check Average Confidence (should be >70%)
4. Review charts for trends
```

---

## 🔧 Quick Troubleshooting

| Problem | Quick Fix |
|---------|-----------|
| AI Status shows INACTIVE | Restart server, check console logs |
| Weather not showing | Check `OPENWEATHER_API_KEY` in `.env` |
| No decisions in timeline | Wait 15 min OR click "Trigger AI Analysis" |
| Charts not displaying | Check internet (Chart.js from CDN) |
| Dashboard not updating | Press F5, check Browser Console for errors |

---

## 📱 Mobile Support

✅ **Fully Responsive**
- Works on phones and tablets
- Auto-adjusts layout
- Touch-friendly buttons
- Readable on small screens

**Tip:** Use landscape mode for better chart viewing

---

## 🔗 API Endpoints Used

```
GET  /api/v1/ai/status/       → AI Agent status
GET  /api/v1/ai/decisions/    → Decision history
POST /api/v1/ai/analyze-now/  → Trigger analysis
GET  /api/v1/ai/stats/        → Statistics
GET  /api/v1/relay/           → Relay status
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **AI_DASHBOARD_GUIDE.md** | Complete dashboard user guide |
| **AI_AGENT_GUIDE.md** | Full AI Agent documentation |
| **README_AI_AGENT.md** | Feature overview |
| **POSTMAN_TESTING_GUIDE.md** | API testing guide |

---

## 🎯 Key Features

- ✅ Real-time monitoring
- ✅ Auto-refresh every 10 seconds
- ✅ Weather integration
- ✅ Decision history with reasoning
- ✅ Statistical analysis
- ✅ Interactive charts
- ✅ Manual trigger control
- ✅ Mobile responsive
- ✅ Beautiful UI with gradients

---

## ⚡ Performance

- **Load Time**: < 2 seconds
- **Update Frequency**: 10 seconds
- **API Calls**: ~6 per update cycle
- **Data Retention**: 7 days statistics

---

## 🎨 Color Coding

| Color | Meaning |
|-------|---------|
| 🟢 Green | Active, ON, Success |
| ⚫ Red | Inactive, OFF, Error |
| 🟡 Yellow | Warning, Relay ON |
| 🔵 Blue | Info, Links, AI Agent |
| ⚪ White | Cards, Background |

---

## 🚦 Status Indicators

```
🤖 AI Agent     → Purple gradient
⚡ Relay 2      → Yellow/Gray
🎯 Decision     → Blue
📊 Confidence   → Yellow
🌤️ Weather     → Purple gradient
```

---

## 📊 Sample Dashboard View

```
┌─────────────────────────────────────────────┐
│   🤖 AI Agent Dashboard                     │
│   Weather-Based Intelligent Relay Control   │
│   [🏠 Main] [🔄 Refresh]                   │
└─────────────────────────────────────────────┘

┌──────────┬──────────┬──────────┬──────────┐
│🤖 AI     │⚡ Relay 2│🎯 Last   │📊 Conf.  │
│✅ ACTIVE │🟢 ON     │🟢 Turn ON│89.5%     │
└──────────┴──────────┴──────────┴──────────┘

┌─────────────────────────────────────────────┐
│ 🌤️ Weather - Nakhon Si Thammarat          │
│ 🌡️35°C  💧85%  ☁️Cloudy  🌧️80%          │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ 🎮 Manual Control                           │
│ [🤖 Trigger] [📋 Decisions] [📊 Stats]     │
└─────────────────────────────────────────────┘

┌──────────┬──────────┬──────────┬──────────┐
│Total: 120│ON: 68    │OFF: 52   │Avg: 87%  │
└──────────┴──────────┴──────────┴──────────┘

┌─────────────────────────────────────────────┐
│ 📜 Decision Timeline                        │
│ ├─ 14:30 🟢 ON (89%) Reason: Hot & Rain    │
│ ├─ 14:15 🟢 ON (85%) Reason: High humidity │
│ └─ 14:00 ⚫ OFF (92%) Reason: Good weather │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ 📈 Decision Trends (7 days)                 │
│ [Bar Chart: ON/OFF per day]                 │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ 🎯 Confidence Score Trend                   │
│ [Line Chart: Avg confidence per day]        │
└─────────────────────────────────────────────┘
```

---

## ✅ First Use Checklist

- [ ] Django server running
- [ ] Access http://localhost:8000/ai/
- [ ] See "✅ ACTIVE" status
- [ ] Weather shows data
- [ ] Click "Trigger AI Analysis"
- [ ] New decision appears in timeline
- [ ] Statistics show numbers
- [ ] Charts display properly
- [ ] Auto-update works (wait 10 sec)
- [ ] All cards show data

---

## 🎓 Learning Path

1. **Week 1**: Understand dashboard components
2. **Week 2**: Learn to read AI reasoning
3. **Week 3**: Analyze decision patterns
4. **Week 4**: Optimize AI prompts based on data

---

## 🌟 Pro Tips

1. **Monitor Confidence**: If avg < 70%, review AI prompts
2. **Check Timeline**: AI Reasoning shows thought process
3. **Use Manual Trigger**: For testing, not production
4. **Analyze Charts**: Look for patterns, not just numbers
5. **Export Data**: Use "View All Decisions" for reports

---

## 🔐 Security Notes

⚠️ **Important:**
- Dashboard is read-mostly (safe)
- Only "Trigger AI Analysis" modifies state
- Don't expose publicly without auth
- Consider Django authentication for production

---

## 📞 Need Help?

1. Check **AI_DASHBOARD_GUIDE.md** for detailed guide
2. Review Django console logs
3. Open Browser Console (F12)
4. Check Network tab for API errors
5. Read API responses for error messages

---

## 🎯 Use Cases

| Scenario | How to Use Dashboard |
|----------|---------------------|
| **Monitor AI** | Check Status card, view timeline |
| **Debug Issues** | Read AI Reasoning, check confidence |
| **Analyze Performance** | Review charts and statistics |
| **Demo/Present** | Use manual trigger, show real-time updates |
| **Generate Reports** | Export data via API endpoints |

---

**Dashboard URL:** `http://localhost:8000/ai/`  
**Created:** December 2024  
**Status:** ✅ Production Ready  
**Auto-Update:** Every 10 seconds  
**Mobile:** ✅ Fully Responsive
