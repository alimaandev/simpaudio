import json
from pathlib import Path
from typing import Dict, List, Optional

PRESETS_FILE = Path.home() / ".simpaudio_presets.json"


def _load_all() -> Dict:
    if PRESETS_FILE.exists():
        try:
            return json.loads(PRESETS_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _save_all(data: Dict) -> None:
    PRESETS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def list_presets() -> List[str]:
    return sorted(_load_all().keys())


def get_preset(name: str) -> Optional[Dict]:
    return _load_all().get(name)


def save_preset(name: str, engine: str, voice: str, speed: float, volume: float, fmt: str) -> None:
    data = _load_all()
    data[name] = {
        "engine": engine,
        "voice": voice,
        "speed": speed,
        "volume": volume,
        "format": fmt,
    }
    _save_all(data)


def delete_preset(name: str) -> None:
    data = _load_all()
    data.pop(name, None)
    _save_all(data)


def rename_preset(old: str, new: str) -> bool:
    data = _load_all()
    if old not in data or new in data:
        return False
    data[new] = data.pop(old)
    _save_all(data)
    return True