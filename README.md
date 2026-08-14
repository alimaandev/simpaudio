<p align="center">
  <img src="assets/logo.png" alt="Simpaudio Logo" width="96">
</p>

# 🎙️ Simpaudio — The Free, Offline Voice Studio That Kills Your ElevenLabs Bill

<p align="center">
https://github.com/user-attachments/assets/93810a63-4849-4a8b-8086-bdd72ba9fce9
</p>

> **$22/month. For reading text out loud.**

ElevenLabs gets you 30 minutes of voice a month for the price of a Netflix subscription — and *streams every word through their servers*. Simpaudio does the same job (and more) with **zero subscriptions, zero accounts, zero cloud, zero tracking** — completely free, forever, on your own PC.

**Don't rent your voice. Own it.**

---

## ⚡ What Is This?

A full studio-grade voice toolkit for Windows that runs **100% offline**:

| 🎙 Text to Speech | 🎤 Voice Blending | 📖 Audiobook Studio | 🎧 Transcription |
|---|---|---|---|
| 40+ voices, 8 languages | Mix voices → custom blend | Full audiobooks from manuscripts | Whisper-powered STT |
| WAV / MP3 / SRT | Like voice DNA mixing | Per-chapter voices + subtitles | TXT / SRT export |

## 💀 ElevenLabs vs Simpaudio

| | **ElevenLabs** 💸 | **Simpaudio** 💀 |
|---|---|---|
| Price | **$22/month** (30 min) | **$0.00** — forever |
| Internet | Required — your text goes to their cloud | **Offline. Nobody sees your text.** |
| Account | Required | None |
| Voice blending | Paywall | Free, unlimited |
| Subtitle export | Paywall | Free |
| Audiobook generation | Manual, painful | One click |
| Speech-to-text | Paywall | Free & offline |
| Your data | In their logs | On your disk |

## 🔥 Why People Love It

- **It's actually private** — your scripts, books, and voice notes never leave your machine. Great for writers, journalists, and anyone with NDAs.
- **It produces usable audiobooks** — import `.txt`, `.md`, `.epub`, or `.pdf`, assign a different voice per chapter, and get a combined audiobook + timed subtitles out the other side.
- **The voice blending is wild** — blend two voices into one and you get a completely unique voice nobody else has. Because *you* generated it.
- **It's MIT licensed** — not a "free tier". A gift. Fork it, sell it, whatever. Free forever means forever.

## 🖥 Requirements

- Windows 10 / 11 (64-bit)
- ~2 GB free disk
- 4 GB RAM recommended

## ⬇️ Download

**[⬇ Grab the latest release here](https://github.com/alimaandev/simpaudio/releases)**

| File | Best for |
|---|---|
| `Simpaudio_Setup_1.0.0.exe` (~392 MB) | **Recommended** — installer with Start Menu & Desktop shortcuts |
| `Simpaudio_Portable.zip` (~567 MB) | No-install — unzip anywhere, run `Simpaudio.exe` |

*Psst — the installer is chunky because it bundles the *entire* AI runtime (Piper + Kokoro + Whisper). That's the price of "runs forever, offline, no updates needed".*

### 🔒 First Launch (one-time, needs internet)

Voice models download on demand, then cache locally:

| Model | Size | When |
|---|---|---|
| Piper voices | ~60 MB each | First use of each voice |
| Kokoro model | ~340 MB | First Kokoro speech |
| Whisper model | ~150 MB | First transcription |

After that? **Fully offline. No phone-home. No telemetry. Ever.**

### ⚠️ SmartScreen Warning

The installer isn't code-signed (certificates cost hundreds a year — we'd rather keep the software free). Windows may say "Windows protected your PC": click **More info → Run anyway**. It's safe — the app literally cannot phone home, there's no cloud to phone.

## 🚀 60-Second Start

1. Install (or unzip) Simpaudio
2. Open **Text to Speech** → pick language + voice
3. Type → **Choose Save Location** → **Generate Audio**
4. Done. You just beat a $22/month subscription.

## 🧰 Built On Open Source (Nothing But)

| Component | Role | License |
|---|---|---|
| [Piper](https://github.com/rhasspy/piper) | Fast CPU TTS — 40+ voices | MIT |
| [Kokoro](https://github.com/hexgrad/kokoro) | High-quality neural voices + blending | Apache 2.0 |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | Offline speech recognition | MIT |
| [ttkbootstrap](https://github.com/israel-dryer/ttkbootstrap) | Modern themed UI | MIT |

## 🛠 Dev Mode (For the Curious)

```bat
python -m venv venv
venv\Scripts\pip install -r requirements.txt
python app.py
```

## 📜 License

[MIT](LICENSE). Use it, fork it, ship it — just keep the copyright line. Star it if it saves you $264/year — that's *our* only pricing plan. ⭐

---

*Simpaudio — because your text-to-speech should live on your PC, not on someone's server.*
