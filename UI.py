import tkinter as tk

import ttkbootstrap as ttk
import os
from  tkinter import filedialog
from typing import Union, List, Dict
from pathlib import Path

class PathHandler:
    def __init__(self):
        self.minecraft_path = "Not selected yet"
        self.combobox_value = "No saves/servers yet"

    def browse_directory(self, payload: Dict[str, Union[ttk.Label, ttk.Combobox]]):
        appdata_path = os.path.expanduser('~\\AppData\\Roaming')
        self.minecraft_path = tk.filedialog.askdirectory(initialdir=appdata_path, title="Select .minecraft directory")
        payload["label"].config(text = self.minecraft_path)
        payload["combobox"].config(values = self.find_saves())
        self.combobox_value = self.find_saves()

    @staticmethod
    def look_for_folder(base_dir: Union[str, Path], folder_name:str) -> Union[Path, None]:
        for item in os.listdir(Path(base_dir)):
            if os.path.isdir(os.path.join(base_dir, item)):
                if item == folder_name:
                    return Path(base_dir,item)

    def find_saves(self) -> List[str]:
        res = []
        saves_path = Path(self.minecraft_path,"saves")
        if os.path.exists(saves_path):
            saves_folders = [item for item in os.listdir(saves_path) if os.path.isdir(os.path.join(saves_path, item))]
            res.extend(saves_folders)

        bobby_path = Path(self.minecraft_path, ".bobby")
        if os.path.exists(bobby_path):
            bobby_folders = [item for item in os.listdir(bobby_path) if os.path.isdir(os.path.join(bobby_path, item))]
            res.extend(bobby_folders)

        return res






class MinecraftChunkAnalyzer:
    def __init__(self):
        self.current_path_value: ttk.Label = None
        self.saves_combobox: ttk.Combobox = None
        self.browse_file_btn: ttk.Button = None
        self.root = ttk.Window(
            title="Mca Analyzer",
            themename="darkly",
            size=(800, 600),
            position=(100, 100),
            resizable=(True, True)
        )
        self.ph = PathHandler()

        self.__setup_notebook(self.root)
        self.setup_info_frame()
        self.setup_future_features_frame()
        self.root.mainloop()



    def __setup_notebook(self, root):
            self.notebook = ttk.Notebook(root)
            self.notebook.pack(side = "top", pady=15, padx=15, expand=True, fill='both')

            self.info_frame = tk.Frame(self.notebook, bg="#f0f0f0")
            self.chunk_analytics_frame = tk.Frame(self.notebook, bg="#f0f0f0")
            self.block_search_frame = tk.Frame(self.notebook, bg="#f0f0f0")
            self.future_features_frame = tk.Frame(self.notebook, bg="#f0f0f0")

            self.notebook.add(self.info_frame, text="Info")
            self.notebook.add(self.chunk_analytics_frame, text="Chunk Analytics")
            self.notebook.add(self.block_search_frame, text="Block Search")
            self.notebook.add(self.future_features_frame, text = "Future Features")

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

    def setup_info_frame(self):
        info_frame = self.info_frame

        current_path_label = ttk.Label(info_frame, text="Current path:",font=("Arial",10,"bold"))
        current_path_label.grid(row=1, column=1, sticky="w", pady=(16, 0), padx = (10,0))

        self.current_path_value = ttk.Label(info_frame, text = "Not selected yet")
        self.current_path_value.grid(row=1, column=2, sticky="w", pady=(16, 0), padx = (10,0))

        self.saves_combobox = ttk.Combobox(
            info_frame,
            state="readonly",
            values=["your saves and servers"]
        )

        payload = {"combobox": self.saves_combobox, "label": self.current_path_value}
        self.browse_file_btn = ttk.Button(
            master=self.info_frame,
            command= lambda: (self.ph.browse_directory(payload), self.root.focus()),
            text="Select .minecraft folder",
            bootstyle = "dark",
        )
        self.browse_file_btn.grid(row=1, column=0, sticky="nsew", padx= (15,0), pady=(10,0))


        saves_label = ttk.Label(info_frame, text="Save selection:")
        saves_label.grid(row=2, column=0, sticky="w", padx=(20, 5), pady=(20, 5))
        self.saves_combobox.grid(row=3, column=0, sticky="ew", padx=(20, 20), pady=(0, 20))
        info_frame.grid_columnconfigure(0, weight=0)



if __name__ == "__main__":
    app = MinecraftChunkAnalyzer()
