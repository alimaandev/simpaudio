import os
import sys
from pathlib import Path
from typing import List, Optional

import numpy as np
import torch
import soundfile as sf

from .base import TTSBackend
from utils import LANGUAGES


def _espeak_ng_dir() -> Path:
    if getattr(sys, "frozen", False):
        base = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
        return base / "espeak-ng"
    return Path(__file__).resolve().parent.parent / "assets" / "espeak-ng"


def _setup_espeak_ng() -> None:
    espeak_dir = _espeak_ng_dir()
    library = espeak_dir / "espeak-ng.dll"
    data = espeak_dir / "espeak-ng-data"
    if library.is_file():
        os.environ["PHONEMIZER_ESPEAK_LIBRARY"] = str(library)
    if data.is_dir():
        os.environ["ESPEAK_DATA_PATH"] = str(data)


def _patch_misaki_fallback() -> None:
    if getattr(_patch_misaki_fallback, "_done", False):
        return
    _patch_misaki_fallback._done = True
    from misaki import en
    from misaki.espeak import EspeakFallback

    original_init = en.G2P.__init__

    def init(self, *args, **kwargs):
        if kwargs.get("fallback") is True:
            british = kwargs.get("british", args[1] if len(args) > 1 else False)
            kwargs["fallback"] = EspeakFallback(british)
        original_init(self, *args, **kwargs)

    en.G2P.__init__ = init


_setup_espeak_ng()
_patch_misaki_fallback()


class KokoroBackend(TTSBackend):
    name = "Kokoro TTS"

    def __init__(self):
        self._pipeline = None
        self._model = None
        self._last_segments: List[dict] = []

    def load(self) -> None:
        pass

    def _get_pipeline(self, lang_code: str):
        from kokoro import KPipeline, KModel
        if self._model is None:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            self._model = KModel().to(device).eval()
        if self._pipeline is None or self._pipeline.lang_code != lang_code:
            self._pipeline = KPipeline(lang_code=lang_code, model=False)
        return self._pipeline

    def get_available_voices(self, language: str) -> List[str]:
        return LANGUAGES.get(language, {}).get("kokoro", [])

    def get_last_segments(self) -> List[dict]:
        return self._last_segments

    def generate(self, text: str, voice: str, speed: float, volume: float, output_path: Path, status_callback=None) -> Path:
        if self._model is None and status_callback:
            status_callback("Downloading Kokoro model (one-time, ~340 MB)...")
        lang_code = self._language_for_voice(voice)
        pipeline = self._get_pipeline(lang_code)

        all_audio = []
        self._last_segments = []
        sample_rate = 24000

        for result in pipeline(text, voice=voice, speed=speed, model=self._model):
            if result.audio is not None:
                audio = result.audio.cpu().numpy()
                audio = audio * volume
                all_audio.append(audio)
            if result.tokens:
                for t in result.tokens:
                    if hasattr(t, 'start_ts') and t.start_ts is not None and t.text:
                        self._last_segments.append({
                            "text": t.text,
                            "start": t.start_ts,
                            "end": t.end_ts if hasattr(t, 'end_ts') and t.end_ts is not None else t.start_ts + 0.1,
                        })

        if not all_audio:
            raise RuntimeError("No audio was generated.")

        full_audio = np.concatenate(all_audio)

        ext = output_path.suffix.lower()
        if ext == ".wav":
            sf.write(str(output_path), full_audio, sample_rate, subtype="PCM_16")
        elif ext == ".mp3":
            temp_wav = output_path.with_suffix(".wav")
            sf.write(str(temp_wav), full_audio, sample_rate, subtype="PCM_16")
            from pydub import AudioSegment
            segment = AudioSegment.from_wav(str(temp_wav))
            segment.export(str(output_path), format="mp3", bitrate="192k")
            temp_wav.unlink(missing_ok=True)
        else:
            sf.write(str(output_path), full_audio, sample_rate, subtype="PCM_16")

        return output_path

    def _language_for_voice(self, voice: str) -> str:
        first = voice.lstrip("*")[0] if voice else "a"
        mapping = {'a': 'a', 'b': 'b', 'e': 'e', 'f': 'f', 'i': 'i',
                   'p': 'p', 'j': 'j', 'z': 'z'}
        return mapping.get(first, 'a')