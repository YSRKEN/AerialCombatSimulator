from abc import ABCMeta, abstractmethod
from typing import List, Union


class Dom(metaclass=ABCMeta):
    @abstractmethod
    def select_many(self, css_selector: str) -> List[any]:
        pass

    @abstractmethod
    def select(self, css_selector: str) -> Union[None, any]:
        pass
