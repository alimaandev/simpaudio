# Changelog

All notable changes to Simpaudio are documented here.

## [1.0.0] - 2026-08-15

Initial release. First published as a single release: **Simpaudio v1.0.0** (installer + portable zip, same version tag, binaries replaced on 2026-08-15 after the packaged app was fixed).

### Added
- Piper TTS engine (40+ voices, 8 languages, voice downloader built in)
- Kokoro TTS engine (8 languages: English, Spanish, French, Hindi, Italian, Japanese, Portuguese, Mandarin)
- Voice blending — combine any two voices ("af_heart,af_bella") with silent fallback to a single voice
- Whisper speech-to-text (tiny/base/small/medium) with WAV/MP3 support
- Audiobook mode with chapter detection and per-chapter export (WAV/MP3)
- SSML visual editor with live SSML preview
- SRT subtitle export with real segment timestamps
- Text-file and EPUB/PDF import
- Built-in self-test (`Simpaudio.exe --selftest`) to verify all engines

### Fixed (packaged build, binaries replaced 2026-08-15)
- Kokoro TTS no longer fails with "No audio was generated" — the model is now passed to the pipeline correctly
- Piper/Kokoro/Whisper voice and model data is now bundled into the app (previously missing from the frozen build, so engines silently failed)
- Kokoro now handles names and unknown words in all languages via a bundled espeak-ng phonemizer (previously crashed on out-of-vocabulary words)
- Voice blending now actually generates blended audio in the packaged app
- "Test Play" in the Blending tab now really plays audio instead of showing a placeholder message
- MP3 preview and MP3 export work in the packaged app (ffmpeg bundled)
- Output format choice is remembered between sessions
- SRT export uses real word timestamps instead of zero-duration entries
- Fixed a potential UI crash from status updates arriving from background threads
- Installer size reduced from ~392 MB to ~285 MB by excluding unused optional packages

## [Unreleased]

- Nothing yet.
