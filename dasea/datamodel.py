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
    # platform: str


@dataclass
class Version(Persistent):
    idx: int
    pkg_idx: int
    name: str  # Added compared to RP paper
    version: str
    license: str
    description: str
    homepage: str  # Called HomepageURL in RP paper
    repository: str  # Called SourceCodeURL in RP paper
    author: str
    maintainer: str


@dataclass
class Dependency(Persistent):
    pkg_idx: int  # Called ID in RP paper
    source_idx: int
    target_idx: int
    source_name: str  # Added compared to RP paper
    target_name: str  # Added compared to RP paper
    source_version: str  # Added compared to RP paper
    target_version: str  # Added compared to RP paper
    kind: Kind  # Called Type in RP paper
