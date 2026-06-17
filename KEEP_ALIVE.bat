@echo off
echo Starting Ai Anveshana Platform Watchdog...
echo Server will auto-restart if it crashes.
echo Log: %~dp0watchdog.log
echo.

REM Run the watchdog in a minimized background window
start "AiAnveshana-Watchdog" /MIN powershell.exe -ExecutionPolicy Bypass -WindowStyle Minimized -File "%~dp0watchdog.ps1"

echo Watchdog launched! Check watchdog.log for status.
echo Close the minimized "AiAnveshana-Watchdog" window to stop the server.
timeout /t 5
