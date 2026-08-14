"""Lightweight health check for Simpaudio.

Compiles all project Python files and imports the stdlib-only modules.
Writes the result to health/status.json (also usable as a local smoke test).
Exit code is 0 on success, 1 on failure.
"""
import json
import os
import py_compile
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", "venv", "build", "dist", "__pycache__", "installer", "health", ".github"}
IMPORT_MODULES = ["utils", "voice_presets", "srt_exporter", "ssml_parser"]
STATUS_FILE = ROOT / "health" / "status.json"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _py_files():
    files = []
    for p in ROOT.rglob("*.py"):
        if any(part in SKIP_DIRS for part in p.relative_to(ROOT).parts):
            continue
        files.append(p)
    return files


def run_check():
    errors = []

    for py_file in _py_files():
        try:
            py_compile.compile(str(py_file), doraise=True)
        except py_compile.PyCompileError as exc:
            errors.append(f"compile error in {py_file.relative_to(ROOT)}: {exc}")

    for module in IMPORT_MODULES:
        try:
            __import__(module)
        except Exception as exc:
            errors.append(f"import error in '{module}': {exc}")

    ok = not errors
    status = {
        "status": "ok" if ok else "fail",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "commit": os.environ.get("GITHUB_SHA", "local"),
        "python": sys.version.split()[0],
        "files_checked": len(_py_files()),
        "message": "" if ok else errors[0],
    }

    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATUS_FILE.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    print(f"health: {status['status']} ({status['timestamp']})")
    if errors:
        for err in errors[:5]:
            print(f"  {err}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(run_check())