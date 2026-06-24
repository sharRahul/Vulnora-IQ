@echo off
REM VulnoraIQ browser GUI double-click launcher for Windows.
cd /d "%~dp0"
echo Starting VulnoraIQ browser GUI — Docker containers will run in the background.
where py >nul 2>nul
if %ERRORLEVEL%==0 (
  py scripts\bootstrap_launch.py %*
) else (
  python scripts\bootstrap_launch.py %*
)
echo.
echo Docker containers are still running. To stop them later, run:
echo   docker compose down
pause
