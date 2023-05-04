import argparse

import common
import service
from common import File, request_download, debug_out

services = service.index_services()


def download_files(files: list[File], download_path):
    """
    Helper function for downloading multiple files
    :param files: list of files to download
    :param download_path: path to save
    :return:
    """
    file_count = len(files)
    for i, file in enumerate(files):
        print("\r", end='')
        print(f"Downloading files... ({i+1}/{file_count})", end='')
        request_download(
            file.link, download_path, file.name, modified=float(file.modtime)
        )
    print()
    print(f"{file_count} files downloaded.")


def oneshot(service_type, acct_id, download_path, post_id):
    """
    Parses and downloads images from a single post
    :param service_type: parser/service to use
    :param acct_id: account identifier
    :param download_path: path to download
    :param post_id: post identifier
    :return:
    """
    _service = services[service_type]
    files = _service.parse_post(acct_id, post_id)
    download_files(files, download_path)


def download_from_feed(service_type, acct_id, download_path, post_count=20, offset=0):
    """
    Parses and download images from recent feed
    :param service_type: parser/service to use
    :param acct_id: account identifier
    :param download_path: path to download
    :param post_count: number of posts to download; default = 20
    :param offset: number of most recent posts to skip; default = 0
    :return:
    """
    _service = services[service_type]
    feed = _service.get_recent_posts(acct_id, post_count, offset)
    files = []
    print("Searching posts...", end="")
    for i, post in enumerate(feed):
        print("\r", end="")
        files.extend(_service.extract_images(acct_id, post))
        print(f"Searching {i+1} out of {len(feed)} posts..."
              f" ({len(files)} image(s) collected)", end="")

    print(" OK.")
    download_files(files, download_path)


def main(args):
    """
    tumbl-down main function; program entry point
    :param args: parsed arguments by ArgumentParser
    :return:
    """
    service_type = args.service
    debug_out(f"Service type: {service_type}")
    common.DEBUG = args.verbose
    for i, account in enumerate(args.account_id):
        print(f"Fetching feed of {account}..."
              f" ({i+1}/{len(args.account_id)})")
        download_from_feed(service_type, account, account,
                           post_count=args.posts, offset=args.offset)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")
    parser.add_argument("-n", "--posts", type=int, default=20,
                        help="specify number of posts to query")
    parser.add_argument("--offset", type=int, default=0,
                        help="specify offset of posts to query")
    parser.add_argument("--date-after", help="only download ")
    parser.add_argument("service", help="type of service to use")
    parser.add_argument("account_id",
                        help="the account ID or IDs to download images from",
                        nargs='+')
    main(args=parser.parse_args())
