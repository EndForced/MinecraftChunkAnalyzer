from tkinter import Widget, LabelFrame
from abc import ABC, abstractmethod

import ttkbootstrap


class IConsoleWidget(LabelFrame, ABC):
    @abstractmethod
    def log(self, message, level):
        """Метод делающий запись"""

    @abstractmethod
    def clear(self):
        """Очистка консоли"""

class IPathWidget(Widget, ABC):
    """
    :return вызывает callable с объектом класса Path с выбранной директорией
    """
    @abstractmethod
    def __init__(self, on_change: callable):
        super().__init__()


class IDimensionSelector(ABC):
    def __init__(self, on_change: callable):
        """
        Класс для выбора измерения
        При выборе вызывает callable с выбранным вариантом
        """
