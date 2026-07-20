@echo off
cd /d "%~dp0"
title Simpaudio Installer

echo ========================================
echo   Simpaudio - Offline Text to Speech
echo   Installing...
echo ========================================
echo.

:: Check admin rights
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

set "APP_DIR=%ProgramFiles%\Simpaudio"
set "MENU_DIR=%AppData%\Microsoft\Windows\Start Menu\Programs\Simpaudio"

echo Installing to: %APP_DIR%
echo.

:: Stop if already running
taskkill /f /im Simpaudio.exe >nul 2>&1

:: Copy files
echo Copying files...
if not exist "%APP_DIR%" mkdir "%APP_DIR%"
xcopy /y /e /i /q "%~dp0dist\Simpaudio\*" "%APP_DIR%\" >nul
copy /y "%~dp0icon.ico" "%APP_DIR%\" >nul

:: Create shortcuts with PowerShell
echo Creating shortcuts...
powershell -Command ^
    $WS = New-Object -ComObject WScript.Shell; ^
    $S = $WS.CreateShortcut('%MENU_DIR%\Simpaudio.lnk'); ^
    $S.TargetPath = '%APP_DIR%\Simpaudio.exe'; ^
    $S.WorkingDirectory = '%APP_DIR%'; ^
    $S.IconLocation = '%APP_DIR%\icon.ico'; ^
    $S.Description = 'Offline Text-to-Speech Desktop Tool'; ^
    $S.Save(); ^
    $S2 = $WS.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\Simpaudio.lnk'); ^
    $S2.TargetPath = '%APP_DIR%\Simpaudio.exe'; ^
    $S2.WorkingDirectory = '%APP_DIR%'; ^
    $S2.IconLocation = '%APP_DIR%\icon.ico'; ^
    $S2.Description = 'Offline Text-to-Speech Desktop Tool'; ^
    $S2.Save(); ^
    $Uninstall = $WS.CreateShortcut('%APP_DIR%\Uninstall Simpaudio.lnk'); ^
    $Uninstall.TargetPath = '%~dp0uninstall_me.bat'; ^
    $Uninstall.Save()

echo.
echo ========================================
echo   Installation complete!
echo   Shortcuts added to Start Menu and Desktop
echo ========================================
echo.
pause
