# Helper script to run demos with proper auth token setup

# Step 1: Get auth token
Write-Host "Getting auth token..." -ForegroundColor Yellow
$output = python auth.py
$token = ($output | Select-Object -Last 1).Trim()

if (-not $token) {
    Write-Host "Failed to get auth token!" -ForegroundColor Red
    exit 1
}

Write-Host "Token obtained: $($token.Substring(0,20))..." -ForegroundColor Green

# Step 2: Set environment variable
$env:EVAL_AUTH_TOKEN = $token

# Step 3: Run Scheduler
Write-Host "`n========== VEHICLE MAINTENANCE SCHEDULER ==========" -ForegroundColor Cyan
Push-Location vehicle_maintence_scheduler
python scheduler.py
Pop-Location

# Step 4: Run Priority Inbox
Write-Host "`n========== PRIORITY INBOX - STAGE 6 DEMO ==========" -ForegroundColor Cyan
Push-Location notification_app_be
python priority_inbox.py
Pop-Location

Write-Host "`nDone! Take screenshots with Windows+Shift+S" -ForegroundColor Green
