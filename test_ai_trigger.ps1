# AI Agent Manual Trigger Test (PowerShell)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🤖 AI Agent Manual Trigger Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "กำลังสั่งให้ AI วิเคราะห์และควบคุม Relay 2..." -ForegroundColor Yellow
Write-Host ""

try {
    $result = Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/ai/analyze-now/' -Method Post
    
    if ($result.success) {
        Write-Host "✅ AI Analysis สำเร็จ!" -ForegroundColor Green
        Write-Host ""
        
        $decision = $result.data.latest_decision
        
        Write-Host "📊 ผลการตัดสินใจ:" -ForegroundColor Cyan
        Write-Host "  Decision: " -NoNewline
        if ($decision.decision -eq "on") {
            Write-Host "🟢 TURN ON" -ForegroundColor Green
        } else {
            Write-Host "⚫ TURN OFF" -ForegroundColor Red
        }
        
        Write-Host "  Confidence: $([math]::Round($decision.confidence * 100, 1))%"
        Write-Host "  Reasoning: $($decision.reasoning)"
        Write-Host ""
        
        Write-Host "⚡ Relay 2 Status:" -ForegroundColor Yellow
        Write-Host "  Current Status: " -NoNewline
        if ($decision.relay_status) {
            Write-Host "🟢 ON" -ForegroundColor Green
        } else {
            Write-Host "⚫ OFF" -ForegroundColor Red
        }
        Write-Host "  Command Sent: " -NoNewline
        if ($decision.command_sent) {
            Write-Host "✅ SUCCESS" -ForegroundColor Green
        } else {
            Write-Host "❌ FAILED" -ForegroundColor Red
        }
        Write-Host "  Timestamp: $($decision.timestamp)"
        Write-Host ""
        
        Write-Host "🌤️ ข้อมูลสภาพอากาศ:" -ForegroundColor Cyan
        $weather = $decision.weather_data
        Write-Host "  Location: $($weather.location)"
        Write-Host "  Temperature: $($weather.temperature)°C"
        Write-Host "  Humidity: $($weather.humidity)%"
        Write-Host "  Description: $($weather.description)"
        Write-Host "  Rain Probability: $($weather.rain_probability)%"
        Write-Host ""
        
    } else {
        Write-Host "❌ เกิดข้อผิดพลาด: $($result.error)" -ForegroundColor Red
    }
    
} catch {
    Write-Host "❌ เกิดข้อผิดพลาดในการเชื่อมต่อ API" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "📱 ตรวจสอบผลลัพธ์เพิ่มเติม:" -ForegroundColor Yellow
Write-Host "  • AI Dashboard: http://localhost:8000/ai/" -ForegroundColor White
Write-Host "  • Main Dashboard: http://localhost:8000/" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
