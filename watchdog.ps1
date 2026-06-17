# ============================================================
# Ai Anveshana Platform - Watchdog / Auto-Restart Script
# Keeps the FastAPI backend alive. Restarts on crash.
# Run this once; it loops forever in the background.
# ============================================================

$BackendDir  = "C:\Users\Admin\Documents\Agentic AI\backend"
$StartCmd    = "python -m uvicorn main:app --host 0.0.0.0 --port 8000"
$HealthUrl   = "http://localhost:8000/health"
$CheckEvery  = 15   # seconds between health checks
$StartDelay  = 8    # seconds to wait after launching before first health check
$LogFile     = "C:\Users\Admin\Documents\Agentic AI\watchdog.log"
$MaxLogLines = 500  # Rotate log when it gets too big

function Write-Log($msg) {
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$ts] $msg"
    Write-Host $line
    Add-Content -Path $LogFile -Value $line
    # Simple log rotation
    $lines = Get-Content $LogFile -ErrorAction SilentlyContinue
    if ($lines.Count -gt $MaxLogLines) {
        $lines | Select-Object -Last ($MaxLogLines / 2) | Set-Content $LogFile
    }
}

function Start-Server {
    Write-Log ">>> Starting server: $StartCmd"
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = "cmd.exe"
    $psi.Arguments = "/c cd /d `"$BackendDir`" && $StartCmd"
    $psi.WorkingDirectory = $BackendDir
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $false
    $proc = [System.Diagnostics.Process]::Start($psi)
    Write-Log ">>> Server process started (PID $($proc.Id))"
    return $proc
}

function Test-Server {
    try {
        $r = Invoke-WebRequest -Uri $HealthUrl -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
        return $r.StatusCode -eq 200
    } catch {
        return $false
    }
}

Write-Log "============================================"
Write-Log "Watchdog started. Monitoring $HealthUrl"
Write-Log "============================================"

$serverProc = $null
$restartCount = 0

while ($true) {
    # Check if process is still running
    $procAlive = ($serverProc -ne $null) -and (-not $serverProc.HasExited)

    if (-not $procAlive) {
        $restartCount++
        if ($restartCount -gt 1) {
            Write-Log "!!! Server process died (restart #$($restartCount - 1)). Relaunching..."
        }
        $serverProc = Start-Server
        Write-Log "Waiting $StartDelay seconds for server to boot..."
        Start-Sleep -Seconds $StartDelay
    }

    # Health check
    if (Test-Server) {
        Write-Log "OK - Server is healthy."
    } else {
        Write-Log "WARN - Health check FAILED. Killing process and restarting..."
        try { $serverProc.Kill() } catch {}
        $serverProc = $null
        Start-Sleep -Seconds 2
        $restartCount++
        $serverProc = Start-Server
        Start-Sleep -Seconds $StartDelay
    }

    Start-Sleep -Seconds $CheckEvery
}
