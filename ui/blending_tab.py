import tkinter as tk
from tkinter import messagebox

import ttkbootstrap as ttk

from utils import LANGUAGES, SORTED_LANGUAGES
from voice_presets import save_preset, list_presets


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
        frame = ttk.LabelFrame(self, text="Add Voices", padding=(12, 8, 12, 8))
        frame.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 4))
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(3, weight=1)

        ttk.Label(frame, text="Language:").grid(row=0, column=0, padx=(0, 4), pady=4, sticky="w")
        self.lang_var = tk.StringVar(value=SORTED_LANGUAGES[0])
        ttk.Combobox(
            frame, textvariable=self.lang_var,
            values=SORTED_LANGUAGES, state="readonly", width=18,
        ).grid(row=0, column=1, padx=(0, 12), pady=4, sticky="w")
        self.lang_var.trace_add("write", self._on_lang_changed)

        ttk.Label(frame, text="Voice:").grid(row=0, column=2, padx=(0, 4), pady=4, sticky="w")
        self.voice_var = tk.StringVar()
        self.voice_menu = ttk.Combobox(
            frame, textvariable=self.voice_var,
            state="readonly", width=22,
        )
        self.voice_menu.grid(row=0, column=3, padx=(0, 8), pady=4, sticky="w")

        ttk.Button(frame, text="Add to Blend", command=self._add_to_blend).grid(
            row=0, column=4, pady=4, sticky="e"
        )

    def _create_blend_section(self):
        frame = ttk.LabelFrame(self, text="Current Blend", padding=(12, 8, 12, 8))
        frame.grid(row=2, column=0, sticky="nsew", padx=12, pady=4)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        columns = ("voice",)
        self.blend_tree = ttk.Treeview(frame, columns=columns, show="headings", height=6)
        self.blend_tree.heading("voice", text="Voices in blend")
        self.blend_tree.column("voice", width=350)
        self.blend_tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.blend_tree.yview)
        self.blend_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        ttk.Button(btn_frame, text="Remove Selected", command=self._remove_selected).pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text="Clear All", command=self._clear_blend).pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text="Test Play", command=self._test_blend).pack(side="left")

    def _create_save_section(self):
        frame = ttk.Frame(self, padding=(12, 4, 12, 12))
        frame.grid(row=3, column=0, sticky="ew")
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Preset Name:").grid(row=0, column=0, padx=(0, 4), pady=4, sticky="w")
        self.preset_name = tk.StringVar()
        ttk.Entry(frame, textvariable=self.preset_name, width=30).grid(
            row=0, column=1, padx=(0, 8), pady=4, sticky="w"
        )
        ttk.Button(frame, text="Save Blend as Preset", command=self._save_blend_preset).grid(
            row=0, column=2, pady=4, sticky="w"
        )

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
        self.status_callback(f"Added: {voice}")

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
            messagebox.showinfo("No Blend", "Add at least one voice to the blend first.")
            return
        voice_str = ",".join(self._blend)
        self.status_callback(f"Blend string: {voice_str}")
        messagebox.showinfo(
            "Blend Ready",
            f"Use this voice string in the TTS tab:\n\n{voice_str}\n\n"
            f"Kokoro will average these voice packs.",
        )

    def _save_blend_preset(self):
        name = self.preset_name.get().strip()
        if not name:
            messagebox.showwarning("No Name", "Enter a name for the preset.")
            return
        if not self._blend:
            messagebox.showwarning("No Blend", "Add at least one voice to the blend first.")
            return
        voice_str = ",".join(self._blend)
        save_preset(name, "Kokoro TTS", voice_str, 1.0, 1.0, "WAV")
        self.status_callback(f"Blend saved: {name}")
        messagebox.showinfo("Saved", f"Blend preset '{name}' saved!\nUse it from the Preset menu.")