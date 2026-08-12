import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Optional

import ttkbootstrap as ttk

from utils import LANGUAGES, OUTPUT_FORMATS, SORTED_LANGUAGES, Config
from srt_exporter import export_srt


class TTSTab(ttk.Frame):
    def __init__(self, master, config: Config, status_callback, engine=None, **kwargs):
        super().__init__(master, **kwargs)
        self.config = config
        self.status_callback = status_callback
        self.engine = engine
        self.save_path: Optional[Path] = None
        self._generated_wav: Optional[Path] = None

        self.columnconfigure(0, weight=1)
        self.rowconfigure(5, weight=1)

        self._build_ui()

    def _build_ui(self):
        self._create_variables()
        self._create_top_controls()
        self._create_speed_row()
        self._create_ssml_row()
        self._create_text_area()
        self._create_count_label()
        self._create_save_frame()
        self._create_action_row()

    def _create_variables(self):
        self.language_var = tk.StringVar(value=self.config.last_language)
        self.voice_var = tk.StringVar(value=self.config.last_voice)
        self.format_var = tk.StringVar(value="WAV")
        self.speed_var = tk.DoubleVar(value=self.config.speed)
        self.volume_var = tk.DoubleVar(value=self.config.volume)
        self.ssml_mode = tk.BooleanVar(value=False)
        self.export_srt = tk.BooleanVar(value=False)
        self.language_var.trace_add("write", self._on_language_changed)

    def _get_voices_for_language(self, language: str) -> list:
        if self.engine is None:
            return LANGUAGES.get(language, {}).get("piper", [])
        return self.engine.get_available_voices(language)

    def _on_language_changed(self, *_args):
        if self.engine is None:
            return
        voices = self.engine.get_available_voices(self.language_var.get())
        self.voice_menu["values"] = voices
        if self.voice_var.get() not in voices:
            self.voice_var.set(voices[0] if voices else "")

    def set_engine(self, engine):
        self.engine = engine
        if engine is None:
            self.voice_menu["values"] = []
            self.voice_var.set("")
            return
        voices = engine.get_available_voices(self.language_var.get())
        self.voice_menu["values"] = voices
        if voices:
            if self.config.last_voice in voices:
                self.voice_var.set(self.config.last_voice)
            else:
                self.voice_var.set(voices[0])
        else:
            self.voice_var.set("")

    def load_preset(self, preset: dict):
        if "voice" in preset:
            self.voice_var.set(preset["voice"])
        if "speed" in preset:
            self.speed_var.set(preset["speed"])
        if "volume" in preset:
            self.volume_var.set(preset["volume"])
        if "format" in preset:
            self.format_var.set(preset["format"])

    def _create_top_controls(self):
        frame = ttk.Frame(self, padding=(12, 8, 12, 2))
        frame.grid(row=0, column=0, sticky="ew")
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(3, weight=1)

        ttk.Label(frame, text="Language:").grid(row=0, column=0, padx=(0, 4), pady=2, sticky="w")
        ttk.Combobox(
            frame, textvariable=self.language_var,
            values=SORTED_LANGUAGES, state="readonly", width=16,
        ).grid(row=0, column=1, padx=(0, 12), pady=2, sticky="ew")

        ttk.Label(frame, text="Voice:").grid(row=0, column=2, padx=(0, 4), pady=2, sticky="w")
        self.voice_menu = ttk.Combobox(
            frame, textvariable=self.voice_var,
            values=self._get_voices_for_language(self.language_var.get()),
            state="readonly", width=26,
        )
        self.voice_menu.grid(row=0, column=3, padx=(0, 12), pady=2, sticky="ew")

        ttk.Label(frame, text="Format:").grid(row=0, column=4, padx=(0, 4), pady=2, sticky="w")
        ttk.Combobox(
            frame, textvariable=self.format_var,
            values=OUTPUT_FORMATS, state="readonly", width=8,
        ).grid(row=0, column=5, padx=(0, 8), pady=2, sticky="ew")

    def _create_speed_row(self):
        frame = ttk.Frame(self, padding=(12, 0, 12, 2))
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

    def _create_ssml_row(self):
        frame = ttk.Frame(self, padding=(12, 0, 12, 2))
        frame.grid(row=2, column=0, sticky="ew")

        ttk.Button(frame, text="\U0001f4c4 Import Text File", command=self._import_text).pack(
            side="left", padx=(0, 12)
        )

        self.ssml_btn = ttk.Button(frame, text="SSML Editor", command=self._open_ssml_editor)
        self.ssml_btn.pack(side="left", padx=(0, 12))

        ttk.Checkbutton(frame, text="SSML Mode", variable=self.ssml_mode).pack(side="left", padx=(0, 12))

    def _open_ssml_editor(self):
        try:
            from ui.ssml_editor import SSMLEditor
            text = self.text_widget.get("1.0", "end-1c")
            SSMLEditor(self, text, self._on_ssml_saved)
        except ImportError:
            messagebox.showinfo("Coming Soon", "Visual SSML editor will be available in the next update.")

    def _on_ssml_saved(self, text: str):
        self.text_widget.delete("1.0", "end")
        self.text_widget.insert("1.0", text)

    def _create_text_area(self):
        container = ttk.Frame(self, padding=(12, 2, 12, 2))
        container.grid(row=5, column=0, sticky="nsew")
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

    def _create_count_label(self):
        frame = ttk.Frame(self, padding=(12, 0, 12, 2))
        frame.grid(row=6, column=0, sticky="ew")
        self.count_var = tk.StringVar(value="Chars: 0  |  Words: 0")
        count_label = ttk.Label(frame, textvariable=self.count_var, font=("Segoe UI", 9))
        count_label.grid(row=0, column=0, sticky="w")
        self.text_widget.bind("<KeyRelease>", self._update_count)
        self.text_widget.bind("<<Paste>>", self._update_count)

    def _update_count(self, *_args):
        content = self.text_widget.get("1.0", "end-1c")
        chars = len(content)
        words = len(content.split()) if content.strip() else 0
        self.count_var.set(f"Chars: {chars}  |  Words: {words}")

    def _import_text(self):
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

    def _create_save_frame(self):
        frame = ttk.Frame(self, padding=(12, 2, 12, 2))
        frame.grid(row=7, column=0, sticky="ew")
        frame.columnconfigure(1, weight=1)

        self.save_btn = ttk.Button(frame, text="Choose Save Location", command=self.choose_save_location)
        self.save_btn.grid(row=0, column=0, padx=(0, 8), pady=2, sticky="w")
        self.save_path_label = ttk.Label(frame, text="No location selected", foreground="#888888")
        self.save_path_label.grid(row=0, column=1, padx=(0, 12), pady=2, sticky="w")

        ttk.Label(frame, text="Volume:").grid(row=0, column=2, padx=(0, 4), pady=2, sticky="w")
        volume_scale = ttk.Scale(
            frame, from_=0.0, to=2.0, variable=self.volume_var,
            orient="horizontal", length=100,
        )
        volume_scale.grid(row=0, column=3, padx=(0, 4), pady=2, sticky="ew")
        self.volume_label = ttk.Label(frame, text=f"{self.volume_var.get():.1f}x", width=5)
        self.volume_label.grid(row=0, column=4, pady=2, sticky="w")

        ttk.Checkbutton(frame, text="SRT", variable=self.export_srt).grid(
            row=0, column=5, padx=(12, 0), pady=2
        )

    def choose_save_location(self):
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

    def _create_action_row(self):
        frame = ttk.Frame(self, padding=(12, 2, 12, 4))
        frame.grid(row=8, column=0, sticky="ew")
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        self.preview_btn = ttk.Button(frame, text="\u25b6 Preview", command=self._preview_audio)
        self.preview_btn.grid(row=0, column=0, padx=(0, 6), pady=4, sticky="e")

        self.generate_btn = ttk.Button(frame, text="Generate Audio", command=self._on_generate_clicked)
        self.generate_btn.grid(row=0, column=1, padx=(6, 0), pady=4, sticky="w")

        self.progress_bar = ttk.Progressbar(frame, mode="indeterminate", length=200)

    def _update_status(self, message: str):
        self.status_callback(message)

    def _on_generate_clicked(self):
        text = self.text_widget.get("1.0", "end-1c").strip()
        if not text:
            messagebox.showwarning("No Text", "Please enter some text to convert to speech.")
            return
        if not self.save_path:
            messagebox.showwarning("No Location", "Please choose a save location first.")
            return
        voice = self.voice_var.get()
        if not voice:
            messagebox.showwarning("No Voice", "No voice available for this engine/language.")
            return

        self.generate_btn.configure(state="disabled")
        self.save_btn.configure(state="disabled")
        self.preview_btn.configure(state="disabled")
        self.progress_bar.grid(row=2, column=0, columnspan=2, pady=(0, 4))
        self.progress_bar.start(15)

        thread = threading.Thread(
            target=self._generate_thread, args=(text,), daemon=True,
        )
        thread.start()

    def _generate_thread(self, text: str):
        try:
            self._update_status("Generating audio...")
            output_path = self.save_path
            ext = output_path.suffix.lower()
            if ext not in (".wav", ".mp3"):
                output_path = output_path.with_suffix(".wav")

            use_ssml = self.ssml_mode.get()
            final_text = text
            if use_ssml:
                from ssml_parser import strip_ssml
                final_text = strip_ssml(text)

            result = self.engine.generate(
                text=final_text,
                voice=self.voice_var.get(),
                speed=self.speed_var.get(),
                volume=self.volume_var.get(),
                output_path=output_path,
                status_callback=self._update_status,
            )

            self._generated_wav = result if result.suffix == ".wav" else result

            if self.export_srt.get():
                segments = self.engine.get_last_segments()
                if segments:
                    srt_path = output_path.with_suffix(".srt")
                    export_srt(segments, srt_path)

            self.after(0, self._generation_finished)
        except Exception as exc:
            self.after(0, lambda e=exc: self._generation_error(str(e)))

    def _preview_audio(self):
        path = self._generated_wav
        if path is None or not path.exists():
            messagebox.showinfo("No Preview", "Generate audio first, then preview it.")
            return
        try:
            import winsound
            winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_ASYNC)
        except Exception as exc:
            messagebox.showerror("Playback Error", str(exc))

    def _generation_finished(self):
        self._reset_ui()
        self._update_status("Finished!")
        msg = f"Audio saved successfully!\n{self.save_path}"
        if self.export_srt.get():
            msg += "\nSRT subtitles exported."
        messagebox.showinfo("Success", msg)

    def _generation_error(self, msg: str):
        self._reset_ui()
        self._update_status("Error")
        messagebox.showerror("Generation Error", f"An error occurred:\n\n{msg}")

    def _reset_ui(self):
        self.progress_bar.stop()
        self.progress_bar.grid_remove()
        self.generate_btn.configure(state="normal")
        self.save_btn.configure(state="normal")
        self.preview_btn.configure(state="normal")

    def save_state(self):
        self.config.last_language = self.language_var.get()
        self.config.last_voice = self.voice_var.get()
        self.config.speed = self.speed_var.get()
        self.config.volume = self.volume_var.get()

    def load_state(self):
        self.language_var.set(self.config.last_language)
        voices = self._get_voices_for_language(self.config.last_language)
        if self.config.last_voice in voices:
            self.voice_var.set(self.config.last_voice)
        elif voices:
            self.voice_var.set(voices[0])