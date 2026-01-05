from dataclasses import  dataclass
from typing import Tuple, Literal, Optional, Union
from pathlib import  Path
import numpy as np
Dimensions = Literal["End", "Nether", "Overworld"]

@dataclass(frozen=True)
class BlockID:
    id: str

@dataclass(frozen=True)
class TwoDimCord:
    arr: tuple

    @property
    def x(self) -> int:
        return int(self.arr[0])

    @property
    def z(self) -> int:
        return int(self.arr[1])

    @property
    def as_tuple(self) -> tuple:
        return int(self.arr[0]), int(self.arr[1])

    def __str__(self):
        return f"X: {self.x}, Z: {self.z}"

@dataclass(frozen=True)
class ThreeDimCord:
    arr: np.ndarray

    def __post_init__(self):
        if self.arr.shape != (3,):
            raise ValueError("ThreeDimCord must be shape (3,)")

    @property
    def x(self) -> int: return int(self.arr[0])
    @property
    def y(self) -> int: return int(self.arr[1])
    @property
    def z(self) -> int: return int(self.arr[2])

    @property
    def as_tuple(self):
        return int(self.arr[0]), int(self.arr[1]), int(self.arr[2])

    def __str__(self):
        return f"X: {self.x}, Y: {self.y}, Z: {self.z}"

@dataclass(frozen=True)
class Blocks:
    array: np.ndarray

    def __post_init__(self):
        if self.array.shape != (16, 256, 16):
            raise ValueError(f"Blocks array must be shape (16, 256, 16), got {self.array.shape}")

    def get(self, cord: ThreeDimCord) -> np.ndarray:
        return self.array[cord.x, cord.y, cord.z]

    def set(self, cord: ThreeDimCord, block_id: int) -> "Blocks":
        arr = self.array.copy()
        arr[cord.x, cord.y, cord.z] = block_id
        return Blocks(arr)

    def layer(self, y: int) -> np.ndarray:
        return self.array[:, y, :]

@dataclass(frozen=True)
class RawChunk:
    abs_cord: TwoDimCord
    raw_data: Union[bytes, None]
    dimension: Dimensions

    @property
    def exists(self) -> bool:
        return bool(self.raw_data)

    @property
    def bytes_size(self) -> int:
        return len(self.raw_data)

    @property
    def mb_size(self) -> float:
        return round(self.bytes_size / 1024 * 1024, 2)

    @property
    def rel_cord(self) -> Tuple[int, int]:
        return self.abs_cord.x % 32, self.abs_cord.z % 32

@dataclass(frozen=True)
class Chunk:
    chunk_cord: TwoDimCord
    blocks: Union[Blocks, None]

    def get_block(self, cord: ThreeDimCord) -> np.ndarray:
        return self.blocks.get(cord)

@dataclass(frozen=True)
class Entity:
    name: np.ndarray
    id: np.ndarray
    cord: np.ndarray
    hp: Optional[np.ndarray] = None

class Corners:
    def __init__(self,xmin, xmax, ymin, ymax):
        self._xmin = xmin
        self._xmax = xmax
        self._ymin = ymin
        self._ymax = ymax

    @property
    def xmin(self):
        return self._xmin

    @property
    def xmax(self):
        return self._xmax

    @property
    def ymin(self):
        return self._ymin

    @property
    def ymax(self):
        return self._ymax






