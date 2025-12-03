import os
from tkinter import filedialog
from typing import Dict
from pathlib import Path
from ttkbootstrap.constants import PRIMARY
from mcaOperations import ChunkManager
from Base_interface_blocks.TkinterModules import *


class PathHandler:
    def __init__(self):
        self.world_paths = None
        self.minecraft_path = "Not selected yet"
        self.combobox_value = "No saves/servers yet"
        self.payload: dict = {}

    def browse_directory(self, payload: Dict[str, Union[ttk.Label,SecondarySelection]]):
        appdata_path = os.path.expanduser('~\\AppData\\Roaming')
        self.minecraft_path = tk.filedialog.askdirectory(initialdir=appdata_path, title="Select .minecraft directory")
        saves = self.find_saves()
        payload["label"].configure(text=self.minecraft_path)
        selection_panel = payload["selection_panel"]
        selection_panel.clear()
        selection_panel.combobox_widget.configure(values=list(saves.keys()))
        selection_panel.combobox_widget.set("Select your save")
        self.payload = payload
        self.combobox_value = saves

    @staticmethod
    def look_for_folder(base_dir: Union[str, Path], folder_name: str) -> Union[Path, None]:
        for item in os.listdir(Path(base_dir)):
            if os.path.isdir(os.path.join(base_dir, item)):
                if item == folder_name:
                    return Path(base_dir, item)

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
    def show_info_popup(text, title="Warning"):
        popup = ttk.Toplevel(title=title)
        popup.geometry("400x150")
        popup.resizable(False, False)

        ttk.Label(popup, text=text, font=("Arial", 10)).pack(pady=20)
        ttk.Button(popup, text="OK", command=popup.destroy, bootstyle=PRIMARY).pack(pady=10)

