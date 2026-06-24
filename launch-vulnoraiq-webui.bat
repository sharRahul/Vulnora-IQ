@echo off
REM VulnoraIQ Web UI double-click launcher for Windows.
cd /d "%~dp0"
echo Starting VulnoraIQ Web UI...
where py >nul 2>nul
if %ERRORLEVEL%==0 (
  py scripts\bootstrap_launch.py %*
) else (
  python scripts\bootstrap_launch.py %*
)
echo VulnoraIQ Web UI launcher has stopped.
pause
