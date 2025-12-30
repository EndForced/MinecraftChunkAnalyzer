from .interfaces.IWidgets import IConsoleWidget, IPathWidget, IDimensionSelector
import ttkbootstrap as ttk
import tkinter as tk
from tkinter.filedialog import FileDialog
from datetime import datetime
import os
from pathlib import Path
from .utils import EventBus
from .models.events import Event, PathChanged
from ..infrastructure.fs.services import PathInfo
from typing import List

class ConsoleWidget(ttk.Labelframe, IConsoleWidget):
    def __init__(self, parent, title="Info", max_lines=15, **kwargs):
        super().__init__(parent, text=title, **kwargs)
        self.height = 400
        self.width = 200
        self.text_widget = None
        self.max_lines = max_lines
        self.size = (400,200)
        self.setup_ui()


    def setup_ui(self):
        self.text_widget = tk.Text(
            self,
            height=80,
            width=60,
            wrap=tk.WORD,
            bg='#1E1E1E',
            font=('Consolas', 9),
            state=tk.DISABLED,
            relief=tk.FLAT
        )

        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=scrollbar.set)

        self.text_widget.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        scrollbar.grid(row=0, column=1, sticky='n', pady=5)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.text_widget.tag_configure("info", foreground="#CCCCCC")
        self.text_widget.tag_configure("success", foreground="#4EC9B0")
        self.text_widget.tag_configure("warning", foreground="#FFC66D")
        self.text_widget.tag_configure("error", foreground="#F44747")

    def log(self, message: str, level="info") -> None:
        if type(message) != str:
            try:
                message = str(message)
            except:
                message = ""

        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"

        self.text_widget.config(state=tk.NORMAL)

        self.text_widget.insert(tk.END, formatted_message, level)
        self.text_widget.see(tk.END)

        lines = int(self.text_widget.index('end-1c').split('.')[0])
        if lines > self.max_lines:
            self.text_widget.delete(1.0, 2.0)

        self.text_widget.config(state=tk.DISABLED)

    def clear(self):
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.config(state=tk.DISABLED)

class PathWidget(ttk.Frame, IPathWidget):
    def __init__(self, parent, bus: EventBus, name: str = "Current path"):
        super().__init__(parent)
        self.root = parent
        self.name = name
        self._setup_ui()
        self.bus = bus

    def _setup_ui(self):
        _path_label = ttk.Label(self, text="Current path:", font=("Arial", 10, "bold"))
        _path_label.grid(row=1, column=0, sticky="w", pady=(16, 0), padx=(20, 0))

        self._current_path_value = ttk.Label(self, text="Not selected yet")
        self._current_path_value.grid(row=1, column=1, sticky="w", pady=(16, 0), padx=(10, 0))

        self._select_btn = ttk.Button(self, command = lambda: (self._browse_directory(), self.focus()), text = "Select path")
        self._select_btn.grid(row = 2, column = 0, padx = (20,10), pady = (10,10))

    def _browse_directory(self):
        appdata_path = os.path.expanduser('~\\AppData\\Roaming')
        minecraft_path = tk.filedialog.askdirectory(initialdir=appdata_path,
                                                         title="Select .minecraft directory")
        self._current_path_value.config(text = minecraft_path if minecraft_path else "Not selected yet")
        path = Path(minecraft_path)
        self.bus.emit(Event.PATH_CHANGED, PathChanged(path))

class DimensionSelector(ttk.Frame, IDimensionSelector):
    def __init__(self, root, bus: EventBus):
        super().__init__(root)
        self._combos:List[ttk.Combobox] = []
        self._setup_ui()
        self._bus = bus
        self._bus.subscribe(Event.PATH_CHANGED, self._refresh)
        self._path_info = PathInfo(Path())
        self._dims = ["End","Nether","Over"]

        self._setup_ui()


    def _refresh(self, path):
        for c in self._combos:
            c.destroy()
        self._path_info.change_path(path)
        self._combos: List[ttk.Combobox] = []
        self._setup_ui()
        self._combos[0].config(state = "readonly")
        self._combos[0].config(values = list((*self._path_info.get_data.worlds.keys(),*self._path_info.get_data.bobby_words.keys())))

    def _on_select(self, id_combo):
        if id_combo == 0:
            if len(self._combos) == 3:
                self._combos[2].destroy()
            self._combos = self._combos[:1]

            self._add_combo()
            if self._combos[0].get().endswith("(server)"):
                self._combos[1].config(values = list(self._path_info.get_data.bobby_words[self._combos[0].get()]))
                self._combos[1].set("Select bobby subworld!")
                self._bind(self._combos[1], lambda x :self._on_select(1))
            else:
                self._combos[1].config(values = self._dims)
                self._combos[1].set("Select dimension!")
            self._combos[1].grid(row = 0, column = 1)

        elif id_combo == 1:
            if self._combos[0].get().endswith("(server)"):
                self._add_combo()
                self._combos[2].set("Select dimension!")
                self._combos[2].config(values = self._dims)
            else:
                pass
                #event bus emitting
            self._combos[2].grid(row=0, column=2,padx = 50)

    def _add_combo(self):
        combo = ttk.Combobox(self, state = "readonly")
        self._combos.append(combo)

    @staticmethod
    def _bind(combo: ttk.Combobox, func: callable):
        combo.bind("<<ComboboxSelected>>", func)

    def _setup_ui(self):
        self._combos.append(ttk.Combobox(self, values=["Your worlds"]))
        self._combos[0].set("World selection")
        self._combos[0].config(state = "disabled")
        self._bind(self._combos[0],lambda x: self._on_select(0))
        self._combos[0].grid(row = 0, column = 0 , padx =  (0,50))






