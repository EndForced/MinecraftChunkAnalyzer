from enum import Enum
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Type

#event registration


class Event(Enum):
    PATH_CHANGED = "path_changed"
    WORLD_SELECTED = "world_selected"

@dataclass(frozen=True)
class PathChanged:
    path: Path

@dataclass(frozen=True)
class WorldSelected:
    path: Path
    dim: str

EVENT_PAYLOAD: Dict[Event, Type] = {
    Event.PATH_CHANGED: PathChanged,
    Event.WORLD_SELECTED: WorldSelected
}

