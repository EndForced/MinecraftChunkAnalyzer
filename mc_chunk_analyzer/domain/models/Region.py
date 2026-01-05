from dataclasses import dataclass, field
from typing import List, Optional, Literal
from .Chunk import TwoDimCord, Dimensions
from pathlib import Path
from typing import Tuple
from mc_chunk_analyzer.domain.models.Chunk import RawChunk

from dataclasses import dataclass, field
from pathlib import Path
from typing import Tuple

@dataclass(frozen=True)
class RawRegion:
    path: Path
    dimension: Dimensions
    data: bytes = field(init=False)
    cord: TwoDimCord = field(init=False)

    def __post_init__(self):
        path = Path(self.path)

        if not path.is_file():
            raise FileNotFoundError(path)
        with path.open("rb") as f:
            data = f.read()
        name = path.stem  # r.-6.-6
        x, z = self.cord_from_string(name)

        object.__setattr__(self, "data", data)
        object.__setattr__(self, "cord", TwoDimCord((x, z)))

    @staticmethod
    def cord_from_string(name: str) -> Tuple[int, int]:
        parts = name.split(".")
        if len(parts) != 3 or parts[0] != "r":
            raise ValueError(f"Invalid region name: {name}")

        try:
            x = int(parts[1])
            z = int(parts[2])
        except ValueError:
            raise ValueError(f"Invalid integer in region name: {name}")

        return x, z


@dataclass(frozen=True)
class Region:
    readable: bool
    raw_chunks: dict[TwoDimCord, RawChunk]
    dimension: Dimensions
    name: str
    cord: TwoDimCord = field(init=False)

    def __post_init__(self):
        x, z = self.cord_from_string(self.name)
        object.__setattr__(self, "cord", TwoDimCord((x, z)))

    @staticmethod
    def cord_from_string(name: str) -> Tuple[int, int]:
        if not name.endswith(".mca"):
            raise ValueError(f"Invalid region string (missing .mca): {name}")

        # убираем расширение
        name_no_ext = name[:-4]  # r.-1.-1

        parts = name_no_ext.split(".")
        if len(parts) != 3 or parts[0] != "r":
            raise ValueError(f"Invalid region string: {name}")

        try:
            x = int(parts[1])
            z = int(parts[2])
        except ValueError:
            raise ValueError(f"Invalid integer in region string: {name}")

        return x, z


@dataclass(frozen=False)
class World:
    path: Path
    name: str
    regions: List[Region]
    version: Optional[str] = None
