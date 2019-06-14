from typing import Union

from model.i_dom import Dom
from model.lxml_dom import LxmlDom
from service.i_dom import DomService

import requests
import lxml.html


class LxmlDomService(DomService):
    def create_dom_from_url(self, url: str, encoding: str = 'UTF-8') -> Union[None, Dom]:
        response = requests.get(url)
        if not response.ok:
            return None
        response.encoding = encoding
        html_text = response.text
        return LxmlDom(lxml.html.fromstring(html_text))
