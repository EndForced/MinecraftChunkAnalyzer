from pathlib import Path
from typing import Dict, List
from .models import WorldTree
import os

def search_for_files(files: List[str], root: Path) -> List[Path]:
    targets = set(files)
    found: List[Path] = []

    for path in root.rglob("*"):
        if path.is_file() and path.name in targets:
            found.append(path)

    return found


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
        if not self._bobby_enabled:
            return {}
        bobby_dir = Path(self.path, ".bobby")
        if not bobby_dir.exists() or not bobby_dir.is_dir():
            return {}
        result = {}
        for server in bobby_dir.iterdir():
            if not server.is_dir():
                continue
            server_key = f"{server.name}(server)"
            worlds = {
                world.name: world
                for world in server.iterdir()
                if world.is_dir()
            }
            result[server_key] = worlds
        return result

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

class WorldInfo:
    def __init__(self, path: Path):
        self.path = path

    @property
    def size_mb(self) -> int:
       return os.path.getsize(self.path)

    @property
    def name(self) -> str:
        return self.path.parts[-1]

    def path_to_dim(self, dim: str):
        if dim not in ["over", "end", "nether"]:
            raise ValueError(f"Can't get path to dim {dim}") from ValueError

