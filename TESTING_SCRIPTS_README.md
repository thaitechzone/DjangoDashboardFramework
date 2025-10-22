# 🧪 AI Agent Testing Scripts

This directory contains automated testing scripts for the AI Agent feature.

## 📁 Available Scripts

### 1. **test_ai_agent_apis.bat** (Windows CMD)
```cmd
test_ai_agent_apis.bat
```

**Features:**
- ✅ Tests all 5 AI Agent API endpoints
- ✅ Shows pass/fail status for each test
- ✅ Simple and fast execution
- ✅ Works in Windows Command Prompt

**Use Case:** Quick validation during development

---

### 2. **test_ai_agent_apis.ps1** (PowerShell)
```powershell
.\test_ai_agent_apis.ps1
```

**Features:**
- ✅ Advanced testing with detailed output
- ✅ Validates response structure
- ✅ Shows test summary (passed/failed count)
- ✅ Color-coded output
- ✅ Displays sample response data
- ✅ Better error handling

**Use Case:** Comprehensive testing with detailed feedback

**Note:** If you get an execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 🚀 Quick Start

### Prerequisites
1. Django server must be running on `http://localhost:8000`
2. curl must be installed (Windows 10+ has it built-in)
3. For PowerShell script: PowerShell 5.0 or higher

### Running Tests

**Option 1: CMD Script**
```cmd
# Navigate to project directory
cd d:\GitHub\DjangoDashboardFramework

# Run tests
test_ai_agent_apis.bat
```

**Option 2: PowerShell Script**
```powershell
# Navigate to project directory
cd d:\GitHub\DjangoDashboardFramework

# Run tests
.\test_ai_agent_apis.ps1
```

---

## 📊 What Gets Tested

Both scripts test these endpoints:

| # | Endpoint | Method | Description |
|---|----------|--------|-------------|
| 1 | `/api/v1/ai/status/` | GET | AI Agent status and recent decisions |
| 2 | `/api/v1/ai/analyze-now/` | POST | Trigger manual AI analysis |
| 3 | `/api/v1/ai/stats/?days=7` | GET | Statistics for last 7 days |
| 4 | `/api/v1/ai/decisions/?limit=5` | GET | Decision history (paginated) |
| 5 | `/api/v1/system/status/` | GET | Overall system status |

---

## 📋 Expected Output

### CMD Script Output
```
===================================
 AI Agent API Testing
===================================

[1/5] Testing AI Agent Status...
===================================
[OK] AI Agent Status API

[2/5] Triggering Manual AI Analysis...
===================================
[OK] Manual Trigger API

[3/5] Getting AI Statistics (7 days)...
===================================
[OK] Statistics API

[4/5] Getting Decision History...
===================================
[OK] Decision History API

[5/5] Getting System Status...
===================================
[OK] System Status API

===================================
 All Tests Completed!
===================================
```

### PowerShell Script Output
```
===================================
 AI Agent API Testing
===================================

Testing: AI Agent Status...
===================================
[OK] AI Agent Status
Status: success
Data received: {"is_running":true,"interval_minutes":15...

Testing: Manual AI Analysis...
===================================
[OK] Manual AI Analysis
Status: success
Data received: {"decision":"on","confidence":0.89...

...

===================================
 Test Summary
===================================
Passed: 5
Failed: 0
Total:  5

All tests passed! ✓
```

---

## 🔧 Troubleshooting

### Issue 1: "curl is not recognized"
**Solution:**
- Windows 10+: curl is built-in, make sure you're running in a fresh terminal
- Older Windows: Download curl from https://curl.se/windows/

### Issue 2: "Connection refused"
**Solution:**
- Make sure Django server is running: `python manage.py runserver`
- Check if server is on port 8000: http://localhost:8000

### Issue 3: PowerShell execution policy error
**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue 4: All tests fail
**Solution:**
1. Check Django server logs for errors
2. Verify database migrations are applied: `python manage.py migrate`
3. Check .env file has API keys configured
4. Try manual curl test:
   ```cmd
   curl http://localhost:8000/api/v1/ai/status/
   ```

### Issue 5: Tests pass but no AI decisions
**Solution:**
- Wait 15 minutes for automatic analysis, or
- Trigger manual analysis: `curl -X POST http://localhost:8000/api/v1/ai/analyze-now/`
- Check console for scheduler messages

---

## 📖 Related Documentation

- **AI_AGENT_GUIDE.md** - Complete user manual for AI Agent
- **README_AI_AGENT.md** - Feature overview and reference
- **POSTMAN_TESTING_GUIDE.md** - GUI-based testing with Postman
- **QUICK_START_TESTING.md** - Manual curl command reference

---

## 🎯 Testing Workflows

### Development Workflow
```cmd
# 1. Start server
python manage.py runserver

# 2. Run quick test (CMD)
test_ai_agent_apis.bat

# 3. If all pass, continue development
```

### CI/CD Integration
```powershell
# Use PowerShell script for detailed output
$result = .\test_ai_agent_apis.ps1
if ($LASTEXITCODE -ne 0) {
    Write-Error "Tests failed!"
    exit 1
}
```

### Pre-Deployment Checklist
1. ✅ Run PowerShell script: `.\test_ai_agent_apis.ps1`
2. ✅ All 5 tests should pass
3. ✅ Check Django logs for errors
4. ✅ Verify AI decisions are being created
5. ✅ Test Postman collection for detailed validation

---

## 💡 Tips

1. **Run tests regularly** during development to catch issues early
2. **Use CMD script** for quick checks, **PowerShell script** for detailed analysis
3. **Combine with Postman** for comprehensive API testing
4. **Check Django console** for scheduler status and logs
5. **Monitor database** to see AI decisions being saved

---

## 🔄 Continuous Testing

### Monitor AI Agent (CMD)
```cmd
@echo off
:loop
echo Testing at %time%...
test_ai_agent_apis.bat
timeout /t 60 /nobreak
goto loop
```

### Monitor AI Agent (PowerShell)
```powershell
while ($true) {
    Write-Host "Testing at $(Get-Date -Format 'HH:mm:ss')..." -ForegroundColor Cyan
    .\test_ai_agent_apis.ps1
    Start-Sleep -Seconds 60
}
```

---

## ✅ Success Criteria

All tests should pass with:
- ✅ Status code: 200 OK
- ✅ Response format: JSON
- ✅ Required keys present in response
- ✅ No server errors in console
- ✅ AI decisions logged in database

---

## 🚀 Next Steps

After all tests pass:
1. **Test Postman Collection** - Import and run full test suite
2. **Monitor AI Decisions** - Check admin panel or `/api/v1/ai/decisions/`
3. **Review AI Logic** - Read AI_AGENT_GUIDE.md for decision rules
4. **Configure Settings** - Adjust `.env` for your environment
5. **Deploy to Production** - Use these scripts for health checks

---

## 📞 Support

If tests continue to fail:
1. Check Django server logs for detailed errors
2. Review AI_AGENT_GUIDE.md troubleshooting section
3. Verify all dependencies are installed: `pip list`
4. Check database migrations: `python manage.py showmigrations`
5. Test with curl manually to isolate the issue

---

**Created:** December 2024  
**Version:** 1.0  
**Status:** Production Ready ✅
