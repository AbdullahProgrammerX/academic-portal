# Editorial System - Development Server Starter
# This script starts both backend and frontend servers

Write-Host "`n" -ForegroundColor Cyan
Write-Host "         EDITORIAL SYSTEM - DEV SERVER STARTER        " -ForegroundColor Cyan
Write-Host "" -ForegroundColor Cyan

# Check if backend venv exists
if (!(Test-Path "backend\venv\Scripts\Activate.ps1")) {
    Write-Host "Backend virtual environment not found!" -ForegroundColor Red
    Write-Host "Run: cd backend; python -m venv venv; .\venv\Scripts\Activate.ps1; pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

# Check if frontend node_modules exists
if (!(Test-Path "frontend\node_modules")) {
    Write-Host "Frontend node_modules not found!" -ForegroundColor Red
    Write-Host "Run: cd frontend; npm install" -ForegroundColor Yellow
    exit 1
}

Write-Host "Starting Backend Server (Django)..." -ForegroundColor Green
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    cd backend
    .\venv\Scripts\Activate.ps1
    python manage.py runserver 0.0.0.0:8000
}

Write-Host "Starting Frontend Server (Vite)..." -ForegroundColor Green
$frontendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    cd frontend
    npm run dev
}

Write-Host "`n" -ForegroundColor Green
Write-Host "         BOTH SERVERS STARTED!                        " -ForegroundColor Green
Write-Host "" -ForegroundColor Green

Write-Host "Access URLs:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "   Backend:  http://127.0.0.1:8000" -ForegroundColor White
Write-Host "   Admin:    http://127.0.0.1:8000/admin/`n" -ForegroundColor White

Write-Host "Job IDs:" -ForegroundColor Cyan
Write-Host "   Backend Job ID:  $($backendJob.Id)" -ForegroundColor Gray
Write-Host "   Frontend Job ID: $($frontendJob.Id)`n" -ForegroundColor Gray

Write-Host "Monitor logs:" -ForegroundColor Yellow
Write-Host "   Receive-Job -Id $($backendJob.Id) -Keep" -ForegroundColor Gray
Write-Host "   Receive-Job -Id $($frontendJob.Id) -Keep`n" -ForegroundColor Gray

Write-Host "Stop servers:" -ForegroundColor Yellow
Write-Host "   Stop-Job -Id $($backendJob.Id),$($frontendJob.Id)" -ForegroundColor Gray
Write-Host "   Remove-Job -Id $($backendJob.Id),$($frontendJob.Id)`n" -ForegroundColor Gray

Write-Host "Press Ctrl+C to stop monitoring (servers will keep running in background)" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

# Monitor jobs
try {
    while ($true) {
        Start-Sleep -Seconds 2
        
        # Check backend status
        $backendState = (Get-Job -Id $backendJob.Id).State
        if ($backendState -eq "Failed" -or $backendState -eq "Stopped") {
            Write-Host "Backend server stopped!" -ForegroundColor Red
            Receive-Job -Id $backendJob.Id
            break
        }
        
        # Check frontend status
        $frontendState = (Get-Job -Id $frontendJob.Id).State
        if ($frontendState -eq "Failed" -or $frontendState -eq "Stopped") {
            Write-Host "Frontend server stopped!" -ForegroundColor Red
            Receive-Job -Id $frontendJob.Id
            break
        }
    }
} catch {
    Write-Host "`nMonitoring stopped. Servers are still running in background." -ForegroundColor Yellow
}
