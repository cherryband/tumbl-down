import fractions
import sys
import os.path as path
from typing import Optional

import requests
from requests.exceptions import HTTPError
from requests import Response


def request_get(url: str, params: Optional[dict] = None, **options) -> Optional[Response]:
    req = None
    try:
        req = requests.get(url, params, **options)
        if req.status_code // 100 == 5:
            req.raise_for_status()
    except HTTPError as err:
        _print_err("Server is acting strange. Is the service available?", err)
    except ConnectionError as err:
        _print_err("Cannot reach the internet. Check your internet connection.", err)
    except TimeoutError as err:
        _print_err("Request timed out. Bad internet connection?", err)
    return req


def request_download(url: str, path_dir: str, filename: str, **options) -> None:
    if options is None:
        options = {}

    req = request_get(url, stream=True)
    filepath = path.join(path_dir, filename)

    with open(filepath, "xb+") as dest:
        for chunk in req.iter_content(chunk_size=8192):
            dest.write(chunk)


def _print_err(message, error):
    print(message)
    print("The error message below may give you (or someone else) a clue.")
    print(error)
    sys.exit()


def tag_attr(tag, attr):
    return tag[attr] if tag.has_attr(attr) else None
