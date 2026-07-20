@echo off
cd /d "%~dp0"
title Simpaudio Uninstaller

net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo.
echo Removing Simpaudio...
echo.

:: Kill running instance
taskkill /f /im Simpaudio.exe >nul 2>&1

:: Remove shortcuts
del /q "%AppData%\Microsoft\Windows\Start Menu\Programs\Simpaudio\Simpaudio.lnk" >nul 2>&1
rd "%AppData%\Microsoft\Windows\Start Menu\Programs\Simpaudio" >nul 2>&1
del /q "%USERPROFILE%\Desktop\Simpaudio.lnk" >nul 2>&1

:: Remove program files
rd /s /q "%ProgramFiles%\Simpaudio" >nul 2>&1

echo.
echo ========================================
echo   Simpaudio has been uninstalled.
echo ========================================
echo.
pause
