from dataclasses import dataclass
from typing import List, Dict, Union, Literal, Optional, Any

Byte_order = Literal["normal", "reversed"]


@dataclass(frozen=True)
class NBTTag:
    name: Optional[str]
    byte_order: Byte_order = "normal"
    value: Any = None


