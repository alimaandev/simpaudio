<p align="center">
  <img src="assets/logo.png" alt="Simpaudio Logo" width="120">
</p>

<h1 align="center">✨ Simpaudio</h1>
<p align="center">
  <b>The Free, Offline Voice Studio for Creators Who Value Privacy</b><br>
  <sub>Professional TTS • Voice Blending • Audiobooks • Transcription</sub>
</p>

<p align="center">
  <a href="#-download"><img src="https://img.shields.io/badge/Download_Latest-4F46E5?style=for-the-badge&logo=windows&logoColor=white" alt="Download"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-10B981?style=for-the-badge" alt="MIT License"></a>
  <a href="#-dev-mode"><img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"></a>
</p>

<p align="center">
<video autoplay loop muted playsinline src="https://github.com/user-attachments/assets/93810a63-4849-4a8b-8086-bdd72ba9fce9" width="100%"></video>
</p>

> ### 💡 Your Voice, Your Hardware, Your Rules.
> Why rent a voice when you can own the studio? Simpaudio brings premium, offline AI voice generation to your Windows PC. No subscriptions, no cloud uploads, no tracking. Just pure, private creativity.

---

## 🎨 A Complete Creative Suite

Simpaudio isn't just a text-to-speech reader; it's a comprehensive audio production environment designed for writers, developers, and content creators.

| 🗣️ **Text to Speech** | 🧬 **Voice Blending** | 📚 **Audiobook Studio** | 🎧 **Smart Transcription** |
| :--- | :--- | :--- | :--- |
| Access 40+ premium voices across 8 languages. Export in WAV, MP3, or SRT. | Create unique "Voice DNA" by blending two models into a completely new persona. | Turn manuscripts into full audiobooks with per-chapter voice assignment & subtitles. | Whisper-powered STT that converts audio to TXT or SRT entirely on-device. |

---

## ☁️ Cloud vs. Local: The Freedom Choice

We believe creative tools should be accessible and private. Here is how local-first compares to traditional cloud services:

| Feature | Traditional Cloud TTS | ✨ Simpaudio |
| :--- | :--- | :--- |
| **Cost** | ~$22/month (limited chars) | **Free Forever** (Unlimited) |
| **Privacy** | Text processed on external servers | **100% Offline** (Data never leaves PC) |
| **Access** | Account & Login Required | **No Accounts / No Sign-up** |
| **Voice Cloning** | Often Paywalled | **Free & Unlimited Blending** |
| **Audiobooks** | Manual / Fragmented Workflow | **One-Click Generation** |
| **Availability** | Dependent on Internet/Uptime | **Works Anywhere, Anytime** |

---

## 🌟 Why Creators Choose Simpaudio

-   🔒 **True Privacy by Design:** Perfect for NDAs, sensitive journalism, or personal journals. Your scripts exist only on your disk.
-   🎧 **Production-Ready Audiobooks:** Import `.txt`, `.md`, `.epub`, or `.pdf`. Assign unique voices to chapters and export a cohesive audiobook with perfectly timed subtitles.
-   🎨 **Limitless Vocal Creativity:** Voice blending allows you to craft signature voices that no one else has. Because *you* generated them locally.
-   🤝 **Open Source & Transparent:** MIT Licensed. Not a "free tier" trap. Fork it, audit it, build upon it, or use it commercially.

---

## ⬇️ Get Started

### System Requirements

-   **OS:** Windows 10 / 11 (64-bit)
-   **Storage:** ~2 GB free space
-   **Memory:** 4 GB RAM recommended

### Download Options

| Package | Size | Best For |
| :--- | :--- | :--- |
| **[📦 Installer (.exe)](https://github.com/alimaandev/simpaudio/releases)** | ~392 MB | **Recommended.** Includes Start Menu shortcuts & auto-updates. |
| **[📁 Portable (.zip)](https://github.com/alimaandev/simpaudio/releases)** | ~567 MB | Run from USB or custom folder. No installation required. |

> **💡 Note on File Size:** The installer includes the complete AI runtime (Piper + Kokoro + Whisper). This ensures the app runs forever, offline, without needing future dependency updates.

### 🔐 First Launch Setup

Models are downloaded **on-demand** and cached locally. After the initial fetch, Simpaudio is fully air-gapped.

| Model | Size | Trigger |
| :--- | :--- | :--- |
| Piper Voices | ~60 MB ea. | First use of specific voice |
| Kokoro Engine | ~340 MB | First high-quality synthesis |
| Whisper STT | ~150 MB | First transcription task |

> **⚠️ Windows SmartScreen Notice**
> To keep Simpaudio free, we do not purchase expensive code-signing certificates. Windows may flag the installer. Please click **"More info" → "Run anyway"**. The app contains no telemetry and physically cannot phone home.

---

## 🚀 Quick Start Guide

1.  Install or unzip Simpaudio.
2.  Navigate to **Text to Speech** and select your preferred language/voice.
3.  Enter your text, choose an output path, and click **Generate Audio**.
4.  🎉 You’ve just created professional audio with zero recurring costs.

---

## 🏗️ Built on Giants

Simpaudio stands on the shoulders of incredible open-source projects:

| Component | Purpose | License |
| :--- | :--- | :--- |
| [Piper](https://github.com/rhasspy/piper) | Lightning-fast CPU TTS | MIT |
| [Kokoro](https://github.com/hexgrad/kokoro) | Neural voice engine & blending | Apache 2.0 |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | Offline speech recognition | MIT |
| [ttkbootstrap](https://github.com/israel-dryer/ttkbootstrap) | Modern UI framework | MIT |

---

## 🛠️ Developer Mode

Want to contribute or customize?

```bat
python -m venv venv
venv\Scripts\pip install -r requirements.txt
python app.py
```

### 💡 Why this matters
-   **`bat`**: Tells the Markdown renderer to use Batch/Windows Command Prompt syntax highlighting. This correctly colors `python`, `venv\Scripts\pip`, and file paths as shell commands.
-   **Avoids Misleading Highlighting**: If you leave it as `python`, the renderer tries to parse Windows paths like `venv\Scripts\pip` as Python syntax, which results in broken or confusing colors since backslashes and shell arguments aren't valid Python.
-   **Alternative**: You can also use ````powershell` if you want highlighting that matches modern Windows Terminal aesthetics, but `bat` is the most universally compatible for these specific commands across all Markdown renderers (GitHub, GitLab, VS Code, etc.).

---

## 💬 Community & Support

Found a bug or have an idea? We’d love to hear from you!

-   🐞 **[Report a Bug](https://github.com/alimaandev/simpaudio/issues/new?template=bug_report.yml)**
-   💡 **[Request a Feature](https://github.com/alimaandev/simpaudio/issues/new?template=feature_request.yml)**
-   📋 **[Browse All Issues](https://github.com/alimaandev/simpaudio/issues)**

> **Tip:** Always include your version (Installer/Portable/Source) and Windows build number when reporting issues. Screenshots help us resolve problems faster!

---

<p align="center">
  <b>📜 MIT License</b><br>
  Use it, fork it, ship it. Just keep the copyright line.<br>
  <i>If Simpaudio saves you time or money, consider leaving a ⭐ — it’s the best payment we accept.</i>
</p>

<p align="center">
  <sub>Simpaudio — Professional voice synthesis that lives on your PC, not on someone else's server.</sub>
</p>



