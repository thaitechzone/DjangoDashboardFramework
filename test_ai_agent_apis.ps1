# ===================================
# AI Agent API Testing Script (PowerShell)
# ===================================

Write-Host ""
Write-Host "===================================" -ForegroundColor Cyan
Write-Host " AI Agent API Testing" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:8000"
$testsPassed = 0
$testsFailed = 0

function Test-Endpoint {
    param (
        [string]$TestName,
        [string]$Url,
        [string]$Method = "GET",
        [string[]]$ExpectedKeys
    )
    
    Write-Host "Testing: $TestName..." -ForegroundColor Yellow
    Write-Host "===================================" -ForegroundColor Gray
    
    try {
        if ($Method -eq "GET") {
            $response = Invoke-RestMethod -Uri $Url -Method Get -ContentType "application/json"
        } else {
            $response = Invoke-RestMethod -Uri $Url -Method Post -ContentType "application/json"
        }
        
        $allKeysFound = $true
        foreach ($key in $ExpectedKeys) {
            if (-not ($response | Get-Member -Name $key -MemberType Properties)) {
                $allKeysFound = $false
                Write-Host "[FAIL] Missing key: $key" -ForegroundColor Red
            }
        }
        
        if ($allKeysFound) {
            Write-Host "[OK] $TestName" -ForegroundColor Green
            $script:testsPassed++
            
            # Display some response data
            if ($response.status) {
                Write-Host "Status: $($response.status)" -ForegroundColor Gray
            }
            if ($response.data) {
                Write-Host "Data received: $(($response.data | ConvertTo-Json -Depth 1).Substring(0, [Math]::Min(100, ($response.data | ConvertTo-Json -Depth 1).Length)))..." -ForegroundColor Gray
            }
        } else {
            Write-Host "[FAIL] $TestName - Missing required keys" -ForegroundColor Red
            $script:testsFailed++
        }
    }
    catch {
        Write-Host "[FAIL] $TestName" -ForegroundColor Red
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
        $script:testsFailed++
    }
    
    Write-Host ""
}

# Test 1: AI Agent Status
Test-Endpoint -TestName "AI Agent Status" `
              -Url "$baseUrl/api/v1/ai/status/" `
              -ExpectedKeys @("status", "data")

# Test 2: Manual AI Analysis
Test-Endpoint -TestName "Manual AI Analysis" `
              -Url "$baseUrl/api/v1/ai/analyze-now/" `
              -Method "POST" `
              -ExpectedKeys @("status", "data")

# Test 3: AI Statistics
Test-Endpoint -TestName "AI Statistics (7 days)" `
              -Url "$baseUrl/api/v1/ai/stats/?days=7" `
              -ExpectedKeys @("status", "data")

# Test 4: Decision History
Test-Endpoint -TestName "Decision History" `
              -Url "$baseUrl/api/v1/ai/decisions/?limit=5&offset=0" `
              -ExpectedKeys @("status", "data", "pagination")

# Test 5: System Status
Test-Endpoint -TestName "System Status" `
              -Url "$baseUrl/api/v1/system/status/" `
              -ExpectedKeys @("status", "data")

# Summary
Write-Host "===================================" -ForegroundColor Cyan
Write-Host " Test Summary" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host "Passed: $testsPassed" -ForegroundColor Green
Write-Host "Failed: $testsFailed" -ForegroundColor Red
Write-Host "Total:  $($testsPassed + $testsFailed)" -ForegroundColor Cyan
Write-Host ""

if ($testsFailed -eq 0) {
    Write-Host "All tests passed! ✓" -ForegroundColor Green
} else {
    Write-Host "Some tests failed! ✗" -ForegroundColor Red
}
Write-Host ""
