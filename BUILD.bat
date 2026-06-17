@echo off
echo Building React frontend...
cd v2\frontend
call npm install
call npm run build
echo Build complete! Output in: v2/frontend/dist
pause
