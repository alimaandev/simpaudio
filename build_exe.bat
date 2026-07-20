@echo off
cd /d "%~dp0"

echo Creating virtual environment...
python -m venv venv

echo Installing dependencies...
call venv\Scripts\pip install piper-tts pydub pyinstaller

echo Building executable...
call venv\Scripts\python -m PyInstaller --onedir --noconfirm --clean ^
    --name "Simpaudio" --windowed ^
    --icon "icon.ico" ^
    --add-data "venv\Lib\site-packages\piper\espeak-ng-data;piper/espeak-ng-data" ^
    --add-data "icon.ico;." ^
    --hidden-import piper.voice --hidden-import piper.config ^
    --hidden-import piper.const --hidden-import piper.phoneme_ids ^
    --hidden-import piper.phonemize_espeak --hidden-import piper.tashkeel ^
    --hidden-import piper.download_voices app.py

echo.
echo Build complete! Executable is in: dist\Simpaudio\Simpaudio.exe
pause
