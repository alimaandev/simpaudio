import tkinter as tk

import ttkbootstrap as ttk

import numpy as np


class WaveformView(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(self, height=80, bg="#2d2d2d", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self._audio = None
        self._sample_rate = None

    def set_audio(self, audio: np.ndarray, sample_rate: int):
        self._audio = audio
        self._sample_rate = sample_rate
        self._draw()

    def clear(self):
        self._audio = None
        self._sample_rate = None
        self.canvas.delete("all")

    def _draw(self):
        self.canvas.delete("all")
        if self._audio is None or len(self._audio) == 0:
            return

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 10:
            w = 200
        if h < 10:
            h = 80

        audio = self._audio
        if audio.dtype in (np.float32, np.float64):
            audio = np.abs(audio)
        else:
            audio = np.abs(audio.astype(np.float32) / 32767.0)

        num_samples = len(audio)
        if num_samples == 0:
            return

        step = max(1, num_samples // w)
        peaks = audio[::step]
        if len(peaks) < 2:
            return

        mid = h / 2
        scale = (h / 2) * 0.9
        points = []
        for i, val in enumerate(peaks):
            x = i
            y = mid - val * scale
            points.append((x, y))

        coords = []
        for i, (x, y) in enumerate(points):
            coords.extend([x, y])

        fill = "#4fc3f7"
        self.canvas.create_line(coords, fill=fill, width=1, smooth=True)

        mirror = []
        for x, y in points:
            mirror.extend([x, mid + (mid - y)])
        self.canvas.create_line(mirror, fill=fill, width=1, smooth=True)

        self.canvas.create_line(0, mid, w, mid, fill="#555555", width=1)


class AudioPlayer(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.columnconfigure(2, weight=1)

        self.play_btn = ttk.Button(self, text="\u25b6", width=3, command=self._toggle_play)
        self.play_btn.grid(row=0, column=0, padx=(0, 4))

        self.stop_btn = ttk.Button(self, text="\u25a0", width=3, command=self._stop)
        self.stop_btn.grid(row=0, column=1, padx=(0, 8))

        self.progress = ttk.Scale(self, from_=0, to=100, orient="horizontal", command=self._seek)
        self.progress.grid(row=0, column=2, sticky="ew", padx=(0, 8))

        self.time_label = ttk.Label(self, text="0:00 / 0:00", width=12)
        self.time_label.grid(row=0, column=3)

        self._audio_path = None
        self._playing = False

    def set_audio(self, path: str):
        self._audio_path = path
        self.progress.set(0)
        self.time_label.configure(text="0:00 / 0:00")

    def _toggle_play(self):
        if self._playing:
            self._stop()
        else:
            self._play()

    def _play(self):
        if not self._audio_path:
            return
        try:
            import winsound
            winsound.PlaySound(self._audio_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
            self._playing = True
            self.play_btn.configure(text="\u23f8")
        except Exception:
            pass

    def _stop(self):
        try:
            import winsound
            winsound.PlaySound(None, winsound.SND_PURGE)
        except Exception:
            pass
        self._playing = False
        self.play_btn.configure(text="\u25b6")
        self.progress.set(0)

    def _seek(self, val):
        pass

    def clear(self):
        self._stop()
        self._audio_path = None
        self.progress.set(0)
        self.time_label.configure(text="0:00 / 0:00")