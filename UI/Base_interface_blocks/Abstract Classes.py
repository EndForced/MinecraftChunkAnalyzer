from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple, List
from mcaOperations import ChunkManager


@dataclass
class Block:
    """Блок с координатами, ID, названием и палитрой."""
    cord: Tuple[int, int]
    id: int
    name: str
    palette: List[str]


class StatisticPanel(ABC):
    @abstractmethod
    def __init__(self, chunk_analyzer: ChunkManager):
        """
        Получает объект ChunkManager, который анализирует чанк.
        """
        pass

    @abstractmethod
    def update(self):
        """
        Обновление данных статистики.
        """
        pass

    @property
    @abstractmethod
    def stats_csv(self) -> bytes:
        """
        Возвращает данные CSV/Excel в бинарном виде.
        """
        pass

    @abstractmethod
    def hide_block(self, block: Block):
        """
        Скрывает блок из итоговой статистики.
        """
        pass
