import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
from threading import Thread

import ttkbootstrap as ttk

from whisper_stt import WhisperSTT


class STTTab(ttk.Frame):
    def __init__(self, master, status_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.status_callback = status_callback
        self._audio_path: Path | None = None
        self._transcriber = WhisperSTT()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        self._build_ui()

    def _build_ui(self):
        self._create_input_section()
        self._create_separator(1)
        self._create_result_section()

    def _create_input_section(self):
        frame = ttk.LabelFrame(self, text="Input Audio", padding=(12, 8, 12, 8))
        frame.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 4))
        frame.columnconfigure(1, weight=1)

        ttk.Button(frame, text="Open Audio File", command=self._open_file).grid(
            row=0, column=0, padx=(0, 8), pady=4, sticky="w"
        )
        self.file_label = ttk.Label(frame, text="No file selected", foreground="#888888")
        self.file_label.grid(row=0, column=1, padx=(0, 8), pady=4, sticky="w")

        ttk.Label(frame, text="Model:").grid(row=1, column=0, padx=(0, 4), pady=4, sticky="w")
        self.model_var = tk.StringVar(value="base")
        ttk.Combobox(
            frame, textvariable=self.model_var,
            values=self._transcriber.list_models(),
            state="readonly", width=14,
        ).grid(row=1, column=1, padx=(0, 12), pady=4, sticky="w")

        ttk.Label(frame, text="Language:").grid(row=1, column=2, padx=(0, 4), pady=4, sticky="w")
        self.lang_var = tk.StringVar(value="Auto-detect")
        lang_options = ["Auto-detect", "en", "es", "fr", "de", "it", "pt", "ja", "zh"]
        ttk.Combobox(
            frame, textvariable=self.lang_var,
            values=lang_options, state="readonly", width=14,
        ).grid(row=1, column=3, padx=(0, 8), pady=4, sticky="w")

        self.transcribe_btn = ttk.Button(frame, text="Transcribe", command=self._transcribe)
        self.transcribe_btn.grid(row=1, column=4, padx=(0, 8), pady=4, sticky="e")

        self.trans_progress = ttk.Progressbar(frame, mode="indeterminate", length=200)

    def _create_separator(self, row: int):
        ttk.Separator(self, orient="horizontal").grid(row=row, column=0, sticky="ew", padx=12, pady=8)

    def _create_result_section(self):
        frame = ttk.LabelFrame(self, text="Transcription", padding=(12, 8, 12, 8))
        frame.grid(row=3, column=0, sticky="nsew", padx=12, pady=4)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        self.result_text = tk.Text(
            frame, wrap="word", font=("Segoe UI", 10),
            relief="flat", borderwidth=2, padx=8, pady=8,
            state="disabled",
        )
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        self.result_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        ttk.Button(btn_frame, text="Copy All", command=self._copy).pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text="Save as TXT", command=self._save_txt).pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text="Save as SRT", command=self._save_srt).pack(side="left")

    def _open_file(self):
        path = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[("Audio files", "*.wav *.mp3 *.m4a *.flac *.ogg"), ("All files", "*.*")],
        )
        if path:
            self._audio_path = Path(path)
            duration = "?"
            self.file_label.configure(text=f"{path} ({duration})", foreground="")
            self.result_text.configure(state="normal")
            self.result_text.delete("1.0", "end")
            self.result_text.configure(state="disabled")

    def _transcribe(self):
        if self._audio_path is None or not self._audio_path.exists():
            messagebox.showwarning("No File", "Please select an audio file first.")
            return

        lang = self.lang_var.get()
        if lang == "Auto-detect":
            lang = None

        model_name = self.model_var.get()
        self._transcriber = WhisperSTT(model_name)

        self.transcribe_btn.configure(state="disabled")
        self.trans_progress.grid(row=0, column=5, pady=4, padx=(0, 4))
        self.trans_progress.start(15)
        self.status_callback("Transcribing...")

        Thread(target=self._transcribe_thread, args=(lang,), daemon=True).start()

    def _transcribe_thread(self, language):
        try:
            result = self._transcriber.transcribe(self._audio_path, language, self.status_callback)
            segments = result["segments"]
            lines = []
            for seg in segments:
                m, s = divmod(int(seg.start), 60)
                h, m = divmod(m, 60)
                stamp = f"{h:02d}:{m:02d}:{s:02d}"
                lines.append(f"[{stamp}] {seg.text.strip()}")
            self._segments = segments
            self.after(0, lambda: self._display_result("\n".join(lines)))
        except Exception as e:
            self._segments = []
            self.after(0, lambda: self._error(str(e)))

    def _display_result(self, text: str):
        self.trans_progress.stop()
        self.trans_progress.grid_remove()
        self.transcribe_btn.configure(state="normal")
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", text)
        self.result_text.configure(state="disabled")
        self.status_callback("Transcription complete")

    def _error(self, msg: str):
        self.trans_progress.stop()
        self.trans_progress.grid_remove()
        self.transcribe_btn.configure(state="normal")
        self.status_callback("Error")
        messagebox.showerror("Transcription Error", f"Failed to transcribe:\n{msg}")

    def _copy(self):
        text = self.result_text.get("1.0", "end-1c")
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            self.status_callback("Copied to clipboard")

    def _save_txt(self):
        text = self.result_text.get("1.0", "end-1c")
        if not text:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile="transcript.txt",
        )
        if path:
            Path(path).write_text(text, encoding="utf-8")
            self.status_callback(f"Saved: {path}")

    def _save_srt(self):
        text = self.result_text.get("1.0", "end-1c")
        if not text:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".srt",
            filetypes=[("SRT files", "*.srt"), ("All files", "*.*")],
            initialfile="transcript.srt",
        )
        if path:
            lines = []
            segs = getattr(self, "_segments", None)
            if segs:
                from srt_exporter import export_srt
                export_srt([{"text": s.text.strip(), "start": s.start, "end": s.end} for s in segs], Path(path))
                self.status_callback(f"Saved: {path}")
                return
            for i, line in enumerate(text.split("\n"), 1):
                if line.strip():
                    stamp, _, content = line.partition(" ")
                    lines.append(str(i))
                    start = stamp.strip("[]")
                    lines.append(f"{start},000 --> {start},000")
                    lines.append(content)
                    lines.append("")
            Path(path).write_text("\n".join(lines), encoding="utf-8")
            self.status_callback(f"Saved: {path}")