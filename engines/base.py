from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, List, Optional


class TTSBackend(ABC):
    name: str = ""

    @abstractmethod
    def generate(
        self,
        text: str,
        voice: str,
        speed: float,
        volume: float,
        output_path: Path,
        status_callback: Optional[Callable[[str], None]] = None,
    ) -> Path:
        ...

    @abstractmethod
    def get_available_voices(self, language: str) -> List[str]:
        ...

    @abstractmethod
    def load(self) -> None:
        ...

    def unload(self) -> None:
        pass

    def get_last_segments(self) -> List[dict]:
        return []