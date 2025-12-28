from ttkbootstrap import Window
from ttkbootstrap import Notebook, Frame, Label
from .presentation.tabs.info import InfoTab


class App:
    def __init__(self, root: Window):
        self.root = root
        self.notebook = Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)
        self.tabs = []

    def add_tab(self, title: str, widget_class=Frame, **kwargs):
        tab_frame = widget_class()
        self.notebook.add(tab_frame, text=title)
        self.tabs.append(tab_frame)
        return tab_frame

    def get_tabs(self) -> list:
        return self.tabs

# --- пример использования ---
if __name__ == "__main__":
    root = Window(themename="darkly", size=(1000,720), title = "ChunkAnalyzer")
    app = App(root)
    tab1 = app.add_tab("Selection", InfoTab)
    root.mainloop()
