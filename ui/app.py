from pathlib import Path
from tkinter import messagebox, simpledialog
import ttkbootstrap as ttk

from engines import create_engine
from voice_presets import list_presets, get_preset, save_preset, delete_preset
from utils import Config, ENGINES, WINDOW_SIZE, WINDOW_TITLE
from ui.tts_tab import TTSTab
from ui.blending_tab import BlendingTab
from ui.studio_tab import StudioTab
from ui.stt_tab import STTTab


LIGHT_THEME = "nord-light"
DARK_THEME = "nord-dark"


class App:
    def __init__(self):
        self.config = Config()

        self.current_theme = DARK_THEME if self.config.theme == "dark" else LIGHT_THEME
        self.root = ttk.Window(title=WINDOW_TITLE, themename=self.current_theme, size=WINDOW_SIZE, minsize=(800, 600))

        try:
            ico = Path(__file__).parent.parent / "icon.ico"
            if ico.exists():
                self.root.iconbitmap(str(ico))
        except Exception:
            pass

        self.engine = None
        self.engine_name = self.config.last_engine
        self._notebook_created = False

        self._build_ui()
        self._bind_shortcuts()
        self._init_engine()
        self._refresh_preset_menu()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)
        self._create_toolbar()
        self._create_status_bar()

    def _create_notebook(self):
        if self._notebook_created:
            return
        self._notebook_created = True

        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=2, column=0, sticky="nsew", padx=8, pady=(4, 0))
        self.root.rowconfigure(2, weight=1)

        self.tts_tab = TTSTab(self.notebook, self.config, self.update_status, engine=self.engine)
        self.blending_tab = BlendingTab(self.notebook, self.update_status)
        self.studio_tab = StudioTab(self.notebook, self.config, self.update_status)
        self.stt_tab = STTTab(self.notebook, self.update_status)

        self.notebook.add(self.tts_tab, text="  \U0001f399 Text to Speech  ")
        self.notebook.add(self.blending_tab, text="  \U0001f3a4 Voice Blending  ")
        self.notebook.add(self.studio_tab, text="  \U0001f4d6 Studio  ")
        self.notebook.add(self.stt_tab, text="  \U0001f3a7 Transcribe  ")

        self.blending_tab.set_engine(self.engine)
        self.studio_tab.set_engine(self.engine)

    def _create_toolbar(self):
        frame = ttk.Frame(self.root, padding=(12, 8, 12, 4))
        frame.grid(row=0, column=0, sticky="ew")
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Engine:").grid(row=0, column=0, padx=(0, 4), pady=2, sticky="w")
        self.engine_var = ttk.StringVar(value=self.engine_name)
        engine_menu = ttk.Combobox(
            frame, textvariable=self.engine_var,
            values=ENGINES, state="readonly", width=20,
        )
        engine_menu.grid(row=0, column=1, padx=(0, 12), pady=2, sticky="w")
        self.engine_var.trace_add("write", self._on_engine_changed)

        ttk.Label(frame, text="Preset:").grid(row=0, column=2, padx=(0, 4), pady=2, sticky="w")
        self.preset_var = ttk.StringVar()
        self.preset_menu = ttk.Combobox(
            frame, textvariable=self.preset_var,
            state="readonly", width=16,
        )
        self.preset_menu.grid(row=0, column=3, padx=(0, 4), pady=2, sticky="w")
        self.preset_var.trace_add("write", self._on_preset_selected)

        ttk.Button(frame, text="Save", width=5, command=self._save_preset).grid(
            row=0, column=4, padx=(0, 4), pady=2
        )
        ttk.Button(frame, text="Delete", width=5, command=self._delete_preset).grid(
            row=0, column=5, padx=(0, 12), pady=2
        )

        theme_btn = ttk.Button(frame, text="Toggle Theme", width=12, command=self.toggle_theme, bootstyle="secondary-outline")
        theme_btn.grid(row=0, column=6, padx=(0, 0), pady=2, sticky="e")

    def _create_status_bar(self):
        frame = ttk.Frame(self.root, padding=(12, 4, 12, 6))
        frame.grid(row=3, column=0, sticky="ew")
        frame.columnconfigure(0, weight=1)

        self.status_var = ttk.StringVar(value="Ready")
        self.status_label = ttk.Label(
            frame, textvariable=self.status_var, font=("Segoe UI", 9),
        )
        self.status_label.grid(row=0, column=0, sticky="w")

    def update_status(self, message: str):
        self.status_var.set(message)
        self.root.update_idletasks()

    def _on_engine_changed(self, *_args):
        self.engine_name = self.engine_var.get()
        if self.engine:
            self.engine.unload()
        self._init_engine()

    def _init_engine(self):
        try:
            self.engine = create_engine(self.engine_name)
            self.engine.load()
            self._create_notebook()
            self._set_engine_on_tabs()
            self.update_status(f"Engine: {self.engine_name}")
        except Exception as e:
            self._create_notebook()
            self.update_status(f"Error loading engine: {e}")

    def _set_engine_on_tabs(self):
        if self.engine:
            self.tts_tab.set_engine(self.engine)
            self.blending_tab.set_engine(self.engine)
            self.studio_tab.set_engine(self.engine)

    def _refresh_preset_menu(self):
        presets = list_presets()
        self.preset_menu["values"] = presets

    def _on_preset_selected(self, *_args):
        name = self.preset_var.get()
        if not name:
            return
        preset = get_preset(name)
        if preset is None:
            return
        if preset.get("engine") in ENGINES:
            self.engine_var.set(preset["engine"])
        self.tts_tab.load_preset(preset)

    def _save_preset(self):
        name = self.preset_var.get().strip()
        if not name:
            name = simpledialog.askstring("Save Preset", "Preset name:", parent=self.root)
            if not name:
                return
        engine = self.engine_var.get()
        voice = self.tts_tab.voice_var.get()
        speed = self.tts_tab.speed_var.get()
        volume = self.tts_tab.volume_var.get()
        fmt = self.tts_tab.format_var.get()
        save_preset(name, engine, voice, speed, volume, fmt)
        self._refresh_preset_menu()
        self.preset_var.set(name)
        self.update_status(f"Preset saved: {name}")

    def _delete_preset(self):
        name = self.preset_var.get()
        if not name:
            return
        if messagebox.askyesno("Delete Preset", f"Delete preset '{name}'?"):
            delete_preset(name)
            self._refresh_preset_menu()
            self.preset_var.set("")
            self.update_status(f"Preset deleted: {name}")

    def _bind_shortcuts(self):
        self.root.bind("<Control-Return>", lambda e: self.tts_tab._on_generate_clicked())

    def toggle_theme(self):
        self.current_theme = LIGHT_THEME if self.current_theme == DARK_THEME else DARK_THEME
        self.root.style.theme_use(self.current_theme)
        self.config.theme = "dark" if self.current_theme == DARK_THEME else "light"

    def _on_close(self):
        self.config.theme = "dark" if self.current_theme == DARK_THEME else "light"
        self.config.last_engine = self.engine_name
        if hasattr(self, 'tts_tab'):
            self.tts_tab.save_state()
        self.config.save()
        self.root.destroy()

    def run(self):
        self.root.mainloop()