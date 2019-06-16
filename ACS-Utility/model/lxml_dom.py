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

    def inner_text(self) -> str:
        return str(self.raw_dom.text_content())

    def attribute(self, key: str, default: any) -> any:
        return self.raw_dom.get(key, default=default)

    def outer_html(self) -> str:
        return lxml.html.tostring(self.raw_dom, encoding="UTF-8").decode('UTF-8')

    def inner_html(self) -> str:
        # 参考：https://www.imgless.com/article/112.html
        html_text = self.outer_html()
        p_begin = html_text.find('>') + 1
        p_end = html_text.rfind('<')
        return html_text[p_begin: p_end]
