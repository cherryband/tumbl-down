#!/usr/bin/python
"""module with common helper functions"""

from __future__ import annotations

import dataclasses
import os
import sys
import time
import traceback
from typing import Optional

import requests
from bs4 import BeautifulSoup
from requests import Response
from requests.exceptions import HTTPError

from common import history

DEBUG = False

@dataclasses.dataclass
class File:
    """Data class for downloadable files"""
    _id: str
    link: str
    modtime: int
    name: str = None

    def get_filename(self):
        if not self.name:
            return self.link.split("/")[-1]
        return self.name


def get_bs_document(url: str, params: Optional[dict] = None, **options) -> BeautifulSoup | None:
    """
    Helper function for querying the web with error handling.
    :param url: destination URL
    :param params: optional URL parameters; default None
    :return: BeautifulSoup object, or None when unsuccessful
    """
    req = request_get(url, params, **options)
    if req.status_code == 200:
        return BeautifulSoup(req.text, "html.parser")
    if req.status_code // 100 == 4:
        raise ValueError("Bad Request. Is the spelling correct? "
                         "Are the post and the account public?")
    return None


def get_extension(file: str) -> str:
    filename = file.split('/')[-1]
    ext = filename.split('.')[-1]
    if ext:
        return f".{ext}"
    return ""


def debug_out(message: str) -> None:
    if DEBUG:
        print(message)


def request_get(url: str, params: Optional[dict] = None, **options) -> Optional[Response]:
    """
    Helper function for querying the web with error handling.
    :param url: destination URL
    :param params: optional URL parameters; default None
    :return: Response object, or None when unsuccessful
    """
    req = None
    debug_out(f"request url: {url}, params: {params}")
    try:
        req = requests.get(url, params, **options, timeout=60,
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:114.0)'
                   ' Gecko/20100101 Firefox/114.0'})
        if req.status_code // 100 == 5:
            req.raise_for_status()
        elif req.status_code // 100 == 4:
            raise ValueError("Bad Request. Is the spelling correct? "
                             "Are the post and the account public?")
    except HTTPError as err:
        _print_err("Server is acting strange. Is the service available?", err)
    except ConnectionError as err:
        _print_err("Cannot reach the internet. Check your internet connection.", err)
    except TimeoutError as err:
        _print_err("Request timed out. Bad internet connection?", err)
    return req


def _print_err(message, error):
    print(message)
    print("The error message below may give you (or someone else) a clue.")
    traceback.print_exc()
    sys.exit()


def tag_attr(tag, attr):
    """
    None-safe function for querying attributes in a tag
    :param tag: list-like object to query attributes
    :param attr: name of the attribute
    :return: the attribute value, or None
    """
    return tag[attr] if tag.has_attr(attr) else None
