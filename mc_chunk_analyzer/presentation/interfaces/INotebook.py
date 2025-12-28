import ttkbootstrap as ttk

class INotebookPage(ttk.Frame):
    def __init__(self, name: str):
        super().__init__()
        self.name = name

class IInfoPage(INotebookPage):
        def __init__(self):
            super().__init__("Info")


