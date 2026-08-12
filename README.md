# 🎙️ Simpaudio — Offline Voice Studio

**Free, offline, open-source voice toolkit for Windows.** Text-to-Speech, voice blending, audiobook generation, and speech-to-text — no cloud, no accounts, no data leaves your PC.

## ✨ Features

| Tab | What it does |
|-----|--------------|
| **🎙 Text to Speech** | 40+ realistic voices across 8 languages (English US/UK, Spanish, French, Italian, Portuguese, Chinese, Japanese). Speed/volume control, WAV or MP3 export, **SRT subtitle export**, visual **SSML editor** for fine-grained pronunciation control |
| **🎤 Voice Blending** | Combine 2+ voices into a custom blended voice (unique results, like a voice DNA mix) |
| **📖 Studio** | Import manuscripts (`.txt`, `.md`, `.epub`, `.pdf`) → auto-chapter detection → assign voices per chapter → full audiobook generation with optional concatenation and per-chapter subtitles |
| **🎧 Transcribe** | Offline speech-to-text with Whisper. Copy or save as TXT/SRT. 9 languages + auto-detect |

## 🖥 System Requirements

- Windows 10 or 11 (64-bit)
- ~2 GB free disk space (after download)
- 4 GB RAM recommended

## ⬇️ Download

Grab the latest release from the **[Releases page](https://github.com/alimaandev/simpaudio/releases)**:

| File | Best for |
|------|----------|
| `Simpaudio_Setup_1.0.0.exe` | **Recommended.** Full installer with Start Menu/Desktop shortcuts |
| `Simpaudio_Portable.zip` | No-install version — unzip anywhere and run `Simpaudio.exe` |

The installer is ~400 MB because it bundles the complete AI runtime (Piper + Kokoro + Whisper) — so **everything runs fully offline, forever, after first setup**.

### 🔒 On first launch (one-time, needs internet)

Voice models are downloaded on demand and cached in `%USERPROFILE%\.simpaudio_voices`:
1. **Piper voices** — ~60 MB each, downloaded the first time you use a voice
2. **Kokoro model** — ~340 MB once (higher-quality voices)
3. **Whisper model** — ~150 MB once (transcription)

Every voice used only downloads once — speech itself always works offline.

### ⚠️ Windows SmartScreen

The installer is **not code-signed** (signing certificates are expensive). Windows may show "Windows protected your PC". Click **More info → Run anyway**. It's safe — the app is 100% offline and never phones home.

## 📖 Quick Start

1. Install or unzip Simpaudio
2. Open the **Text to Speech** tab
3. Choose a language + voice, type your text
4. Click **Choose Save Location**, then **Generate Audio**
5. Preview or play your file — done!

For long-form work: use **Studio** for books/podcasts and **Transcribe** to turn audio back into text.

## 🧱 Built With

| Component | Purpose | License |
|-----------|---------|---------|
| [Piper TTS](https://github.com/rhasspy/piper) | Fast CPU text-to-speech (40+ voices) | MIT |
| [Kokoro TTS](https://github.com/hexgrad/kokoro) | High-quality neural voices + voice blending | Apache 2.0 |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | Offline speech recognition | MIT |
| [ttkbootstrap](https://github.com/israel-dryer/ttkbootstrap) | Modern themed UI | MIT |

## 🛠 Building from Source

```bat
python -m venv venv
venv\Scripts\pip install -r requirements.txt
python app.py
```

License: [MIT](LICENSE) — use it, modify it, sell it, whatever. Just keep the copyright notice.