import json
from pathlib import Path

__version__ = "1.0.0"

_FFMPEG_CONFIGURED = False


def configure_ffmpeg() -> None:
    global _FFMPEG_CONFIGURED
    if _FFMPEG_CONFIGURED:
        return
    _FFMPEG_CONFIGURED = True
    try:
        from pydub import AudioSegment
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if exe and Path(exe).exists():
            AudioSegment.converter = exe
    except Exception:
        pass

SETTINGS_FILE = Path.home() / ".simpaudio_settings.json"
VOICES_DIR = Path.home() / ".simpaudio_voices"
CLONED_DIR = VOICES_DIR / "cloned"
ERROR_LOG = Path.home() / ".simpaudio_error.log"
WINDOW_TITLE = "Simpaudio - Offline Voice Studio"
WINDOW_SIZE = (900, 720)

LANGUAGES = {
    "English (US)": {
        "piper": ["en_US-lessac-medium", "en_US-amy-medium", "en_US-ryan-medium", "en_US-arnold-medium", "en_US-dave-medium", "en_US-kathleen-medium"],
        "kokoro": ["af_heart", "af_bella", "af_nicole", "af_sarah", "af_sky", "am_adam", "am_michael", "am_fenrir"],
    },
    "English (UK)": {
        "piper": ["en_GB-alan-medium", "en_GB-semi-medium"],
        "kokoro": ["bf_emma", "bf_isabella", "bm_george", "bm_lewis"],
    },
    "Spanish": {
        "piper": ["es_ES-carlfm-x_low", "es_ES-davefx-medium", "es_ES-sharvard-medium"],
        "kokoro": ["ef_dora", "ef_maria", "em_alex", "em_santiago"],
    },
    "French": {
        "piper": ["fr_FR-siwis-medium", "fr_FR-siwis-low"],
        "kokoro": ["ff_siwis"],
    },
    "Italian": {
        "piper": ["it_IT-paola-medium"],
        "kokoro": ["if_sara", "im_nicola"],
    },
    "Portuguese (BR)": {
        "piper": ["pt_BR-edresson-medium", "pt_BR-faber-medium"],
        "kokoro": ["pf_dora", "pf_leticia", "pm_vitor"],
    },
    "Chinese": {
        "piper": ["zh_CN-huayan-medium", "zh_CN-xiaoxuan-medium"],
        "kokoro": ["zf_xiaobei", "zf_xiaoni", "zf_xiaoxiao", "zm_yunjian", "zm_yunxi", "zm_yunyang"],
    },
    "Japanese": {
        "piper": [],
        "kokoro": ["jf_alpha", "jf_gongitsune", "jf_nezumi", "jf_tebukuro", "jm_kumo"],
    },
}

OUTPUT_FORMATS = ["WAV", "MP3"]

SORTED_LANGUAGES = sorted(LANGUAGES.keys())

ENGINES = ["Piper TTS", "Kokoro TTS"]

KOKORO_TO_LANG = {
    'en-us': 'English (US)', 'en-gb': 'English (UK)',
    'es': 'Spanish', 'fr-fr': 'French', 'it': 'Italian',
    'pt-br': 'Portuguese (BR)', 'zh': 'Chinese', 'ja': 'Japanese',
}


class Config:
    def __init__(self):
        self.last_language: str = SORTED_LANGUAGES[0]
        self.last_voice: str = ""
        self.last_folder: str = str(Path.home() / "Desktop")
        self.theme: str = "light"
        self.speed: float = 1.0
        self.volume: float = 1.0
        self.sentence_silence: float = 0.3
        self.last_engine: str = ENGINES[0]
        self.last_format: str = "WAV"
        self.load()

    def load(self):
        try:
            data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
            self.last_language = data.get("last_language", self.last_language)
            self.last_voice = data.get("last_voice", self.last_voice)
            self.last_folder = data.get("last_folder", self.last_folder)
            self.theme = data.get("theme", self.theme)
            self.speed = data.get("speed", self.speed)
            self.volume = data.get("volume", self.volume)
            self.sentence_silence = data.get("sentence_silence", self.sentence_silence)
            self.last_engine = data.get("last_engine", self.last_engine)
            self.last_format = data.get("last_format", self.last_format)
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def save(self):
        try:
            SETTINGS_FILE.write_text(
                json.dumps({
                    "last_language": self.last_language,
                    "last_voice": self.last_voice,
                    "last_folder": self.last_folder,
                    "theme": self.theme,
                    "speed": self.speed,
                    "volume": self.volume,
                    "sentence_silence": self.sentence_silence,
                    "last_engine": self.last_engine,
                    "last_format": self.last_format,
                }, indent=2),
                encoding="utf-8",
            )
        except OSError:
            pass