from abc import abstractmethod
from .models import WorldPath
from pathlib import Path

class IWorldInfo:
    def __init__(self, path: WorldPath) -> None:
        """
        :param path: WorldPath instance
        """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        :return: name of world as str
        """

    @property
    @abstractmethod
    def overpath(self) -> Path:
        """
        :return: path to path with .mca files
        """

    @property
    @abstractmethod
    def netherpath(self) -> Path:
        """
        :return: path to path with .mca files
        """

    @property
    @abstractmethod
    def endpath(self) -> Path:
        """
        :return: path to path with .mca files
        """

    @property
    @abstractmethod
    def size_mb(self) -> int:
        """

        :return:
        """

