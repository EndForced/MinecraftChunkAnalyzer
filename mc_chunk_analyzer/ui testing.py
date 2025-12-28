import ttkbootstrap as ttk
from presentation.Widgets import ConsoleWidget, PathWidget, DimensionSelector
from pathlib import Path

root = ttk.Window(themename="darkly", size=(1000,720))
path = PathWidget(root,lambda a: print(a.parts))
path.pack()

dim = DimensionSelector(root)
# dim.pack()



console = ConsoleWidget(root, "cool console bro")
console.pack()
console.log("err", "error")
console.log("something happened")
root.mainloop()

