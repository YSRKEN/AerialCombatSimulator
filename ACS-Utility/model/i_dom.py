from abc import ABCMeta, abstractmethod
from typing import List, Union


class Dom(metaclass=ABCMeta):
    @abstractmethod
    # Python3の仕様上、Type Hintingを再帰的に定義するには、
    # Hint側で当該型を引用符で囲む必要がある(前方参照、PEP 484)
    # 参考：https://stackoverflow.com/questions/38340808/recursive-typing-in-python-3-5
    def select_many(self, css_selector: str) -> List['Dom']:
        pass

    @abstractmethod
    def select(self, css_selector: str) -> Union[None, 'Dom']:
        pass

    @abstractmethod
    def inner_text(self) -> str:
        pass
