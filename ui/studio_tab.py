import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
from threading import Thread
from typing import List, Optional

import ttkbootstrap as ttk

from utils import Config, LANGUAGES, OUTPUT_FORMATS, SORTED_LANGUAGES


def _extract_chapters(file_path: Path) -> List[dict]:
    ext = file_path.suffix.lower()
    text = file_path.read_text(encoding="utf-8", errors="replace")

    if ext == ".md":
        return _split_markdown(text)
    elif ext == ".epub":
        return _split_epub(file_path)
    elif ext == ".pdf":
        return _split_pdf(file_path)
    else:
        return _split_plain(text)


def _split_plain(text: str) -> List[dict]:
    lines = text.split("\n")
    chapters = []
    current = {"title": "Untitled", "text": []}
    for line in lines:
        stripped = line.strip()
        if stripped and (stripped.isupper() and len(stripped) > 3) or stripped.startswith("Chapter"):
            if current["text"]:
                chapters.append(current)
            current = {"title": stripped, "text": []}
        else:
            current["text"].append(line)
    if current["text"]:
        chapters.append(current)
    if not chapters:
        chapters.append({"title": "Document", "text": lines})
    for ch in chapters:
        ch["text"] = "\n".join(ch["text"]).strip()
    return chapters


def _split_markdown(text: str) -> List[dict]:
    chapters = []
    current = {"title": "Introduction", "text": []}
    for line in text.split("\n"):
        if line.startswith("# "):
            if current["text"]:
                chapters.append(current)
            current = {"title": line.lstrip("# ").strip(), "text": []}
        else:
            current["text"].append(line)
    if current["text"]:
        chapters.append(current)
    for ch in chapters:
        ch["text"] = "\n".join(ch["text"]).strip()
    return chapters


def _split_epub(file_path: Path) -> List[dict]:
    try:
        import ebooklib
        from ebooklib import epub
        from bs4 import BeautifulSoup
    except ImportError:
        raise RuntimeError("Install: pip install ebooklib beautifulsoup4")
    book = epub.read_epub(str(file_path))
    chapters = []
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), "html.parser")
            title = soup.find("title")
            title_text = title.get_text(strip=True) if title else "Chapter"
            text = soup.get_text(strip=True)
            if text:
                chapters.append({"title": title_text, "text": text})
    if not chapters:
        chapters.append({"title": "Document", "text": ""})
    return chapters


def _split_pdf(file_path: Path) -> List[dict]:
    try:
        import pypdf
    except ImportError:
        raise RuntimeError("Install: pip install pypdf")
    reader = pypdf.PdfReader(str(file_path))
    chapters = []
    current = {"title": "Document", "text": []}
    for page in reader.pages:
        text = page.extract_text() or ""
        for line in text.split("\n"):
            stripped = line.strip()
            if stripped and stripped.isupper() and len(stripped) > 3:
                if current["text"]:
                    chapters.append(current)
                current = {"title": stripped, "text": []}
            else:
                current["text"].append(line)
    if current["text"]:
        chapters.append(current)
    for ch in chapters:
        ch["text"] = "\n".join(ch["text"]).strip()
    return chapters


