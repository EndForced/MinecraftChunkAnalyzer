import ttkbootstrap as ttk
import os
from  tkinter import filedialog
from typing import Union, Dict
from pathlib import Path
from ttkbootstrap.constants import PRIMARY
from datetime import datetime
from mcaOperations import ChunkManager

class PathHandler:
    def __init__(self):
        self.world_paths = None
        self.minecraft_path = "Not selected yet"
        self.combobox_value = "No saves/servers yet"
        self.payload: dict = None



    def browse_directory(self, payload: Dict[str, Union[ttk.Label, ttk.Combobox]]):
        appdata_path = os.path.expanduser('~\\AppData\\Roaming')
        self.minecraft_path = tk.filedialog.askdirectory(initialdir=appdata_path, title="Select .minecraft directory")
        saves = self.find_saves()
        payload["label"].config(text = self.minecraft_path)
        payload["combobox"].config(values = list(saves.keys()))
        self.payload = payload
        self.combobox_value = saves

    @staticmethod
    def look_for_folder(base_dir: Union[str, Path], folder_name:str) -> Union[Path, None]:
        for item in os.listdir(Path(base_dir)):
            if os.path.isdir(os.path.join(base_dir, item)):
                if item == folder_name:
                    return Path(base_dir,item)

    def find_saves(self) -> Dict[str, str]:
        worlds = {}
        exist_troubles_message = ""

        saves_path = Path(self.minecraft_path, "saves")
        if os.path.exists(saves_path):
            saves_folders = [item for item in os.listdir(saves_path)
                             if os.path.isdir(os.path.join(saves_path, item))]
            for world_name in saves_folders:
                worlds[world_name] = str(Path(saves_path, world_name))
        else:
            exist_troubles_message = "No saves folder found"

        bobby_path = Path(self.minecraft_path, ".bobby")
        if os.path.exists(bobby_path):
            bobby_folders = [item for item in os.listdir(bobby_path)
                             if os.path.isdir(os.path.join(bobby_path, item))]
            for world_name in bobby_folders:
                full_path = str(Path(bobby_path, world_name))
                if world_name in worlds:
                    worlds[f"{world_name} (bobby)"] = full_path
                else:
                    worlds[world_name] = full_path
        else:
            if exist_troubles_message:
                exist_troubles_message = "No .bobby and saves folder, can't load any data"
            else:
                exist_troubles_message = "No .bobby folder, that means no data from multiplayer"
        if exist_troubles_message:
            self.show_info_popup(exist_troubles_message)
        
        self.world_paths = worlds
        return worlds

    @staticmethod
    def show_info_popup(text, title = "Warning"):
        popup = ttk.Toplevel(title=title)
        popup.geometry("400x150")
        popup.resizable(False, False)

        ttk.Label(popup, text=text, font=("Arial", 10)).pack(pady=20)
        ttk.Button(popup, text="OK", command=popup.destroy, bootstyle=PRIMARY).pack(pady=10)
import tkinter as tk

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

    def clear_entries(self):
        self.from_x_entry.delete(0, tk.END)
        self.to_x_entry.delete(0, tk.END)
        self.from_z_entry.delete(0, tk.END)
        self.to_z_entry.delete(0, tk.END)

    def get_coordinates(self):
        try:
            from_x = int(self.from_x_entry.get())
            to_x = int(self.to_x_entry.get())
            from_z = int(self.from_z_entry.get())
            to_z = int(self.to_z_entry.get())
            return from_x, to_x, from_z, to_z
        except ValueError:
            return None

    def set_coordinates(self, from_x, to_x, from_z, to_z):
        self.from_x_entry.delete(0, tk.END)
        self.from_x_entry.insert(0, str(from_x))
        self.to_x_entry.delete(0, tk.END)
        self.to_x_entry.insert(0, str(to_x))
        self.from_z_entry.delete(0, tk.END)
        self.from_z_entry.insert(0, str(from_z))
        self.to_z_entry.delete(0, tk.END)
        self.to_z_entry.insert(0, str(to_z))

