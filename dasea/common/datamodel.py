import io
import csv
from enum import Enum
from dataclasses import dataclass


class Kind(Enum):
    BUILD = 1
    RUN = 2
    TEST = 3
    DEV = 4
    LIB = 5
    FETCH = 6
    EXTRACT = 7
    PATCH = 8
    MY = 9
    RECOMMEND = 10
    OPTIONAL = 11
    CONFLICTS = 12
    USES_FROM_MACOS = 13
    USES_FROM_MACOS_BUILD = 14
    USES_FROM_MACOS_TEST = 15
    NORMAL = 16  # Kind of dependency in Cargo
    DOC = 17


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


# TODO: Make fields optional, e.g., via Optional[str]
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
