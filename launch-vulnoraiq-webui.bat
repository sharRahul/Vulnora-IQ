@echo off
setlocal EnableExtensions

REM VulnoraIQ Desktop Mode launcher for Windows.
REM Source checkouts require Python 3.10+ on PATH.
REM Docker Desktop is required for Docker-based runtime features.

cd /d "%~dp0"

where py >nul 2>nul
if %ERRORLEVEL%==0 (
  py scripts\desktop_launch.py %*
  goto done
)

where python >nul 2>nul
if %ERRORLEVEL%==0 (
  python scripts\desktop_launch.py %*
  goto done
)

echo Python was not found on PATH.
echo For source checkouts, install Python 3.10+ or use:
echo   launch-vulnoraiq-docker-lab.bat
echo.
:done
pause
