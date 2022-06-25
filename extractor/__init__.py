#!/usr/bin/python
from __future__ import annotations
import sys
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError
import requests


def _get_bs_document(link: str) -> BeautifulSoup | None:
    try:
        req = requests.get(link)
        if req.status_code == 200:
            return BeautifulSoup(req.text, "html.parser")
        if req.status_code // 100 == 4:
            raise ValueError("Bad Request. Has the post/account been deleted or made private?")
        req.raise_for_status()
    except HTTPError as err:
        _print_err("Server is acting strange. Is the service available?", err)
    except ConnectionError as err:
        _print_err("Cannot reach the internet. Check your internet connection.", err)
    except TimeoutError as err:
        _print_err("Request timed out. Bad internet connection?", err)
    return None


def _print_err(message, error):
    print(message)
    print("The error message below may give you (or someone else) a clue.")
    print(error)
    sys.exit()


def _tag_attr(tag, attr):
    return tag[attr] if tag.has_attr(attr) else None
