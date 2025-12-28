from pathlib import Path
from typing import Dict, List
from .models import WorldTree
import os

class PathInfo:
    def __init__(self, path: Path):
        self.path = path

    def change_path(self, path):
        self.path = path

    @property
    def _bobby_enabled(self) -> bool:
        if ".bobby" in os.listdir(self.path):
            return True
        return False

    @property
    def _bobby(self):
        if not self._bobby_enabled: return []
        res = {}
        for p in os.listdir(Path(self.path,".bobby")):
            res[p+"(server)"] = []
            for subp in os.listdir(Path(self.path,".bobby",p)):
                res[p+"(server)"].append(subp)
        return res

    @property
    def _saves(self):
        saves_dir = Path(self.path, "saves")
        if not saves_dir.exists() or not saves_dir.is_dir():
            return {}
        saves_dirs = [
            saves_dir / p
            for p in os.listdir(saves_dir)
            if (saves_dir / p).is_dir()
        ]
        return {p.name: p for p in saves_dirs}

    @property
    def get_data(self) -> WorldTree:
        return WorldTree(worlds=self._saves, bobby_words=self._bobby)
