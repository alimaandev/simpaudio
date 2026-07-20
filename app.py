import json
import os
import threading
import tkinter as tk
import wave
import winsound
from pathlib import Path
from tkinter import ttk, filedialog, messagebox
from typing import Optional

from piper import PiperVoice, SynthesisConfig
from piper.download_voices import download_voice

HAS_PYDUB = True
try:
    from pydub import AudioSegment
except ImportError:
    HAS_PYDUB = False

SETTINGS_FILE = Path.home() / ".simpaudio_settings.json"
WINDOW_TITLE = "Offline Text to Speech"
WINDOW_SIZE = (800, 680)
VOICES_DIR = Path.home() / ".simpaudio_voices"

LANGUAGES = {
    "English (US)": [
        "en_US-lessac-medium",
        "en_US-amy-medium",
        "en_US-ryan-medium",
        "en_US-arnold-medium",
        "en_US-dave-medium",
        "en_US-kathleen-medium",
    ],
    "English (UK)": [
        "en_GB-alan-medium",
        "en_GB-semi-medium",
    ],
    "Spanish": [
        "es_ES-carlfm-x_low",
        "es_ES-davefx-medium",
        "es_ES-sharvard-medium",
    ],
    "French": [
        "fr_FR-siwis-medium",
        "fr_FR-siwis-low",
    ],
    "German": [
        "de_DE-eva-medium-x_low",
        "de_DE-karlsson-medium",
        "de_DE-thorsten-medium",
    ],
    "Italian": [
        "it_IT-paola-medium",
    ],
    "Portuguese (BR)": [
        "pt_BR-edresson-medium",
        "pt_BR-faber-medium",
    ],
    "Chinese": [
        "zh_CN-huayan-medium",
        "zh_CN-xiaoxuan-medium",
    ],
}

OUTPUT_FORMATS = ["WAV", "MP3"]

SORTED_LANGUAGES = sorted(LANGUAGES.keys())


def _voice_model_path(voice: str) -> Path:
    return VOICES_DIR / f"{voice}.onnx"


def _voice_config_path(voice: str) -> Path:
    return VOICES_DIR / f"{voice}.onnx.json"


def _ensure_voice_downloaded(voice: str) -> None:
    model_path = _voice_model_path(voice)
    if model_path.exists():
        return
    VOICES_DIR.mkdir(parents=True, exist_ok=True)
    download_voice(voice, VOICES_DIR)


