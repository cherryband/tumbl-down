#!/usr/bin/python
import os
import time

from os import path
from typing import Optional

from common import File, debug_out, request_get, _print_err
from common import history

_HISTORY_FILENAME = '.history.csv'


def _resolve_path(path_dir: str) -> str:
    return path.abspath(path.expanduser(path_dir))


def request_download(url: str, path_dir: str, filename: str,
                     modified: float = None, **options) -> None:
    """
    Helper function for downloading file to a specified location.
    :param url: URL to file
    :param path_dir: destination directory(folder) for file download
    :param filename: name of the file, including file extension
    :param modified: UNIX timestamp of post time. default None
    """
    if options is None:
        options = {}

    path_dir = _resolve_path(path_dir)
    debug_out(f'Downloading "{url}" to {path_dir}')
    if not path.exists(path_dir):
        debug_out('Target Directory Does Not Exist; Create')
        os.makedirs(path_dir)

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

def download_files(files: list[File], download_path):
    """
    Helper function for downloading multiple files
    :param files: list of files to download
    :param download_path: path to save
    """
    for file in files:
        request_download(
            file.link, download_path, file.name, modified=float(file.modtime)
        )


def oneshot(service, acct_id, download_path, post_id,
            last_read:history.Post=None) -> Optional[tuple[int, int]]:
    """
    Parses and downloads images from a single post
    :param service: parser/service to use
    :param acct_id: account identifier
    :param download_path: path to download
    :param post_id: post identifier
    :param last_read: optional argument for limiting re-downloads
    :return: tuple of timestamp and number of files, or (0, 0) if not applicable
    """
    try:
        files = service.extract_images(acct_id, post_id)
        if not files:
            return (0, 0)

        modtime = files[0].modtime
        file_count = len(files)
        debug_out(f"Uploaded: {modtime}")
        if last_read and int(modtime) < last_read.timestamp:
            return (modtime, -1)

        download_files(files, download_path)
        return (modtime, file_count)
    except Exception as e:
        print(e)
        return (0, 0)


def download_from_feed(service, acct_id, download_path, post_count=20, redownload=False):
    """
    Parses and downloads images from recent feed
    :param service: parser/service to use
    :param acct_id: account identifier
    :param download_path: path to download
    :param post_count: number of posts to download; default = 20
    :param offset: number of most recent posts to skip; default = 0
    :param redownload: whether to re-download posts that are marked as read; default = False
    """
    debug_out(f"redownload = {redownload}")
    try:
        feed = service.get_recent_posts(acct_id, post_count)
    except ValueError:
        print(f"The ID '{acct_id}' seems to be unavailable. Skipping...")
        return
    except Exception as e:
        _print_err("This is an unexpected error; report this to the issue tracker: "
              "https://github.com/cherryband/tumbl-down/issues", e)

    file_count = 0
    with open(_HISTORY_FILENAME, 'r+', encoding='utf8') as rwriter:
        last_read = None if redownload else history.get_last_read(rwriter, service.SLUG, acct_id)
        if last_read:
            debug_out(f"Last read post id: {last_read.post_id}, timestamp: {last_read.timestamp}")
        elif not redownload:
            debug_out("No history recorded.")

        print("Searching posts...", end="")
        for i, post in enumerate(feed):
            print("\r", end="")
            if last_read and post == last_read.post_id:
                print("\nSkipping already downloaded posts"
                      "(override with -f or config file)...", end="")
                break

            modtime, dl_files = oneshot(service, acct_id, download_path, post, last_read=last_read)
            if modtime == 0:
                continue
            if dl_files < 0:
                print("\nSkipping older posts"
                      "(override with -f or config file)...", end="")
                break

            file_count += dl_files
            print(f"Searching {i+1} out of {len(feed)} posts..."
                  f" ({file_count} image(s) collected)", end="")
            history.mark_read(rwriter, history.History(service.SLUG, acct_id, post, modtime))

    print(f"\nDownloaded {file_count} file(s).")


ls = os.listdir()

if _HISTORY_FILENAME not in ls:
    with open(_HISTORY_FILENAME, 'x', encoding='utf8'):
        pass
