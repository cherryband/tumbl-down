#!/usr/bin/python

from importlib.util import spec_from_file_location, module_from_spec
from os import path, listdir

SERVICES = ()
DEFAULT_SERVICES_PATH = "service"
BASE_DIR = path.join(path.dirname(path.realpath(__file__)), "..")


def index_services():
    services_path = _abs_path(DEFAULT_SERVICES_PATH)
    return {
        (name := _get_name(service)): _load_module(name, filepath)
        for service in listdir(services_path)
        if path.isfile(filepath := _abs_path(service, services_path))
        and service.endswith(".py")
    }


def _load_module(name, mod_path):
    spec = spec_from_file_location(name, mod_path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _get_name(filename):
    return filename.removesuffix(".py")


def _abs_path(relpath, base=BASE_DIR):
    return path.join(base, relpath)
