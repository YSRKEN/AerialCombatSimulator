from typing import Union

import lxml.html

from model.i_dom import Dom
from model.lxml_dom import LxmlDom
from service.http import HttpService
from service.i_dom import DomService


class LxmlDomService(DomService):
    def __init__(self, https: HttpService):
        self.https = https

    def create_dom_from_url(self, url: str, encoding: str = 'UTF-8') -> Union[None, Dom]:
        return LxmlDom(lxml.html.fromstring(self.https.read_text_from_url(url, encoding)))