class MinecraftChunkAnalyzer:
    def __init__(self):
        self.root = ttk.Window(
            title="Mca Analyzer",
            themename="darkly",
            size=(1000, 800),
            position=(100, 100),
            resizable=(True, True)
        )
        # ------------------My Classes----------------------#
        self.chunk_manager: ChunkManager = Optional[None]
        self.chunk_selection: ChunkSelectionFrame = Optional[None]
        self.path_handler = PathHandler()
        self.chunk_manager: ChunkManager = Optional[None]
        self.console: ColoredConsoleLabelFrame = Optional[None]
        self.secondary_select_world = SecondarySelection(ttk.Label(self.root), "Select world from bobby",
                                                         on_select=self.secondary_box_selection_processing,
                                                         values=["world_dirs"])
        self.dimension_panel = SecondarySelection(ttk.Frame(self.root), "123", lambda x: x, ["Overworld", "Nether", "End"])
        self.world_selection_panel: SecondarySelection = Optional[None]
        # ------------------TK Classes----------------------#
        self.current_path_value: ttk.Label = Optional[None]
        self.browse_file_btn: ttk.Button = Optional[None]


        # ------------------Variables--------------------#
        self.full_world_path: Path = Optional[None]

        # ------------------Methods--------------------#
        self.__setup_notebook(self.root)
        self.setup_info_frame()
        self.setup_future_features_frame()
        self.root.mainloop()

    def __setup_notebook(self, root):
        #Настройка вкладок для листания
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(side="top", pady=15, padx=15, expand=True, fill='both')

        #Создание вкладок
        self.info_frame = ttk.Frame(self.notebook)
        self.chunk_analytics_frame = ttk.Frame(self.notebook)
        self.block_search_frame = ttk.Frame(self.notebook)
        self.future_features_frame = ttk.Frame(self.notebook)

        #И добавление их
        self.notebook.add(self.info_frame, text="Info")
        self.notebook.add(self.chunk_analytics_frame, text="Chunk Analytics")
        self.notebook.add(self.block_search_frame, text="Block Search")
        self.notebook.add(self.future_features_frame, text="Future Features")

    def setup_future_features_frame(self):
        #Тут просто статические надписи, ничего интересного
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

    def secondary_box_selection_processing(self, event):
        self.console.clear() #Стираем с консоли
        world_name = str(Path(self.full_world_path, self.secondary_select_world.combobox_widget.get(), self.world_selection_panel.frames[0][1].get()))
        #Имя мира - базовая папка бобби + название сервера + название мира
        self.console.log(f"Loading {world_name} data")
        self.chunk_manager = ChunkManager(world_name) #создаем  чанк менеджер
        data_info = self.chunk_manager.find_mca_files(world_name)

        if len(data_info["files"]) > 0: #если есть .mca файлы
            if len(self.world_selection_panel.frames) < 2: #и не добавили панель выбора измерения
                self.world_selection_panel.add_copy(self.dimension_panel) #добавляем панель измерения
            self.console.log(
                f"Successfully loaded {len(data_info['files'])} region files with total size of {data_info['total_size_mb']} mb")
        else:
            self.console.log(
                f"Unable to find any .mca files which is strange. Trying to find in {self.full_world_path}")

    def combobox_selection_processing(self, event):
        self.console.clear()
        self.world_selection_panel.clear()

        #Получение пути до папки мира
        world_name = self.world_selection_panel.combobox_widget.get()
        self.full_world_path = self.path_handler.world_paths[world_name]

        #Если это папка бобби, то нужно создать еще один комбобокс, поэтому перенаправляем на специальную функцию
        if ".bobby" in Path(self.full_world_path).parts:
            world_dirs = [path.name for path in Path(self.full_world_path).iterdir() if path.is_dir()] #Получаем имена всех папок в папке бобби
            self.secondary_select_world.combobox_widget.config(values = world_dirs) #И добавляем их в комбобокс второго выбора мира
            self.world_selection_panel.add_copy(self.secondary_select_world, self.secondary_box_selection_processing) #Ну и добавляем в панель выбора мира поле для выбора мира из бобби
            return

        #тут тоже самое что и в первой функции
        self.console.log(f"Loading {world_name} data")
        self.chunk_manager = ChunkManager(self.full_world_path)
        data_info = self.chunk_manager.find_mca_files(self.full_world_path)
        if len(data_info["files"]) > 0:
            self.console.log(
                f"Successfully loaded {len(data_info['files'])} region files with total size of {data_info['total_size_mb']} mb")
            self.world_selection_panel.add_copy(self.dimension_panel)
        else:
            self.console.log(
                f"Unable to find any .mca files which is strange. Trying to find in {self.full_world_path}")

    def setup_info_frame(self):
        info_frame = self.info_frame
        # настройки грида
        info_frame.grid_rowconfigure(4, weight=1)
        info_frame.grid_columnconfigure(0, weight=1)
        info_frame.grid_columnconfigure(1, weight=1)
        self.dimension_panel = SecondarySelection(self.info_frame, label_text="Select dimension", on_select=lambda x: x,
                                                  values=["Overworld", "Nether", "End"])

        # лейбл для "Current path"
        current_path_label = ttk.Label(info_frame, text="Current path:", font=("Arial", 10, "bold"))
        current_path_label.grid(row=1, column=0, sticky="w", pady=(16, 0), padx=(20, 0))
        # лейбл для отображения самого пути
        self.current_path_value = ttk.Label(info_frame, text="Not selected yet")
        self.current_path_value.grid(row=1, column=1, sticky="w", pady=(16, 0), padx=(10, 0))
        # # выпадающий список для выбора мира
        self.world_selection_panel = SecondarySelection(self.info_frame, "World Selection", on_select=self.combobox_selection_processing, values=["Your servers and saves"])
        self.world_selection_panel.combobox_widget.set("Select your save")

        #Настройки кнопки выбора мира
        payload = {"selection_panel": self.world_selection_panel, "label": self.current_path_value, "root": self.root}
        self.browse_file_btn = ttk.Button(
            master=info_frame,
            command=lambda: (self.path_handler.browse_directory(payload), self.root.focus()),
            text="Select .minecraft folder",
        )
        self.browse_file_btn.grid(row=0, column=0, sticky="w", padx=(15, 0), pady=(10, 0))

        self.world_selection_panel.container.grid(row = 3, column = 0, sticky = "w", padx=(20, 5), pady=(20, 5))
        self.console = ColoredConsoleLabelFrame(info_frame)
        self.console.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=(20, 20), pady=(10, 20))
        self.chunk_selection = ChunkSelectionFrame(info_frame)
        self.chunk_selection.grid(row=5, column=0, columnspan=2, sticky="ew", padx=(20, 20), pady=(0, 20))


if __name__ == "__main__":
    app = MinecraftChunkAnalyzer()
