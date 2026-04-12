from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Generator
from urllib.parse import urlparse
from urllib.request import urlretrieve

from scripts.core.constants import DOCS_ROOT, MODPACK_ROOT, REPO_ROOT, TEMP_FILE_ROOT


@dataclass
class SourceFile:
    path: Path | None = field(init=False)

    @property
    def extension(self) -> str:
        return self.path.suffix.lower()

    @property
    def stem(self) -> str:
        return self.path.stem


@dataclass
class ModpackFile(SourceFile):
    rel_path: Path | str

    def __post_init__(self) -> None:
        if isinstance(self.rel_path, str):
            self.rel_path = Path(self.rel_path)
        self.path = MODPACK_ROOT / self.rel_path


@dataclass
class GitRawFile(SourceFile):
    url: str
    rel_path: str | Path | None = None

    def __post_init__(self) -> None:
        if not self.rel_path:
            self.rel_path = Path(urlparse(self.url).path).name

    def get_file(self) -> SourceFile:
        TEMP_FILE_ROOT.mkdir(parents=True, exist_ok=True)
        path_str, _ = urlretrieve(self.url, TEMP_FILE_ROOT / self.rel_path)
        self.path = Path(path_str)
        return self

    def delete_file(self) -> None:
        self.path.unlink(missing_ok=True)


@dataclass
class ModpackDirectory:
    rel_path: Path | str
    path: Path = field(init=False)

    def __post_init__(self) -> None:
        if isinstance(self.rel_path, str):
            self.rel_path = Path(self.rel_path)
        self.path = MODPACK_ROOT / self.rel_path

    def get_files(self) -> Generator[ModpackFile, Any, None]:
        for root, _, files in self.path.walk():
            for file in files:
                yield ModpackFile(rel_path=(root / file).relative_to(MODPACK_ROOT))


@dataclass
class ConfigDocument:
    title: str
    source_type: str
    content: dict[str, Any]
    raw_text: str | None = None


@dataclass
class MarkdownPage:
    title: str
    description: str
    rel_output_path: Path | str
    content: str

    def __post_init__(self) -> None:
        self.full_text = f"# {self.title}\n\n{self.description}\n\n---\n\n{self.content}"
        if isinstance(self.rel_output_path, str):
            self.rel_output_path = Path(self.rel_output_path)
        if not (path := self.rel_output_path).suffix:
            self.rel_output_path = path.with_name(f"{path.name}.md")
        self.output_path = DOCS_ROOT / self.rel_output_path

    def write_to_file(self) -> None:
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.output_path.write_text(self.full_text, encoding="utf-8")