class ColoredConsoleLabelFrame(ttk.Labelframe):
    def __init__(self, parent, title="Info", max_lines=15, **kwargs):
        super().__init__(parent, text=title, **kwargs)
        self.max_lines = max_lines
        self.setup_ui()

    def setup_ui(self):
        self.text_widget = tk.Text(
            self,
            height=8,
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

        # Настройка цветов для разных типов сообщений
        self.text_widget.tag_configure("info", foreground="#CCCCCC")
        self.text_widget.tag_configure("success", foreground="#4EC9B0")
        self.text_widget.tag_configure("warning", foreground="#FFC66D")
        self.text_widget.tag_configure("error", foreground="#F44747")

    def log(self, message, level="info"):
        """Добавление сообщения с цветовым кодированием"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"

        self.text_widget.config(state=tk.NORMAL)

        # Добавляем сообщение с соответствующим тегом
        self.text_widget.insert(tk.END, formatted_message, level)
        self.text_widget.see(tk.END)

        # Ограничение количества строк
        lines = int(self.text_widget.index('end-1c').split('.')[0])
        if lines > self.max_lines:
            self.text_widget.delete(1.0, 2.0)  # Удаляем первую строку

        self.text_widget.config(state=tk.DISABLED)

    def clear(self):
        """Очистка консоли"""
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.config(state=tk.DISABLED)

class MinecraftChunkAnalyzer:
    def __init__(self):
        self.chunk_selection = None
        self.full_world_path = None
        self.current_path_value: ttk.Label = None
        self.saves_combobox: ttk.Combobox = None
        self.browse_file_btn: ttk.Button = None

        self.root = ttk.Window(
            title="Mca Analyzer",
            themename="darkly",
            size=(1000, 600),
            position=(100, 100),
            resizable=(True, True)
        )
        self.path_handler = PathHandler()
        self.chunk_manager: ChunkManager
        self.console: ColoredConsoleLabelFrame = None

        self.__setup_notebook(self.root)
        self.setup_info_frame()
        self.setup_future_features_frame()
        self.root.mainloop()

    def __setup_notebook(self, root):
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(side="top", pady=15, padx=15, expand=True, fill='both')

        # Используем ttk.Frame вместо tk.Frame для consistency
        self.info_frame = ttk.Frame(self.notebook)
        self.chunk_analytics_frame = ttk.Frame(self.notebook)
        self.block_search_frame = ttk.Frame(self.notebook)
        self.future_features_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.info_frame, text="Info")
        self.notebook.add(self.chunk_analytics_frame, text="Chunk Analytics")
        self.notebook.add(self.block_search_frame, text="Block Search")
        self.notebook.add(self.future_features_frame, text="Future Features")

    def setup_future_features_frame(self):
        main_frame = ttk.Frame(self.future_features_frame)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        title_label = ttk.Label(
            main_frame,
            text="Future Features",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 20))

        features_frame = ttk.Labelframe(main_frame, text="Planned Features", padding=15)
        features_frame.pack(fill='x', pady=(0, 15))

        features_text = """
    • Isolated area render
    • Cobble/obsidian generation prediction  
    • Chunks seedcracking (maybe)
    • Advanced optimization
    """
        features_label = ttk.Label(features_frame, text=features_text, justify='left')
        features_label.pack(anchor='w')

        contact_frame = ttk.Labelframe(main_frame, text="Contribute", padding=15)
        contact_frame.pack(fill='x', pady=(0, 15))

        contact_text = "Want to request features or contribute?\nContact me via Telegram: @EndForced"
        contact_label = ttk.Label(contact_frame, text=contact_text, justify='center')
        contact_label.pack(anchor='w')

    def combobox_selection_processing(self, event):
        self.console.clear()
        world_name = self.saves_combobox.get()
        self.full_world_path = self.path_handler.world_paths[world_name]
        self.console.log(f"Loading {world_name} data")
        self.chunk_manager = ChunkManager(self.full_world_path)
        data_info = self.chunk_manager.find_mca_files(self.full_world_path)
        if len(data_info["files"]) > 0:
            self.console.log(f"Successfully loaded {len(data_info['files'])} files with total size of {data_info['total_size_mb']} mb")
        else:
            self.console.log(f"Unable to find any .mca files which is strange. Trying to find in {self.full_world_path}")

    def setup_info_frame(self):
        info_frame = self.info_frame
        info_frame.grid_rowconfigure(4, weight=1)
        info_frame.grid_columnconfigure(0, weight=1)
        info_frame.grid_columnconfigure(1, weight=1)

        current_path_label = ttk.Label(info_frame, text="Current path:", font=("Arial", 10, "bold"))
        current_path_label.grid(row=1, column=0, sticky="w", pady=(16, 0), padx=(10, 0))

        self.current_path_value = ttk.Label(info_frame, text="Not selected yet")
        self.current_path_value.grid(row=1, column=1, sticky="w", pady=(16, 0), padx=(10, 0))

        self.saves_combobox = ttk.Combobox(
            info_frame,
            state="readonly",
            values=["your saves and servers"],
        )
        self.saves_combobox.bind("<<ComboboxSelected>>", self.combobox_selection_processing)

        payload = {"combobox": self.saves_combobox, "label": self.current_path_value, "root": self.root}
        self.browse_file_btn = ttk.Button(
            master=info_frame,
            command=lambda: (self.path_handler.browse_directory(payload), self.root.focus()),
            text="Select .minecraft folder",
            bootstyle="dark",
        )
        self.browse_file_btn.grid(row=0, column=0, sticky="w", padx=(15, 0), pady=(10, 0))

        saves_label = ttk.Label(info_frame, text="World selection:")
        saves_label.grid(row=2, column=0, sticky="w", padx=(20, 5), pady=(20, 5))
        self.saves_combobox.grid(row=3, column=0, sticky="ew", padx=(20, 20), pady=(0, 10))
        self.console = ColoredConsoleLabelFrame(info_frame)
        self.console.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=(20, 20), pady=(10, 20))
        self.chunk_selection = ChunkSelectionFrame(info_frame)
        self.chunk_selection.grid(row=5, column=0, columnspan=2, sticky="ew", padx=(20, 20), pady=(0, 20))





if __name__ == "__main__":
    app = MinecraftChunkAnalyzer()