class StudioTab(ttk.Frame):
    def __init__(self, master, config: Config, status_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.config = config
        self.status_callback = status_callback
        self.engine = None
        self._chapters: List[dict] = []
        self._source_path: Optional[Path] = None
        self._generating = False

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self._build_ui()

    def _build_ui(self):
        self._create_import_section()
        self._create_chapter_section()
        self._create_output_section()

    def _create_import_section(self):
        frame = ttk.LabelFrame(self, text="Import Manuscript", padding=(12, 8, 12, 8))
        frame.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 4))
        frame.columnconfigure(1, weight=1)

        self.import_btn = ttk.Button(frame, text="Import File", command=self._import_file)
        self.import_btn.grid(row=0, column=0, padx=(0, 8), pady=4, sticky="w")
        self.source_label = ttk.Label(frame, text="No file loaded", foreground="#888888")
        self.source_label.grid(row=0, column=1, padx=(0, 8), pady=4, sticky="w")

        ttk.Label(frame, text="Default Voice:").grid(row=1, column=0, padx=(0, 4), pady=4, sticky="w")
        self.default_voice = tk.StringVar()
        self.voice_menu = ttk.Combobox(frame, textvariable=self.default_voice, state="readonly", width=26)
        self.voice_menu.grid(row=1, column=1, padx=(0, 8), pady=4, sticky="w")

    def _create_chapter_section(self):
        frame = ttk.LabelFrame(self, text="Chapters", padding=(12, 8, 12, 8))
        frame.grid(row=2, column=0, sticky="nsew", padx=12, pady=4)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        columns = ("num", "title", "voice", "words")
        self.chapter_tree = ttk.Treeview(frame, columns=columns, show="headings", height=8)
        self.chapter_tree.heading("num", text="#")
        self.chapter_tree.heading("title", text="Chapter")
        self.chapter_tree.heading("voice", text="Voice")
        self.chapter_tree.heading("words", text="Words")
        self.chapter_tree.column("num", width=40)
        self.chapter_tree.column("title", width=300)
        self.chapter_tree.column("voice", width=180)
        self.chapter_tree.column("words", width=70)
        self.chapter_tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.chapter_tree.yview)
        self.chapter_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        ttk.Button(btn_frame, text="Assign Voice", command=self._assign_voice).pack(side="left", padx=(0, 8))

    def _create_output_section(self):
        frame = ttk.Frame(self, padding=(12, 4, 12, 12))
        frame.grid(row=3, column=0, sticky="ew")
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Output Folder:").grid(row=0, column=0, padx=(0, 4), pady=4, sticky="w")
        self.output_dir_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.output_dir_var, width=50).grid(
            row=0, column=1, padx=(0, 8), pady=4, sticky="ew"
        )
        ttk.Button(frame, text="Browse", command=self._browse_output).grid(row=0, column=2, pady=4)

        ttk.Label(frame, text="Format:").grid(row=1, column=0, padx=(0, 4), pady=4, sticky="w")
        self.fmt_var = tk.StringVar(value="WAV")
        ttk.Combobox(frame, textvariable=self.fmt_var, values=["WAV", "MP3"], state="readonly", width=8).grid(
            row=1, column=1, padx=(0, 8), pady=4, sticky="w"
        )

        self.srt_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="SRT per chapter", variable=self.srt_var).grid(
            row=1, column=2, padx=(0, 8), pady=4, sticky="w"
        )

        self.concat_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Concatenate", variable=self.concat_var).grid(
            row=1, column=3, padx=(0, 8), pady=4, sticky="w"
        )

        self.generate_btn = ttk.Button(frame, text="Generate Audiobook", command=self._generate)
        self.generate_btn.grid(row=2, column=0, pady=8, sticky="w")

        self.progress = ttk.Progressbar(frame, mode="determinate", length=400)
        self.progress.grid(row=2, column=1, columnspan=3, pady=8, sticky="ew")
        self.progress_label = ttk.Label(frame, text="")
        self.progress_label.grid(row=2, column=4, padx=(8, 0), pady=8)

    def set_engine(self, engine):
        self.engine = engine
        if engine and engine.name == "Kokoro TTS":
            self.voice_menu["values"] = engine.get_available_voices("English (US)")
        elif engine:
            self.voice_menu["values"] = engine.get_available_voices("English (US)")
        if self.voice_menu["values"]:
            self.default_voice.set(self.voice_menu["values"][0])

    def _import_file(self):
        path = filedialog.askopenfilename(
            title="Import Manuscript",
            filetypes=[
                ("All supported", "*.txt *.md *.epub *.pdf"),
                ("Text files", "*.txt"),
                ("Markdown", "*.md"),
                ("EPUB", "*.epub"),
                ("PDF", "*.pdf"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return
        self._source_path = Path(path)
        self.source_label.configure(text=str(path), foreground="")

        try:
            self._chapters = _extract_chapters(self._source_path)
        except Exception as e:
            messagebox.showerror("Import Error", str(e))
            return

        self._refresh_chapters()
        self.status_callback(f"Loaded {len(self._chapters)} chapters from {path}")

    def _refresh_chapters(self):
        for item in self.chapter_tree.get_children():
            self.chapter_tree.delete(item)
        for i, ch in enumerate(self._chapters, 1):
            voice = ch.get("voice") or self.default_voice.get() or ""
            words = len(ch["text"].split()) if ch["text"] else 0
            self.chapter_tree.insert(
                "", "end", iid=str(i),
                values=(i, ch["title"][:60], voice, words),
            )

    def _assign_voice(self):
        selected = self.chapter_tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Select a chapter to assign a voice.")
            return
        voice = self.default_voice.get()
        if not voice:
            return
        for item in selected:
            idx = int(self.chapter_tree.item(item, "values")[0]) - 1
            self._chapters[idx]["voice"] = voice
        self._refresh_chapters()

    def _browse_output(self):
        path = filedialog.askdirectory(title="Select Output Folder")
        if path:
            self.output_dir_var.set(path)

    def _generate(self):
        if not self._chapters:
            messagebox.showwarning("No Chapters", "Import a manuscript first.")
            return
        if self.engine is None:
            messagebox.showwarning("No Engine", "Select an engine from the toolbar first.")
            return
        output_dir = self.output_dir_var.get().strip()
        if not output_dir:
            messagebox.showwarning("No Output", "Select an output folder.")
            return

        self._generating = True
        self.generate_btn.configure(state="disabled")
        self.progress["maximum"] = len(self._chapters)
        self.progress["value"] = 0

        Thread(target=self._generate_thread, args=(Path(output_dir),), daemon=True).start()

    def _generate_thread(self, output_dir: Path):
        output_dir.mkdir(parents=True, exist_ok=True)
        ext = ".mp3" if self.fmt_var.get() == "MP3" else ".wav"
        total = len(self._chapters)
        audio_paths = []

        for i, ch in enumerate(self._chapters):
            if not self._generating:
                break

            text = ch["text"]
            if not text.strip():
                self.after(0, lambda idx=i: self._mark_done(idx, "empty"))
                self.after(0, lambda v=i+1: self.progress.configure(value=v))
                continue

            voice = ch.get("voice") or self.default_voice.get() or ""
            if not voice:
                self.after(0, lambda idx=i: self._mark_done(idx, "no voice"))
                continue

            out_path = output_dir / f"chapter_{i+1:03d}{ext}"
            try:
                self.after(0, lambda idx=i, title=ch["title"]: self.progress_label.configure(
                    text=f"Chapter {idx+1}: {title[:40]}"
                ))
                self.engine.generate(
                    text=text, voice=voice,
                    speed=1.0, volume=1.0,
                    output_path=out_path,
                    status_callback=self.status_callback,
                )
                audio_paths.append((ch["title"], out_path))

                if self.srt_var.get():
                    segs = self.engine.get_last_segments()
                    if segs:
                        from srt_exporter import export_srt
                        srt_path = out_path.with_suffix(".srt")
                        export_srt(segs, srt_path)

                self.after(0, lambda idx=i: self._mark_done(idx, "done"))
            except Exception as e:
                self.after(0, lambda idx=i, msg=str(e): self._mark_done(idx, f"error: {msg}"))

            self.after(0, lambda v=i+1: self.progress.configure(value=v))

        if self.concat_var.get() and len(audio_paths) > 1:
            self._concatenate_audio(audio_paths, output_dir, ext)

        self.after(0, self._generation_done)

    def _mark_done(self, idx: int, status: str):
        item = str(idx + 1)
        if self.chapter_tree.exists(item):
            vals = list(self.chapter_tree.item(item, "values"))
            vals[3] = status
            self.chapter_tree.item(item, values=vals)

    def _concatenate_audio(self, audio_paths: list, output_dir: Path, ext: str):
        if not audio_paths:
            return
        try:
            from pydub import AudioSegment
            combined = AudioSegment.empty()
            for _, path in audio_paths:
                if path.suffix.lower() == ".wav":
                    combined += AudioSegment.from_wav(str(path))
                else:
                    combined += AudioSegment.from_mp3(str(path))
            combined_path = output_dir / f"audiobook_full{ext}"
            combined.export(str(combined_path), format=ext.lstrip("."), bitrate="192k")
            self.status_callback(f"Concatenated: {combined_path.name}")
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Concat Error", str(e)))

    def _generation_done(self):
        self._generating = False
        self.generate_btn.configure(state="normal")
        self.progress_label.configure(text="Complete!")
        self.status_callback("Audiobook generation finished!")
        messagebox.showinfo("Complete", f"Generated {len(self._chapters)} chapters.\nOutput: {self.output_dir_var.get()}")