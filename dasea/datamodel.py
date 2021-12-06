import io
import csv
from enum import Enum
from dataclasses import dataclass


class Kind(Enum):
    BUILD = 1
    RUN = 2
    TEST = 3
    DEV = 4


class Persistent:
    # TODO: Figure out where the return newline comes from
    def to_csv(self) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(self.__dict__.values())
        return output.getvalue().rstrip()

    def to_csv_header(self) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(self.__dict__.keys())
        return output.getvalue().rstrip()


@dataclass
class Package(Persistent):
    idx: int
    name: str
    pkgman: str
    platform: str


@dataclass
class Version(Persistent):
    idx: int
    pkg_idx: int
    name: str
    version: str
    license: str
    description: str
    homepage: str
    repository: str
    author: str
    maintainer: str


@dataclass
class Dependency(Persistent):
    pkg_idx: int
    source_idx: int
    target_idx: int
    source_name: str
    target_name: str
    source_version: str
    target_version: str
    kind: Kind
