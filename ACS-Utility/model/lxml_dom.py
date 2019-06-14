from typing import Union, List

import lxml.html

from model.i_dom import Dom


class LxmlDom(Dom):
    def __init__(self, raw_dom: lxml.html.HtmlElement):
        self.raw_dom = raw_dom

    def select_many(self, css_selector: str) -> List[Dom]:
        result: List[lxml.html.HtmlElement] = self.raw_dom.cssselect(css_selector)
        return [LxmlDom(x) for x in result]

    def select(self, css_selector: str) -> Union[None, Dom]:
        result: List[lxml.html.HtmlElement] = self.raw_dom.cssselect(css_selector)
        if len(result) == 0:
            return None
        else:
            return LxmlDom(result[0])