class Config:
    def __init__(self) -> None:
        self.last_language: str = SORTED_LANGUAGES[0]
        self.last_voice: str = LANGUAGES[SORTED_LANGUAGES[0]][0]
        self.last_folder: str = str(Path.home() / "Desktop")
        self.theme: str = "light"
        self.speed: float = 1.0
        self.volume: float = 1.0
        self.sentence_silence: float = 0.3
        self.load()

    def load(self) -> None:
        try:
            data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
            self.last_language = data.get("last_language", self.last_language)
            self.last_voice = data.get("last_voice", self.last_voice)
            self.last_folder = data.get("last_folder", self.last_folder)
            self.theme = data.get("theme", self.theme)
            self.speed = data.get("speed", self.speed)
            self.volume = data.get("volume", self.volume)
            self.sentence_silence = data.get("sentence_silence", self.sentence_silence)
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def save(self) -> None:
        try:
            SETTINGS_FILE.write_text(
                json.dumps(
                    {
                        "last_language": self.last_language,
                        "last_voice": self.last_voice,
                        "last_folder": self.last_folder,
                        "theme": self.theme,
                        "speed": self.speed,
                        "volume": self.volume,
                        "sentence_silence": self.sentence_silence,
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
        except OSError:
            pass


class TTSApp:
    def __init__(self) -> None:
        self.config = Config()
        self.save_path: Optional[Path] = None
        self.voice: Optional[PiperVoice] = None
        self._generated_wav: Optional[Path] = None

        self.root = tk.Tk()
        self.root.title(WINDOW_TITLE)
        self.root.geometry(f"{WINDOW_SIZE[0]}x{WINDOW_SIZE[1]}")
        self.root.minsize(680, 500)
        try:
            ico = Path(__file__).parent / "icon.ico"
            if ico.exists():
                self.root.iconbitmap(str(ico))
        except Exception:
            pass

        style = ttk.Style(self.root)
        self.current_theme = self.config.theme
        self._apply_theme(style)

        self._create_variables()
        self.create_ui()
        self._bind_shortcuts()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _create_variables(self) -> None:
        self.language_var = tk.StringVar(value=self.config.last_language)
        voices = LANGUAGES.get(self.language_var.get(), LANGUAGES[SORTED_LANGUAGES[0]])
        if self.config.last_voice in voices:
            self.voice_var = tk.StringVar(value=self.config.last_voice)
        else:
            self.voice_var = tk.StringVar(value=voices[0])
        self.format_var = tk.StringVar(value=OUTPUT_FORMATS[0])
        self.speed_var = tk.DoubleVar(value=self.config.speed)
        self.volume_var = tk.DoubleVar(value=self.config.volume)
        self.silence_var = tk.DoubleVar(value=self.config.sentence_silence)
        self.language_var.trace_add("write", self._on_language_changed)
        self.voice_var.trace_add("write", lambda *_: setattr(self, "voice", None))

    def _on_language_changed(self, *_args: object) -> None:
        voices = LANGUAGES.get(self.language_var.get(), LANGUAGES[SORTED_LANGUAGES[0]])
        menu = self.voice_menu
        menu["values"] = voices
        current = self.voice_var.get()
        if current not in voices:
            self.voice_var.set(voices[0])
            self.voice = None

    def _load_voice(self, voice_name: str) -> PiperVoice:
        model_path = _voice_model_path(voice_name)
        config_path = _voice_config_path(voice_name)
        return PiperVoice.load(model_path, config_path)

    def _apply_theme(self, style: ttk.Style) -> None:
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        if self.current_theme == "dark":
            bg = "#1e1e1e"
            fg = "#d4d4d4"
            select_bg = "#264f78"
            select_fg = "#ffffff"
            entry_fg = "#d4d4d4"
            entry_bg = "#2d2d2d"
            button_bg = "#0e639c"
            button_fg = "#ffffff"
            disabled_fg = "#6a6a6a"
        else:
            bg = "#f5f5f5"
            fg = "#1a1a1a"
            select_bg = "#0078d7"
            select_fg = "#ffffff"
            entry_fg = "#1a1a1a"
            entry_bg = "#ffffff"
            button_bg = "#0078d8"
            button_fg = "#ffffff"
            disabled_fg = "#a0a0a0"

        self.root.configure(bg=bg)
        style.configure(".", background=bg, foreground=fg, fieldbackground=entry_bg)
        style.configure("TFrame", background=bg)
        style.configure("TLabel", background=bg, foreground=fg)
        style.configure("TButton", background=button_bg, foreground=button_fg, borderwidth=1, focusthickness=3)
        style.map("TButton", background=[("active", "#005a9e")])
        style.configure("TCombobox", fieldbackground=entry_bg, foreground=entry_fg, background=bg)
        style.configure("TEntry", fieldbackground=entry_bg, foreground=entry_fg)
        style.map("TEntry", fieldbackground=[("focus", entry_bg)])
        style.configure("Horizontal.TProgressbar", background=button_bg, troughcolor=entry_bg)
        style.configure("TStatusBar.TLabel", background=bg, foreground=disabled_fg)
        style.configure("TScale", background=bg, foreground=fg, troughcolor=entry_bg)

    def toggle_theme(self) -> None:
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self._apply_theme(ttk.Style(self.root))
        self.config.theme = self.current_theme

    def create_ui(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(3, weight=1)

        self._create_top_controls()
        self._create_speed_row()
        self._create_import_row()
        self._create_text_area()
        self._create_count_label()
        self._create_save_frame()
        self._create_action_row()
        self._create_status_bar()

    def _create_top_controls(self) -> None:
        frame = ttk.Frame(self.root, padding=(12, 8, 12, 2))
        frame.grid(row=0, column=0, sticky="ew")
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(3, weight=1)

        ttk.Label(frame, text="Language:").grid(row=0, column=0, padx=(0, 4), pady=2, sticky="w")
        lang_menu = ttk.Combobox(
            frame, textvariable=self.language_var,
            values=SORTED_LANGUAGES, state="readonly", width=16,
        )
        lang_menu.grid(row=0, column=1, padx=(0, 12), pady=2, sticky="ew")

        ttk.Label(frame, text="Voice:").grid(row=0, column=2, padx=(0, 4), pady=2, sticky="w")
        self.voice_menu = ttk.Combobox(
            frame, textvariable=self.voice_var,
            values=LANGUAGES.get(self.language_var.get(), LANGUAGES[SORTED_LANGUAGES[0]]),
            state="readonly", width=26,
        )
        self.voice_menu.grid(row=0, column=3, padx=(0, 12), pady=2, sticky="ew")

        ttk.Label(frame, text="Format:").grid(row=0, column=4, padx=(0, 4), pady=2, sticky="w")
        ttk.Combobox(
            frame, textvariable=self.format_var,
            values=OUTPUT_FORMATS, state="readonly", width=8,
        ).grid(row=0, column=5, padx=(0, 8), pady=2, sticky="ew")

        theme_btn = ttk.Button(frame, text="\u263d / \u263e", width=4, command=self.toggle_theme)
        theme_btn.grid(row=0, column=6, padx=(0, 0), pady=2, sticky="e")

    def _create_speed_row(self) -> None:
        frame = ttk.Frame(self.root, padding=(12, 0, 12, 2))
        frame.grid(row=1, column=0, sticky="ew")
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Speed:").grid(row=0, column=0, padx=(0, 6), pady=2, sticky="w")
        speed_scale = ttk.Scale(
            frame, from_=0.5, to=2.0, variable=self.speed_var,
            orient="horizontal", length=200,
        )
        speed_scale.grid(row=0, column=1, padx=(0, 8), pady=2, sticky="ew")
        self.speed_label = ttk.Label(frame, text=f"{self.speed_var.get():.1f}x", width=5)
        self.speed_label.grid(row=0, column=2, padx=(0, 0), pady=2, sticky="w")
        self.speed_var.trace_add("write", lambda *_: self.speed_label.configure(
            text=f"{self.speed_var.get():.1f}x"
        ))

    def _create_import_row(self) -> None:
        frame = ttk.Frame(self.root, padding=(12, 0, 12, 2))
        frame.grid(row=2, column=0, sticky="ew")
        ttk.Button(frame, text="\U0001f4c4 Import Text File", command=self._import_text).grid(
            row=0, column=0, sticky="w"
        )

    def _create_text_area(self) -> None:
        container = ttk.Frame(self.root, padding=(12, 2, 12, 2))
        container.grid(row=3, column=0, sticky="nsew")
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)

        text_frame = ttk.Frame(container, borderwidth=1, relief="solid")
        text_frame.grid(row=0, column=0, sticky="nsew")
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        self.text_widget = tk.Text(
            text_frame,
            wrap="word",
            font=("Segoe UI", 11),
            relief="flat",
            borderwidth=4,
            padx=8,
            pady=8,
            undo=True,
            maxundo=50,
        )
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=scrollbar.set)
        self.text_widget.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def _create_count_label(self) -> None:
        frame = ttk.Frame(self.root, padding=(12, 0, 12, 2))
        frame.grid(row=4, column=0, sticky="ew")
        self.count_var = tk.StringVar(value="Chars: 0  |  Words: 0")
        count_label = ttk.Label(frame, textvariable=self.count_var, font=("Segoe UI", 9))
        count_label.grid(row=0, column=0, sticky="w")
        self.text_widget.bind("<KeyRelease>", self._update_count)
        self.text_widget.bind("<<Paste>>", self._update_count)

    def _update_count(self, *_args: object) -> None:
        content = self.text_widget.get("1.0", "end-1c")
        chars = len(content)
        words = len(content.split()) if content.strip() else 0
        self.count_var.set(f"Chars: {chars}  |  Words: {words}")

    def _import_text(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Open Text File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not file_path:
            return
        try:
            text = Path(file_path).read_text(encoding="utf-8")
        except Exception as exc:
            messagebox.showerror("Import Error", f"Could not read file:\n{exc}")
            return
        self.text_widget.delete("1.0", "end")
        self.text_widget.insert("1.0", text)
        self._update_count()

    def _create_save_frame(self) -> None:
        frame = ttk.Frame(self.root, padding=(12, 2, 12, 2))
        frame.grid(row=5, column=0, sticky="ew")
        frame.columnconfigure(1, weight=1)

        self.save_btn = ttk.Button(frame, text="Choose Save Location", command=self.choose_save_location)
        self.save_btn.grid(row=0, column=0, padx=(0, 8), pady=2, sticky="w")
        self.save_path_label = ttk.Label(frame, text="No location selected", foreground="#888888")
        self.save_path_label.grid(row=0, column=1, padx=(0, 12), pady=2, sticky="w")

        ttk.Label(frame, text="Silence:").grid(row=0, column=2, padx=(0, 4), pady=2, sticky="w")
        silence_spin = ttk.Spinbox(
            frame, from_=0.0, to=2.0, increment=0.1,
            textvariable=self.silence_var, width=5,
        )
        silence_spin.grid(row=0, column=3, padx=(0, 8), pady=2, sticky="w")
        ttk.Label(frame, text="s").grid(row=0, column=4, padx=(0, 12), pady=2, sticky="w")

        ttk.Label(frame, text="Volume:").grid(row=0, column=5, padx=(0, 4), pady=2, sticky="w")
        volume_scale = ttk.Scale(
            frame, from_=0.0, to=2.0, variable=self.volume_var,
            orient="horizontal", length=100,
        )
        volume_scale.grid(row=0, column=6, padx=(0, 4), pady=2, sticky="ew")
        self.volume_label = ttk.Label(frame, text=f"{self.volume_var.get():.1f}x", width=5)
        self.volume_label.grid(row=0, column=7, pady=2, sticky="w")
        self.volume_var.trace_add("write", lambda *_: self.volume_label.configure(
            text=f"{self.volume_var.get():.1f}x"
        ))

    def _create_action_row(self) -> None:
        frame = ttk.Frame(self.root, padding=(12, 2, 12, 4))
        frame.grid(row=6, column=0, sticky="ew")
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        self.preview_btn = ttk.Button(frame, text="\u25b6 Preview", command=self._preview_audio)
        self.preview_btn.grid(row=0, column=0, padx=(0, 6), pady=4, sticky="e")

        self.generate_btn = ttk.Button(frame, text="Generate Audio", command=self._on_generate_clicked)
        self.generate_btn.grid(row=0, column=1, padx=(6, 0), pady=4, sticky="w")

        self.progress_bar = ttk.Progressbar(frame, mode="indeterminate", length=200)

    def _create_status_bar(self) -> None:
        frame = ttk.Frame(self.root, padding=(12, 2, 12, 6))
        frame.grid(row=7, column=0, sticky="ew")
        frame.columnconfigure(0, weight=1)

        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(
            frame, textvariable=self.status_var,
            style="TStatusBar.TLabel", font=("Segoe UI", 9),
        )
        self.status_label.grid(row=0, column=0, sticky="w")

    def _bind_shortcuts(self) -> None:
        self.root.bind("<Control-Return>", lambda e: self._on_generate_clicked())
        self.text_widget.bind("<Control-a>", self._select_all)
        self.text_widget.bind("<Control-A>", self._select_all)

    @staticmethod
    def _select_all(event: tk.Event) -> str:
        event.widget.tag_add("sel", "1.0", "end")
        return "break"

    def choose_save_location(self) -> None:
        ext = ".mp3" if self.format_var.get() == "MP3" else ".wav"
        default_name = f"narration{ext}"
        file_path = filedialog.asksaveasfilename(
            title="Save Audio As",
            defaultextension=ext,
            filetypes=[
                ("Audio files", "*.wav *.mp3"),
                ("WAV audio", "*.wav"),
                ("MP3 audio", "*.mp3"),
                ("All files", "*.*"),
            ],
            initialdir=self.config.last_folder,
            initialfile=default_name,
        )
        if file_path:
            self.save_path = Path(file_path)
            self.config.last_folder = str(self.save_path.parent)
            self.save_path_label.configure(text=str(self.save_path), foreground="")

    def update_status(self, message: str) -> None:
        self.status_var.set(message)
        self.root.update_idletasks()

    def _on_generate_clicked(self) -> None:
        text = self.text_widget.get("1.0", "end-1c").strip()
        if not text:
            messagebox.showwarning("No Text", "Please enter some text to convert to speech.")
            return
        if not self.save_path:
            messagebox.showwarning("No Location", "Please choose a save location first.")
            return

        self.generate_btn.configure(state="disabled")
        self.save_btn.configure(state="disabled")
        self.preview_btn.configure(state="disabled")
        self.progress_bar.grid(row=2, column=0, columnspan=2, pady=(0, 4))
        self.progress_bar.start(15)

        thread = threading.Thread(
            target=self._generate_audio_thread, args=(text,), daemon=True,
        )
        thread.start()

    def _generate_audio_thread(self, text: str) -> None:
        voice_name = self.voice_var.get()
        try:
            self.root.after(0, lambda: self.update_status("Downloading voice if needed..."))
            _ensure_voice_downloaded(voice_name)

            if self.voice is None:
                self.voice = self._load_voice(voice_name)

            syn_config = SynthesisConfig(
                length_scale=1.0 / max(0.1, self.speed_var.get()),
                volume=max(0.0, self.volume_var.get()),
            )

            self.root.after(0, lambda: self.update_status("Generating audio..."))

            chunks = list(self.voice.synthesize(text, syn_config=syn_config))
            if not chunks:
                raise RuntimeError("No audio was generated.")

            silence_samples = int(self.voice.config.sample_rate * self.silence_var.get())

            self.root.after(0, lambda: self.update_status("Saving..."))

            temp_wav = self.save_path.with_suffix(".wav")
            with wave.open(str(temp_wav), "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(self.voice.config.sample_rate)
                for chunk in chunks:
                    wav_file.writeframes(chunk.audio_int16_bytes)
                    if silence_samples > 0:
                        wav_file.writeframes(b"\x00" * silence_samples * 2)

            output_path = self.save_path
            ext = output_path.suffix.lower()
            if ext == ".wav":
                if str(temp_wav) != str(output_path):
                    os.replace(str(temp_wav), str(output_path))
            elif ext == ".mp3":
                self._convert_wav_to_mp3(temp_wav, output_path)

            self._generated_wav = temp_wav if ext == ".wav" else output_path
            self.root.after(0, self._generation_finished)

        except Exception as exc:
            self.root.after(0, lambda: self._generation_error(str(exc)))

    def _convert_wav_to_mp3(self, wav_path: Path, mp3_path: Path) -> None:
        if not HAS_PYDUB:
            raise RuntimeError("pydub is required for MP3 export. Install it with: pip install pydub")
        segment = AudioSegment.from_wav(str(wav_path))
        segment.export(str(mp3_path), format="mp3", bitrate="192k")
        if wav_path.exists():
            wav_path.unlink(missing_ok=True)

    def _preview_audio(self) -> None:
        path = self._generated_wav
        if path is None or not path.exists():
            messagebox.showinfo("No Preview", "Generate audio first, then preview it.")
            return
        try:
            winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_ASYNC)
        except Exception as exc:
            messagebox.showerror("Playback Error", str(exc))

    def _generation_finished(self) -> None:
        self._reset_ui()
        self.update_status("Finished!")
        messagebox.showinfo("Success", f"Audio saved successfully!\n{self.save_path}")

    def _generation_error(self, msg: str) -> None:
        self._reset_ui()
        self.update_status("Error")
        messagebox.showerror("Generation Error", f"An error occurred:\n\n{msg}")

    def _reset_ui(self) -> None:
        self.progress_bar.stop()
        self.progress_bar.grid_remove()
        self.generate_btn.configure(state="normal")
        self.save_btn.configure(state="normal")
        self.preview_btn.configure(state="normal")

    def _on_close(self) -> None:
        self.config.last_language = self.language_var.get()
        self.config.last_voice = self.voice_var.get()
        self.config.theme = self.current_theme
        self.config.speed = self.speed_var.get()
        self.config.volume = self.volume_var.get()
        self.config.sentence_silence = self.silence_var.get()
        self.config.save()
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    app = TTSApp()
    app.run()


if __name__ == "__main__":
    main()
