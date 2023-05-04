#!/usr/bin/python
from __future__ import annotations

import dataclasses
import os
from os import path
import sys
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup
from requests import Response
from requests.exceptions import HTTPError

DEBUG = False


def get_bs_document(url: str, params: Optional[dict] = None, **options) -> BeautifulSoup | None:
    req = request_get(url, params, **options)
    if req.status_code == 200:
        return BeautifulSoup(req.text, "html.parser")
    if req.status_code // 100 == 4:
        raise ValueError("Bad Request. Has the post/account been deleted or made private?")
    return None


def get_extension(file: str):
    return "." + file.split('.')[-1]


def debug_out(message: str) -> None:
    if DEBUG:
        print(message)


def request_get(url: str, params: Optional[dict] = None, **options) -> Optional[Response]:
    req = None
    try:
        req = requests.get(url, params, **options, timeout=10)
        if req.status_code // 100 == 5:
            req.raise_for_status()
        elif req.status_code // 100 == 4:
            raise ValueError("Bad Request. Is the account ID correct?")
    except HTTPError as err:
        _print_err("Server is acting strange. Is the service available?", err)
    except ConnectionError as err:
        _print_err("Cannot reach the internet. Check your internet connection.", err)
    except TimeoutError as err:
        _print_err("Request timed out. Bad internet connection?", err)
    return req


def request_download(url: str, path_dir: str, filename: str,
                     modified: float = None, **options) -> None:
    if options is None:
        options = {}

    debug_out(f'Downloading "{url}" to {path_dir}')
    if not path.exists(path_dir):
        debug_out('Target Directory Does Not Exist; Create')
        os.mkdir(path_dir)

    filepath = path.join(path_dir, filename)
    debug_out(f'Complete File Path: {filepath}')

    if path.exists(filepath):
        debug_out('File exists; Skipping...')
        return

    req = request_get(url, stream=True)
    debug_out('Connection Established.')
    with open(filepath, "xb+") as dest:
        debug_out('Downloading...')
        for chunk in req.iter_content(chunk_size=8192):
            dest.write(chunk)

    debug_out('Download Finished.')
    if modified:
        os.utime(filepath, (time.time(), modified))
        debug_out(f'Set Modified Time to Timestamp: {modified}')


def _print_err(message, error):
    print(message)
    print("The error message below may give you (or someone else) a clue.")
    print(error)
    sys.exit()


def tag_attr(tag, attr):
    return tag[attr] if tag.has_attr(attr) else None


@dataclasses.dataclass
class File:
    link: str
    modtime: str
    name: str = None

    def get_filename(self):
        if not self.name:
            return self.link.split("/")[-1]
        return self.name
