from pathlib import Path
from typing import Callable, Optional


class WhisperSTT:
    def __init__(self, model_size="base", device="auto"):
        self.model_size = model_size
        self._model = None
        self._device = device

    def _load(self, status_callback: Optional[Callable[[str], None]] = None):
        if self._model is not None:
            return
        from faster_whisper import WhisperModel
        if status_callback:
            status_callback(f"Downloading Whisper model '{self.model_size}' (one-time)...")
        self._model = WhisperModel(self.model_size, device=self._device, compute_type="int8")

    def transcribe(self, audio_path: Path, language: Optional[str] = None, status_callback: Optional[Callable[[str], None]] = None):
        self._load(status_callback)
        segments, info = self._model.transcribe(
            str(audio_path), language=language, beam_size=5,
        )
        return {
            "language": info.language,
            "duration": info.duration,
            "segments": list(segments),
        }

    def list_models(self):
        return ["tiny", "base", "small", "medium", "large-v3"]