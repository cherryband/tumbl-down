#!/usr/bin/python
from __future__ import annotations
from bs4 import BeautifulSoup
from util.__init__ import request_get


def _get_bs_document(link: str) -> BeautifulSoup | None:
    req = request_get(link)
    if req.status_code == 200:
        return BeautifulSoup(req.text, "html.parser")
    if req.status_code // 100 == 4:
        raise ValueError("Bad Request. Has the post/account been deleted or made private?")
    return None
