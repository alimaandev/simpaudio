@echo off
cd /d "%~dp0"

echo Ensuring dependencies are installed...
pip install -r requirements.txt

echo Building executable...
python -m PyInstaller --onedir --noconfirm --clean ^
    --name "Simpaudio" --windowed ^
    --icon "icon.ico" ^
    --version-file "version_info.txt" ^
    --add-data "icon.ico;." ^
    --hidden-import piper.voice ^
    --hidden-import piper.config ^
    --hidden-import piper.const ^
    --hidden-import piper.phoneme_ids ^
    --hidden-import piper.phonemize_espeak ^
    --hidden-import piper.tashkeel ^
    --hidden-import piper.download_voices ^
    --hidden-import kokoro ^
    --collect-data kokoro ^
    --hidden-import ebooklib ^
    --hidden-import pypdf ^
    --hidden-import ttkbootstrap ^
    --collect-data ttkbootstrap ^
    --hidden-import faster_whisper ^
    --hidden-import av ^
    --hidden-import pydub ^
    --hidden-import soundfile ^
    --exclude-module PyQt5 ^
    --exclude-module PyQt6 ^
    --exclude-module matplotlib ^
    app.py

echo.
echo Build complete! Executable is in: dist\Simpaudio\Simpaudio.exe
echo.
echo Optional next steps:
echo   - Create setup installer:  ISCC installer.iss
echo   - Create portable zip:     python package_portable.py
pause