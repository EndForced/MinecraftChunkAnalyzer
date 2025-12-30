from PIL.ImageOps import expand

from ..interfaces.INotebook import INotebookPage
from ..Widgets import ConsoleWidget, PathWidget, DimensionSelector
import ttkbootstrap as ttk
from ..utils import EventBus

class InfoTab(INotebookPage, ttk.Frame):
    def __init__(self):
        super().__init__(name = "Info")
        self.bus = EventBus()
        self._console = ConsoleWidget(self)
        self._path_widget = PathWidget(self, self.bus)
        self._dim_selector = DimensionSelector(self, self.bus)
        self._setup_ui()

    def _setup_ui(self):
        self._path_widget.grid(row = 0, column = 0, pady = 10, padx = 20, stick = "w")
        self._dim_selector.grid(row = 1,column = 0, pady = 20, padx = 40, stick = "w")
        self._console.place(width = 400, height = 400, y = 200, x = 40)
        self._console.log("App started","success")


