from pathlib import Path
from typing import List


def _fmt_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _group_segments(segments: List[dict]) -> List[dict]:
    if not segments:
        return []
    groups = []
    current = {"text": "", "start": segments[0]["start"], "end": segments[0]["end"]}
    for seg in segments:
        text = seg.get("text", "")
        if not text:
            continue
        if current["text"] and text[0] in ".!?":
            current["text"] += text
            current["end"] = seg["end"]
            groups.append(current)
            current = {"text": "", "start": None, "end": None}
        else:
            if current["text"]:
                current["text"] += text
            else:
                current["text"] = text
                current["start"] = seg["start"]
            current["end"] = seg["end"]
    if current["text"]:
        groups.append(current)
    return groups


def export_srt(segments: List[dict], output_path: Path) -> Path:
    groups = _group_segments(segments)
    lines = []
    for i, g in enumerate(groups, 1):
        start = _fmt_time(g["start"])
        end = _fmt_time(g["end"])
        text = g["text"].strip()
        lines.append(str(i))
        lines.append(f"{start} --> {end}")
        lines.append(text)
        lines.append("")
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def export_vtt(segments: List[dict], output_path: Path) -> Path:
    groups = _group_segments(segments)
    lines = ["WEBVTT", ""]
    for g in groups:
        start = _fmt_time(g["start"]).replace(",", ".")
        end = _fmt_time(g["end"]).replace(",", ".")
        text = g["text"].strip()
        lines.append(f"{start} --> {end}")
        lines.append(text)
        lines.append("")
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path