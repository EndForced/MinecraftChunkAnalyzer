import numpy as np
from ..models.Chunk import Chunk, RawChunk, ThreeDimCord, BlockID
from ..models.Region import RawRegion
from abc import ABC, abstractmethod
from typing import Dict
from ..models.Region import Region

class IChunkParser(ABC):
    def __init__(self):
        """Класс для парсинга чанков"""

    @abstractmethod
    def parse(self, raw_chunk:RawChunk) -> Chunk:
        """Превращение nbt в набор блоков/энтити"""

class IChunkAnalyzer(ABC):
    def __init__(self, chunk: Chunk):
        self.chunk = chunk
        """Класс для анализа чанка"""

    @abstractmethod
    def is_a_block(self, block: BlockID) -> bool:
        """Быстрое определение есть ли такой блок"""

    # @abstractmethod
    # def block_stat(self) -> Dict[BlockID.id:int]:
    #     """Статистика блоков в чанке"""

    @abstractmethod
    def blocks_in_area(self,p1: ThreeDimCord, p2:ThreeDimCord) -> np.ndarray[BlockID]:
        """Получение блоков области"""

    @property
    @abstractmethod
    def palette(self) -> np.ndarray[BlockID]:
        """Получение списка блоков"""

    @abstractmethod
    def find_block(self, block: BlockID) -> np.ndarray[ThreeDimCord]:
        """Поиск блоков в чанке"""

    @abstractmethod
    def find_in_area(self, p1: ThreeDimCord, p2: ThreeDimCord, bid:BlockID):
        """Поиск блоков в области"""

class IMcaParser(ABC):
    def __init__(self):
        """Парсинг .mca регионов"""

    @abstractmethod
    def parse(self, region: RawRegion ) -> Region:
        """Распаковка координат и разархивация"""






