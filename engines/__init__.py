from .base import TTSBackend
from .piper_engine import PiperBackend
from .kokoro_engine import KokoroBackend

ENGINE_REGISTRY = {
    "Piper TTS": PiperBackend,
    "Kokoro TTS": KokoroBackend,
}


def create_engine(name: str) -> TTSBackend:
    cls = ENGINE_REGISTRY.get(name)
    if cls is None:
        raise ValueError(f"Unknown engine: {name}")
    return cls()