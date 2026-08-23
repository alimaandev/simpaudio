import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

import ttkbootstrap as ttk

from utils import LANGUAGES, SORTED_LANGUAGES
from voice_presets import save_preset, list_presets

from ui.i18n import t


class BlendingTab(ttk.Frame):
    def __init__(self, master, status_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.status_callback = status_callback
        self.engine = None
        self._blend: list[str] = []

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self._build_ui()

    def _build_ui(self):
        self._create_pick_section()
        self._create_blend_section()
        self._create_save_section()

    def _create_pick_section(self):
        frame = ttk.LabelFrame(self, text=t("add_voices"), padding=(12, 8, 12, 8))
        frame.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 4))
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(3, weight=1)

        ttk.Label(frame, text=t("language")).grid(row=0, column=0, padx=(0, 4), pady=4, sticky="w")
        self.lang_var = tk.StringVar(value=SORTED_LANGUAGES[0])
        ttk.Combobox(
            frame, textvariable=self.lang_var,
            values=SORTED_LANGUAGES, state="readonly", width=18,
        ).grid(row=0, column=1, padx=(0, 12), pady=4, sticky="w")
        self.lang_var.trace_add("write", self._on_lang_changed)

        ttk.Label(frame, text=t("voice")).grid(row=0, column=2, padx=(0, 4), pady=4, sticky="w")
        self.voice_var = tk.StringVar()
        self.voice_menu = ttk.Combobox(
            frame, textvariable=self.voice_var,
            state="readonly", width=22,
        )
        self.voice_menu.grid(row=0, column=3, padx=(0, 8), pady=4, sticky="w")

        ttk.Button(frame, text=t("add_to_blend"), command=self._add_to_blend).grid(row=0, column=4, pady=4, sticky="e")

    def _create_blend_section(self):
        frame = ttk.LabelFrame(self, text=t("current_blend"), padding=(12, 8, 12, 8))
        frame.grid(row=2, column=0, sticky="nsew", padx=12, pady=4)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        columns = ("voice",)
        self.blend_tree = ttk.Treeview(frame, columns=columns, show="headings", height=6)
        self.blend_tree.heading("voice", text=t("voices_in_blend"))
        self.blend_tree.column("voice", width=350)
        self.blend_tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.blend_tree.yview)
        self.blend_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        ttk.Button(btn_frame, text=t("remove_selected"), command=self._remove_selected).pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text=t("clear_all"), command=self._clear_blend).pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text=t("test_play"), command=self._test_blend).pack(side="left")

    def _create_save_section(self):
        frame = ttk.Frame(self, padding=(12, 4, 12, 12))
        frame.grid(row=3, column=0, sticky="ew")
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text=t("preset_name")).grid(row=0, column=0, padx=(0, 4), pady=4, sticky="w")
        self.preset_name = tk.StringVar()
        ttk.Entry(frame, textvariable=self.preset_name, width=30).grid(row=0, column=1, padx=(0, 8), pady=4, sticky="w")
        ttk.Button(frame, text=t("save_blend_as_preset"), command=self._save_blend_preset).grid(row=0, column=2, pady=4, sticky="w")

    def set_engine(self, engine):
        self.engine = engine
        self._on_lang_changed()

    def _on_lang_changed(self, *_args):
        if self.engine is None:
            self.voice_menu["values"] = []
            return
        voices = self.engine.get_available_voices(self.lang_var.get())
        self.voice_menu["values"] = voices
        if voices:
            self.voice_var.set(voices[0])

    def _add_to_blend(self):
        voice = self.voice_var.get()
        if not voice or voice in self._blend:
            return
        self._blend.append(voice)
        self.blend_tree.insert("", "end", values=(voice,))
        self.status_callback(t("added_voice_status", voice=voice))

    def _remove_selected(self):
        selected = self.blend_tree.selection()
        for item in selected:
            vals = self.blend_tree.item(item, "values")
            if vals and vals[0] in self._blend:
                self._blend.remove(vals[0])
            self.blend_tree.delete(item)

    def _clear_blend(self):
        self._blend.clear()
        for item in self.blend_tree.get_children():
            self.blend_tree.delete(item)

    def _test_blend(self):
        if not self._blend:
            messagebox.showinfo(t("no_blend_title"), t("no_blend_msg"))
            return
        if self.engine is None:
            messagebox.showwarning(t("no_engine_title"), t("no_engine_msg"))
            return
        voice_str = ",".join(self._blend)
        save_path = filedialog.asksaveasfilename(
            title=t("save_blend_test_title"),
            defaultextension=".wav",
            filetypes=[("WAV audio", "*.wav"), ("MP3 audio", "*.mp3"), ("All files", "*.*")],
            initialfile="blend_preview.wav",
        )
        if not save_path:
            return

        self.status_callback(t("generating_blend_status", voices=voice_str))
        for item in self.blend_tree.get_children():
            self.blend_tree.item(item, values=(self.blend_tree.item(item, "values")[0], "generating"))
        threading.Thread(
            target=self._generate_blend, args=(voice_str, Path(save_path)), daemon=True,
        ).start()

    def _generate_blend(self, voice_str: str, save_path: Path):
        try:
            text = "This is a preview of the blended voice."
            result = self.engine.generate(
                text=text, voice=voice_str,
                speed=1.0, volume=1.0,
                output_path=save_path,
                status_callback=self.status_callback,
            )
            self.after(0, lambda: self._blend_done(True, result))
        except Exception as exc:
            self.after(0, lambda: self._blend_done(False, str(exc)))

    def _blend_done(self, ok: bool, result):
        for item in self.blend_tree.get_children():
            vals = self.blend_tree.item(item, "values")
            if len(vals) > 1 and vals[1] == "generating":
                self.blend_tree.item(item, values=(vals[0],))
        if not ok:
            messagebox.showerror(t("blend_error_title"), t("blend_error_msg", error=result))
            return
        try:
            import winsound
            winsound.PlaySound(str(result), winsound.SND_FILENAME | winsound.SND_ASYNC)
        except Exception:
            pass
        self.status_callback(t("blend_saved_status", path=result))
        messagebox.showinfo(t("blend_ready_title"), t("blend_ready_msg", path=result))

    def _save_blend_preset(self):
        name = self.preset_name.get().strip()
        if not name:
            messagebox.showwarning(t("no_name_title"), t("no_name_msg"))
            return
        if not self._blend:
            messagebox.showwarning(t("no_blend_title"), t("no_blend_msg"))
            return
        voice_str = ",".join(self._blend)
        save_preset(name, "Kokoro TTS", voice_str, 1.0, 1.0, "WAV")
        self.status_callback(t("preset_saved", name=name))
        messagebox.showinfo(t("preset_saved_title"), t("preset_saved_msg", name=name))