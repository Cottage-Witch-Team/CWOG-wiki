import shutil
from dataclasses import dataclass
from pathlib import Path

from scripts.core.constants import DOCS_ROOT, MODPACK_ROOT


def create_table_base(cols: dict[str, str]) -> str:
    """Create a str table base for use in Markdown.

    >>> print( create_table_base({'a':"l", 'b':"c", 'c':"r"}) )
    | a | b | c |
    | :-- | :-: | --: |
    """
    alignment = {"l": ":--", "c": ":-:", "r": "--:"}

    column_names = cols.keys()
    column_alignment = [alignment[v] for v in cols.values()]

    line_1 = f"| {' | '.join(column_names)} |"
    line_2 = f"| {' | '.join(column_alignment)} |"

    return f"{line_1}\n{line_2}"


def create_table_row(*args: str) -> str:
    """Create a str table row for use in Markdown.

    >>> create_table_row("abc", "def", "ghi")
    '| abc | def | ghi |'
    """
    return f"| {' | '.join(args)} |"


def item_to_string(item: str) -> str | None:
    """Convert the item to string.

    >>> item_to_string("minecraft:chicken_nugget")
    'Chicken Nugget'
    """
    return _thing_to_string(item, [":"])


def tag_to_string(item: str) -> str | None:
    """Convert the item to string.

    >>> tag_to_string("minecraft:cheese/chicken_nugget")
    'Chicken Nugget'
    """
    return _thing_to_string(item, [":", "/"])


def advancement_to_string(advancement: str) -> str | None:
    """Convert the advancement to string.

    >>> advancement_to_string("minecraft:fun/get_chicken_nugget")
    'Get Chicken Nugget'
    """
    return _thing_to_string(advancement, [":", "/"])


def _thing_to_string(thing: str, sep: list[str]) -> str:
    if not thing:
        return None
    for s in sep:
        thing = thing.rsplit(s, maxsplit=1)[-1]
    return thing.replace("_", " ").title()


@dataclass
class ImageRegistry:
    rel_source_root: str | Path
    asset_root: Path = DOCS_ROOT / "assets"

    def __post_init__(self) -> None:
        self.source_root = MODPACK_ROOT / self.rel_source_root
        self.asset_root.mkdir(parents=True, exist_ok=True)

    def process_image(self, rel_path: str | Path) -> str:
        rel_path = Path(rel_path)

        source_path = self.source_root / rel_path
        if not source_path.exists():
            return f"<!-- missing image: {source_path} -->"

        destination_path = self.asset_root / rel_path
        destination_path.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(source_path, destination_path)

        return f"![{rel_path.name}](/assets/{rel_path.as_posix()})"
