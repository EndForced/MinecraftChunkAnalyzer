from .IChunkAnalyzer import RawChunk, Chunk
from abc import ABC, abstractmethod

from ..models.NBT import NBTTag
from ..models.NBTInfo import NBTTagSpec


class INBTReader(ABC):
    def __init__(self):
        """Класс для быстрого чтения nbt"""

    @abstractmethod
    def parse_chunk(self, raw_chunk: RawChunk) -> Chunk:
        """Распаковка блоков, палитры"""


class INBTSkipper(ABC):
    def __init__(self):
        """Класс для скипа тегов, возвращает оффсет в байтах
        ВАЖНО: Не умеет работать с compound, в начале распаковывайте его до внутренних тегов, а потом передавайте сюда"""

    @abstractmethod
    def skip(self, data: bytes, tag_spec: NBTTagSpec) -> int:
        """Функция скипа"""


class INBTTagReader(ABC):
    def __init__(self):
        """Класс для чтения и скипа nbt тегов"""

    def get_inside(self, path: list) -> NBTTag:
        """
        Быстрый парсинг nbt, не загружает ничего кроме конечного тега пути
        После парсинга содержимое поля datf класса меняется на payload целевого тега
        :param path: путь к целевому тегу ["", ...]
        :return: None если не получилось True при успехе
        """


    @abstractmethod
    def read(self) -> NBTTag:
        """Метод для чтения nbt файла"""

    @abstractmethod
    def get_next_type(self) -> NBTTagSpec:
        """Получение типа следующего тега"""

    @abstractmethod
    def get_next_name(self) -> str:
        """Получить имя следующего тега"""

    @abstractmethod
    def _read_base(self, tag_spec: NBTTagSpec) -> int:
        """Метод чтения простых тегов с фиксированной длинной"""