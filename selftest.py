import sys
import tempfile
import traceback
from datetime import datetime
from pathlib import Path


def _record(log: Path, ok: bool, name: str, detail: str):
    line = f"[{'OK' if ok else 'FAIL'}] {name}: {detail}"
    print(line, flush=True)
    with open(log, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def run_selftest(log_path: Path) -> int:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.unlink(missing_ok=True)

    from utils import VOICES_DIR
    VOICES_DIR.mkdir(parents=True, exist_ok=True)

    tmp = Path(tempfile.mkdtemp(prefix="simpaudio_selftest_"))
    overall = True

    def check(name, fn):
        nonlocal overall
        try:
            fn()
            _record(log_path, True, name, "passed")
        except Exception as exc:
            overall = False
            _record(log_path, False, name, f"{type(exc).__name__}: {exc}")
            traceback.print_exc()

    def test_piper():
        from engines import create_engine
        engine = create_engine("Piper TTS")
        out = tmp / "piper_test.wav"
        engine.generate(
            "Hello world, this is a quick test of Piper speech synthesis.",
            "en_US-lessac-medium", 1.0, 1.0, out,
            status_callback=lambda m: None,
        )
        assert out.exists() and out.stat().st_size > 1000, "Piper output missing or empty"

    def test_kokoro():
        from engines import create_engine
        engine = create_engine("Kokoro TTS")
        out = tmp / "kokoro_test.wav"
        engine.generate(
            "Hello world, this is a quick test of Kokoro speech synthesis.",
            "af_heart", 1.0, 1.0, out,
            status_callback=lambda m: None,
        )
        assert out.exists() and out.stat().st_size > 1000, "Kokoro output missing or empty"

    def test_kokoro_blend():
        from engines import create_engine
        engine = create_engine("Kokoro TTS")
        out = tmp / "blend_test.wav"
        engine.generate(
            "This is a test of blended voices.",
            "af_heart,af_bella", 1.0, 1.0, out,
            status_callback=lambda m: None,
        )
        assert out.exists() and out.stat().st_size > 1000, "Blend output missing or empty"

    def test_whisper():
        from engines import create_engine
        from whisper_stt import WhisperSTT
        engine = create_engine("Piper TTS")
        wav = tmp / "whisper_fixture.wav"
        engine.generate(
            "The quick brown fox jumps over the lazy dog.",
            "en_US-lessac-medium", 1.0, 1.0, wav,
            status_callback=lambda m: None,
        )
        assert wav.exists() and wav.stat().st_size > 1000, "Whisper fixture missing"
        stt = WhisperSTT("tiny")
        result = stt.transcribe(wav, status_callback=lambda m: None)
        assert result["segments"], "No segments returned"
        text = " ".join(s.text for s in result["segments"])
        assert len(text.strip()) > 0, "Empty transcription"

    check("piper-tts", test_piper)
    check("kokoro-tts", test_kokoro)
    check("kokoro-blend", test_kokoro_blend)
    check("whisper-stt", test_whisper)

    _record(log_path, overall, "overall", "all checks passed" if overall else "FAILURES DETECTED")
    return 0 if overall else 1
