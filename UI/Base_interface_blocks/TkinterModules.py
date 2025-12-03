import tkinter as tk
from ast import copy_location

import ttkbootstrap as ttk
from datetime import datetime
from typing import Any, Callable, List, Optional, Union

class ColoredConsoleLabelFrame(ttk.Labelframe):
    def __init__(self, parent, title="Info", max_lines=15, **kwargs):
        super().__init__(parent, text=title, **kwargs)
        self.max_lines = max_lines
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
        scrollbar.grid(row=0, column=1, sticky='ns', pady=5)

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
            self.text_widget.delete(1.0, 2.0)  # Удаляем первую строку

        self.text_widget.config(state=tk.DISABLED)

    def clear(self):
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.config(state=tk.DISABLED)

class ChunkSelectionFrame(ttk.Labelframe):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.setup_ui()

    def setup_ui(self):
        description_label = ttk.Label(
            self,
            text="Select the area for chunk loading (coordinates):",
            font=('Arial', 9)
        )
        description_label.grid(row=0, column=0, columnspan=4, sticky='w', padx=5, pady=(5, 10))

        ttk.Label(self, text="From X:").grid(row=1, column=0, sticky='w', padx=(20, 0), pady=2)
        self.from_x_entry = ttk.Entry(self, width=8)
        self.from_x_entry.grid(row=1, column=1, sticky='w', padx=(2, 10), pady=2)
        self.from_x_entry.insert(0, "-10")

        ttk.Label(self, text="To X:").grid(row=1, column=2, sticky='w', padx=(0, 0), pady=2)
        self.to_x_entry = ttk.Entry(self, width=8)
        self.to_x_entry.grid(row=1, column=3, sticky='w', padx=(2, 5), pady=2)
        self.to_x_entry.insert(0, "10")

        ttk.Label(self, text="From Z:").grid(row=2, column=0, sticky='w', padx=(20, 10), pady=2)
        self.from_z_entry = ttk.Entry(self, width=8)
        self.from_z_entry.grid(row=2, column=1, sticky='w', padx=(2, 5), pady=2)
        self.from_z_entry.insert(0, "-10")

        ttk.Label(self, text="To Z:").grid(row=2, column=2, sticky='w', padx=(0, 0), pady=2)
        self.to_z_entry = ttk.Entry(self, width=8)
        self.to_z_entry.grid(row=2, column=3, sticky='w', padx=(2, 5), pady=2)
        self.to_z_entry.insert(0, "10")

        self.set_btn = ttk.Button(
            self,
            text="Select",
            command=self.set_default_area,
            width=12
        )
        self.set_btn.grid(row=3, column=0,sticky = "w", padx = 20, pady=10)

        for i in range(4):
            self.columnconfigure(i, weight=1)

    def set_default_area(self):
        self.from_x_entry.delete(0, tk.END)
        self.from_x_entry.insert(0, "-10")
        self.to_x_entry.delete(0, tk.END)
        self.to_x_entry.insert(0, "10")
        self.from_z_entry.delete(0, tk.END)
        self.from_z_entry.insert(0, "-10")
        self.to_z_entry.delete(0, tk.END)
        self.to_z_entry.insert(0, "10")

    def clear_entries(self) -> None:
        self.from_x_entry.delete(0, tk.END)
        self.to_x_entry.delete(0, tk.END)
        self.from_z_entry.delete(0, tk.END)
        self.to_z_entry.delete(0, tk.END)

    def get_coordinates(self) -> Union[tuple, None]:
        try:
            from_x = int(self.from_x_entry.get())
            to_x = int(self.to_x_entry.get())
            from_z = int(self.from_z_entry.get())
            to_z = int(self.to_z_entry.get())
            return from_x, to_x, from_z, to_z
        except ValueError:
            return None

    def set_coordinates(self, from_x, to_x, from_z, to_z)-> None:
        self.from_x_entry.delete(0, tk.END)
        self.from_x_entry.insert(0, str(from_x))
        self.to_x_entry.delete(0, tk.END)
        self.to_x_entry.insert(0, str(to_x))
        self.from_z_entry.delete(0, tk.END)
        self.from_z_entry.insert(0, str(from_z))
        self.to_z_entry.delete(0, tk.END)
        self.to_z_entry.insert(0, str(to_z))

