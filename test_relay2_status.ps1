# Test Relay 2 Status Sync

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🔍 ทดสอบสถานะ Relay 2" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Get AI Status API
Write-Host "1️⃣ ตรวจสอบจาก AI Status API:" -ForegroundColor Yellow
try {
    $aiStatus = Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/ai/status/' -Method Get
    Write-Host "   Relay 2 Current Status: " -NoNewline
    if ($aiStatus.data.relay2_current_status) {
        Write-Host "🟢 ON" -ForegroundColor Green
    } else {
        Write-Host "⚫ OFF" -ForegroundColor Red
    }
    
    if ($aiStatus.data.latest_decision) {
        Write-Host "   Latest AI Decision: $($aiStatus.data.latest_decision.decision.ToUpper())"
        Write-Host "   AI Decision Time: $($aiStatus.data.latest_decision.timestamp)"
    }
} catch {
    Write-Host "   ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# 2. Get Relay API
Write-Host "2️⃣ ตรวจสอบจาก Relay API:" -ForegroundColor Yellow
try {
    $relayStatus = Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/relay/' -Method Get
    Write-Host "   Relay 2 Status: " -NoNewline
    if ($relayStatus.data.relay2_status) {
        Write-Host "🟢 ON" -ForegroundColor Green
    } else {
        Write-Host "⚫ OFF" -ForegroundColor Red
    }
    Write-Host "   Last Updated: $($relayStatus.data.last_updated)"
} catch {
    Write-Host "   ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "3️⃣ ทดสอบการ Sync:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   วิธีทดสอบ:" -ForegroundColor White
Write-Host "   1. เปิด Main Dashboard: http://localhost:8000/"
Write-Host "   2. สั่ง Relay 2 ON/OFF ผ่านปุ่ม"
Write-Host "   3. Refresh AI Dashboard: http://localhost:8000/ai/"
Write-Host "   4. ตรวจสอบว่า 'Relay 2 Status' เปลี่ยนตามหรือไม่"
Write-Host ""
Write-Host "   ✅ ถ้าสถานะเปลี่ยนตาม = Sync สำเร็จ!"
Write-Host "   ❌ ถ้าสถานะไม่เปลี่ยน = มีปัญหา"
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
