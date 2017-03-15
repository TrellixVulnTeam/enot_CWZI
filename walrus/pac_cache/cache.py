import shlex
import subprocess
from abc import ABC, abstractmethod
from enum import Enum

from walrus.packages import Package


class CacheType(Enum):
    LOCAL = 'local'
    ARTIFACTORY = 'artifactory'
    S3 = 's3'


class Cache(ABC):
    temp_dir = ""
    path = ""
    erlang_version = None

    def __init__(self, temp_dir, path):
        self.erlang_version = Cache.get_erlang_version()
        self.temp_dir = temp_dir
        self.path = path

    @abstractmethod
    def exists(self, package: Package):
        pass

    @abstractmethod
    def fetch_package(self, package: Package):
        pass

    @abstractmethod
    def get_package(self, package: Package):
        pass

    @abstractmethod
    def add_package(self, package: Package, rewrite: bool):
        pass

    def link_package(self, package: Package, path: str):
        pass

    @staticmethod
    def get_erlang_version():
        proc = subprocess.run(
            shlex.split("erl -eval 'erlang:display(erlang:system_info(otp_release)), halt().' -noshell"),
            stdout=subprocess.PIPE)
        if proc.returncode == 0:
            version = proc.stdout.decode('utf-8').strip()
            return version.translate({ord(c): None for c in '"'})
        else:
            print("Can't get erlang version")  # TODO handle error
            return None
