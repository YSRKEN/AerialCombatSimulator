from abc import ABCMeta, abstractmethod
from typing import Union

from model.i_dom import Dom


class DomService(metaclass=ABCMeta):
    @abstractmethod
    def create_dom_from_url(self, url: str, encoding: str='UTF-8') -> Union[None, Dom]:
        pass
