from dataclasses import dataclass
from typing import List, Optional, Literal
from .Chunk import TwoDimCord, Dimensions
from pathlib import Path

from mc_chunk_analyzer.domain.models.Chunk import RawChunk

@dataclass(frozen=True)
class RawRegion:
    data: bytes
    cord: TwoDimCord
    dimension: Dimensions

@dataclass(frozen=True)
class Region:
    readable: bool
    cord: TwoDimCord
    raw_chunks: dict[TwoDimCord, RawChunk]
    dimension: Dimensions

@dataclass(frozen=False)
class World:
    path: Path
    name: str
    regions: List[Region]
    version: Optional[str] = None
