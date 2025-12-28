from dataclasses import dataclass
from typing import Union, Optional, Dict, List
from pathlib import Path

@dataclass(frozen=True)
class WorldPath:
    world_path: Union[str,Path]

    def __post_init__(self):
        if type(self.world_path) != Path:
            path = Path(self.world_path)
            path.resolve(strict=True)
            self.__setattr__("world_path",path)

@dataclass(frozen=True)
class WorldTree:
    worlds: Dict[str,Path]
    bobby_words: Optional[Dict[str, list]]



