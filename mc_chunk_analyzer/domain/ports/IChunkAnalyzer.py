import numpy as np
from ..models.Chunk import Chunk, RawChunk, ThreeDimCord, BlockID
from ..models.Region import RawRegion
from abc import ABC, abstractmethod
from ..models.Region import Region
from typing import List

class IChunkParser(ABC):
    def __init__(self):
        """Класс для парсинга чанков"""

    @abstractmethod
    def parse(self, raw_chunk:RawChunk) -> Chunk:
        """Превращение nbt в набор блоков/энтити"""

class IChunkAnalyzer(ABC):
    @abstractmethod
    def look_for_block(self, block: BlockID) -> bool:
        """Быстрое определение есть ли такой блок"""

    # @abstractmethod
    # def block_stat(self) -> Dict[BlockID.id:int]:
    #     """Статистика блоков в чанке"""

    # @abstractmethod
    # def blocks_in_area(self,p1: ThreeDimCord, p2:ThreeDimCord) -> np.ndarray[BlockID]:
    #     """Получение блоков области"""

    # @property
    # @abstractmethod
    # def palette(self) -> np.ndarray[BlockID]:
    #     """Получение списка блоков"""

    # @abstractmethod
    # def find_block(self, block: BlockID) -> np.ndarray[ThreeDimCord]:
    #     """Поиск блоков в чанке"""

    # @abstractmethod
    # def find_in_area(self, p1: ThreeDimCord, p2: ThreeDimCord, bid:BlockID) -> List[ThreeDimCord]:
    #     """Поиск блоков в области"""

class IMcaParser(ABC):
    def __init__(self):
        """Парсинг .mca регионов"""

    @abstractmethod
    def parse(self, region: RawRegion ) -> Region:
        """Распаковка координат и разархивация"""






