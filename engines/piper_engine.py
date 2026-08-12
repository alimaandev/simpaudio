import os
import threading
import wave
from pathlib import Path
from typing import List, Optional

from piper import PiperVoice, SynthesisConfig
from piper.download_voices import download_voice

from .base import TTSBackend
from utils import VOICES_DIR, LANGUAGES


def _voice_model_path(voice: str) -> Path:
    return VOICES_DIR / f"{voice}.onnx"


def _voice_config_path(voice: str) -> Path:
    return VOICES_DIR / f"{voice}.onnx.json"


def _ensure_voice_downloaded(voice: str, status_callback=None) -> None:
    model_path = _voice_model_path(voice)
    if model_path.exists():
        return
    VOICES_DIR.mkdir(parents=True, exist_ok=True)
    if status_callback:
        status_callback(f"Downloading Piper voice '{voice}' (one-time, ~60 MB)...")
    download_voice(voice, VOICES_DIR)


class PiperBackend(TTSBackend):
    name = "Piper TTS"

    def __init__(self):
        self._voice: Optional[PiperVoice] = None
        self._lock = threading.Lock()
        self._current_voice_name: Optional[str] = None

    def load(self) -> None:
        pass

    def unload(self) -> None:
        self._voice = None
        self._current_voice_name = None

    def get_available_voices(self, language: str) -> List[str]:
        return LANGUAGES.get(language, {}).get("piper", [])

    def generate(self, text: str, voice: str, speed: float, volume: float, output_path: Path, status_callback=None) -> Path:
        _ensure_voice_downloaded(voice, status_callback)

        with self._lock:
            if self._current_voice_name != voice:
                model_path = _voice_model_path(voice)
                config_path = _voice_config_path(voice)
                self._voice = PiperVoice.load(model_path, config_path)
                self._current_voice_name = voice

        syn_config = SynthesisConfig(
            length_scale=1.0 / max(0.1, speed),
            volume=max(0.0, volume),
        )

        chunks = list(self._voice.synthesize(text, syn_config=syn_config))
        if not chunks:
            raise RuntimeError("No audio was generated.")

        sample_rate = self._voice.config.sample_rate
        temp_wav = output_path.with_suffix(".wav")

        with wave.open(str(temp_wav), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            for chunk in chunks:
                wav_file.writeframes(chunk.audio_int16_bytes)

        ext = output_path.suffix.lower()
        if ext == ".wav":
            if str(temp_wav) != str(output_path):
                os.replace(str(temp_wav), str(output_path))
        elif ext == ".mp3":
            from pydub import AudioSegment
            segment = AudioSegment.from_wav(str(temp_wav))
            segment.export(str(output_path), format="mp3", bitrate="192k")
            temp_wav.unlink(missing_ok=True)

        return output_path