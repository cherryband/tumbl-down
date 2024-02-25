"""Main module; provides user-facing interface to the software"""
import argparse
import csv
from pathlib import Path
from random import sample

import common
import service
from common import debug_out
from common.downloader import download_from_feed

SERVICES = service.index_services()

def cmd_main(args):
    """
    tumbl-down main function; program entry point
    :param args: parsed arguments by ArgumentParser
    """
    service_type = args.service
    debug_out(f"Service type: {service_type}")
    common.DEBUG = args.verbose
    if service_type == 'update':
        update_main()
        return
    if not args.account_id:
        print("No accounts specified. Add account handles to download.")
    for i, account in enumerate(args.account_id):
        print(f"Fetching feed of {account}..."
              f" ({i+1}/{len(args.account_id)})")
        download_from_feed(SERVICES[service_type], account, f"downloads/{account}",
                           post_count=args.posts, redownload=args.force)


def _init_argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")
    parser.add_argument("-f", "--force", help="re-download already downloaded"
                        " images", action="store_true")
    parser.add_argument("-n", "--posts", type=int, default=20,
                        help="specify number of posts to query")
    parser.add_argument("service", help="type of service to use")
    parser.add_argument("account_id",
                        help="the account ID(s) to download images from",
                        nargs='*')
    return parser

def _read_config(filename: str = "config.csv", path: str = '.') -> list[list]:
    filepath = Path(path)/filename
    if filepath.exists():
        config_list = []
        with filepath.open(newline='') as f:
            for row in csv.reader(f, delimiter=','):
                config_list.append(row)
            return sample(config_list, len(config_list))
    print("config.csv not found. Please create the file first.")
    return []

def update_main():
    """Function that executes pre-programmed list of downloads."""
    configs = _read_config()
    for i, config in enumerate(configs):
        account, service, dl_path, incl_reblog = [x.strip() for x in config]
        print(f"Fetching feed of {account}... ({i+1}/{len(configs)})")
        download_from_feed(SERVICES[service], account, dl_path, post_count=args.posts, redownload=args.force)

if __name__ == "__main__":
    parser = _init_argparser()
    args = parser.parse_args()
    cmd_main(args=args)
