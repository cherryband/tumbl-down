import os
import unittest

from pathlib import Path

from common import debug_out
from common.downloader import request_download, _resolve_path

DOWNLOAD_DIR = ".downloads_test_DO_NOT_USE"
DOWNLOAD_FILENAME = "test_download"
DOWNLOAD_PATH = f"{DOWNLOAD_DIR}/{DOWNLOAD_FILENAME}"


class UtilTest(unittest.TestCase):
    # noinspection SpellCheckingInspection
    def test_request_download(self):
        self.clear_test_dir()  # remove before test in case of abnormal exit

        request_download("http://us.archive.ubuntu.com/ubuntu/project/ubuntu-archive-keyring.gpg",
                         path_dir=DOWNLOAD_DIR, filename=DOWNLOAD_FILENAME)

        self.assertTrue(os.path.exists(DOWNLOAD_PATH))

        with open(DOWNLOAD_PATH, 'rb') as testfile:
            testfile.seek(0, os.SEEK_END)
            filesize = testfile.tell()
            debug_out(f"File size: {filesize} bytes")

            self.assertGreater(filesize, 16)  # very unlikely that a valid gpg file is 16 bytes or fewer

        self.clear_test_dir()  # remove after test to prevent accidental use

    def clear_test_dir(self):
        if os.path.exists(DOWNLOAD_PATH):
            os.remove(DOWNLOAD_PATH)
        if os.path.exists(DOWNLOAD_DIR):
            os.rmdir(DOWNLOAD_DIR)
    
    def test_resolve_path(self):
        self.assertEqual(_resolve_path("~/asdf"), str(Path.home() / "asdf"))
        self.assertEqual(_resolve_path("/we/ee"), "/we/ee")
        self.assertEqual(_resolve_path("asdf"), str(Path.cwd() / "asdf"))
