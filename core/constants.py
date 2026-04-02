from pathlib import Path
from typing import Final

REPO_ROOT: Final[Path] = Path(__file__).parent.parent
MODPACK_ROOT: Final[Path] = REPO_ROOT / "repo_code"
DOCS_ROOT: Final[Path] = REPO_ROOT / "docs"
