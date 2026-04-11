import json
from collections.abc import Generator
from io import TextIOWrapper
from pathlib import Path

import ftb_snbt_lib as slib


def get_all_files(path: Path) -> Generator[Path, None, None]:
    """Get path for all files in a directory."""
    for root, _, files in path.walk():
        for file in files:
            yield root / file
