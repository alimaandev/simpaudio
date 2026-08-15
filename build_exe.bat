@echo off
cd /d "%~dp0"

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
    --hidden-import ebooklib ^
    --hidden-import pypdf ^
    --hidden-import ttkbootstrap ^
    --collect-data ttkbootstrap ^
    --hidden-import faster_whisper ^
    --hidden-import av ^
    --hidden-import pydub ^
    --hidden-import soundfile ^
    --collect-data piper ^
    --collect-data misaki ^
    --collect-data language_tags ^
    --add-data "assets\espeak-ng;espeak-ng" ^
    --collect-all en_core_web_sm ^
    --exclude-module yt_dlp ^
    --exclude-module gradio ^
    --exclude-module wandb ^
    --exclude-module diffusers ^
    --exclude-module sentry_sdk ^
    --exclude-module boto3 ^
    --exclude-module botocore ^
    --exclude-module s3transfer ^
    --exclude-module google ^
    --exclude-module grpc ^
    --exclude-module redis ^
    --exclude-module flask ^
    --exclude-module fastapi ^
    --exclude-module quart ^
    --exclude-module starlette ^
    --exclude-module uvicorn ^
    --exclude-module gevent ^
    --exclude-module zope ^
    --exclude-module httptools ^
    --exclude-module watchfiles ^
    --exclude-module websockets ^
    --exclude-module openai ^
    --exclude-module tiktoken ^
    --exclude-module plotly ^
    --exclude-module pandas ^
    --exclude-module numba ^
    --exclude-module llvmlite ^
    --exclude-module pytest ^
    --exclude-module _pytest ^
    --exclude-module sklearn ^
    --exclude-module cv2 ^
    --exclude-module faiss ^
    --exclude-module nltk ^
    --exclude-module sentencepiece ^
    --exclude-module sacremoses ^
    --exclude-module ftfy ^
    --exclude-module einops ^
    --exclude-module timm ^
    --exclude-module accelerate ^
    --exclude-module datasets ^
    --exclude-module pyarrow ^
    --exclude-module tables ^
    --exclude-module numexpr ^
    --exclude-module optuna ^
    --exclude-module ray ^
    --exclude-module torchvision ^
    --exclude-module torchaudio ^
    --exclude-module torchtext ^
    --exclude-module torchao ^
    --exclude-module onnx ^
    --exclude-module protobuf ^
    --exclude-module moviepy ^
    --exclude-module librosa ^
    --exclude-module gym ^
    --exclude-module jax ^
    --exclude-module tensorflow ^
    --exclude-module pywin32 ^
    --exclude-module win32 ^
    --exclude-module win32com ^
    --exclude-module pythoncom ^
    --exclude-module pywintypes ^
    --exclude-module Pythonwin ^
    --exclude-module PyQt5 ^
    --exclude-module PyQt6 ^
    --exclude-module PySide2 ^
    --exclude-module PySide6 ^
    --exclude-module matplotlib ^
    app.py

echo.
echo Build complete! Executable is in: dist\Simpaudio\Simpaudio.exe
echo.
echo Verify the frozen build with:
echo   dist\Simpaudio\Simpaudio.exe --selftest --selftest-log "%%TEMP%%\simpaudio_selftest.log"
echo.
echo Optional next steps:
echo   - Create setup installer:  ISCC installer.iss
echo   - Create portable zip:     python package_portable.py
pause