class TypedCombobox:
    def __init__(
            self,
            parent: tk.Widget,
            on_select: Optional[Callable[[str], None]] = None,
            values: Optional[List[str]] = None,
            theme: str = "clam",
            **kwargs: Any
    ) -> None:
        self._parent = parent
        self._on_select_callback = on_select
        self._values: List[str] = values.copy() if values else []
        self._apply_theme(theme)

        self._combobox = ttk.Combobox(
            parent,
            values=self._values,
            state = "readonly",
            **kwargs
        )

        self._setup_bindings()

    def _apply_theme(self, theme: str) -> None:
        try:
            style = ttk.Style()
            available_themes = style.theme_names()
            if theme in available_themes:
                style.theme_use(theme)
        except Exception:
            pass

    def _setup_bindings(self) -> None:
        self._combobox.bind("<<ComboboxSelected>>", self._on_select)

    def _on_select(self, event: tk.Event) -> None:
        if self._on_select_callback:
            selected_value = self._combobox.get()
            self._on_select_callback(selected_value)

    def update_values(self, new_values: List[str]) -> None:
        for value in new_values:
            if not isinstance(value, str):
                raise TypeError(f"Все значения должны быть строками, получено: {type(value)}")

        self._values = new_values.copy()
        self._combobox.configure(values=self._values)

    def update_callback(self, new_callback: Optional[Callable[[str], None]]) -> None:
        self._on_select_callback = new_callback

    def set(self, value: str) -> None:
        self._combobox.set(value)

    def get(self) -> str:
        return self._combobox.get()

    def current(self) -> int:
        return self._combobox.current()

    def grid(self, **kwargs: Any) -> None:
        self._combobox.grid(**kwargs)

    def pack(self, **kwargs: Any) -> None:
        self._combobox.pack(**kwargs)

    def place(self, **kwargs: Any) -> None:
        self._combobox.place(**kwargs)

    def configure(self, **kwargs: Any) -> None:
        self._combobox.configure(**kwargs)

    def destroy(self):
        self._combobox.destroy()

    @property
    def widget(self) -> ttk.Combobox:
        return self._combobox

    @property
    def values(self) -> List[str]:
        return self._values.copy()

    @property
    def callback(self) -> Optional[Callable[[str], None]]:
        return self._on_select_callback

    @property
    def parent(self):
        return self._parent

class SecondarySelection:

    def __init__(
            self,
            parent: tk.Widget,
            label_text: str = "",
            on_select: Optional[Callable] = None,
            values: Optional[List[str]] = None,
            spacing: int = 2,
            label_anchor: str = "w",
            combobox_width: int = 20,
            **kwargs: Any
    ) -> None:
        #Это класс для динамических комбобоксов, просто обычное добавление немного отстой(((
        self._container = ttk.Frame(parent)
        self._label = ttk.Label(self._container, text=label_text, anchor=label_anchor)
        self.frames = []
        self.typed_combobox = TypedCombobox(
            parent=self._container,
            on_select=on_select,
            values=values,
            width=combobox_width
        )

        self._label.grid(row=0, column=0, sticky="ws", pady=(0, spacing))
        self.typed_combobox.grid(row=1, column=0, sticky="w", pady = (0, 35))

        if kwargs:
            self.grid(**kwargs)

    def add_copy(self, copy_instance: 'SecondarySelection', box_command: Any = lambda x: x) -> None:
        if not isinstance(copy_instance, SecondarySelection):
            return

        label_config = {
            'text': copy_instance.label_widget.cget('text'),
            'anchor': copy_instance.label_widget.cget('anchor')
        }

        combobox_config = {
            'values': list(copy_instance.combobox_widget['values']),
            'width': copy_instance.combobox_widget.cget('width'),
            'on_select': box_command
        }

        copy_label = ttk.Label(self.container, **label_config)
        copy_combobox = TypedCombobox(self.container, **combobox_config)

        col = len(self.frames) + 1
        self.frames.append((copy_label, copy_combobox))

        copy_label.grid(row=0, column=col, sticky="ws", pady=(0, 2), padx = (20,0))
        copy_combobox.grid(row=1, column=col, sticky="w", pady=(0, 35), padx = (20,0))

        self.container.grid_columnconfigure(col, weight=1)

    def clear(self) -> None:
        for label, combobox in self.frames:
            label.destroy()
            combobox.destroy()
        self.frames.clear()

        for col in range(1, self.container.grid_size()[0]):
            self.container.grid_columnconfigure(col, weight=0)

    def grid(self, **kwargs: Any) -> None:
        self._container.grid(**kwargs)

    @property
    def label_widget(self) -> ttk.Label:
        return self._label

    @property
    def combobox_widget(self) -> ttk.Combobox:
        return self.typed_combobox.widget

    @property
    def container(self) -> ttk.Frame:
        return self._container
