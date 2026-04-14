from abc import ABC, abstractmethod
from pathlib import Path


class WikiBuildTask(ABC):
    destination: Path

    def run(self) -> None:
        self.prepare_data()
        self.render_output()
        self.write_output()

    @abstractmethod
    def prepare_data(self) -> None:
        pass

    @abstractmethod
    def render_output(self) -> None:
        pass

    @abstractmethod
    def write_output(self) -> None:
        pass

    def write_document_to_destination(self, text: str) -> None:
        """Write the given text to the destination."""
        self.destination.write_text(text, encoding="utf-8")

    def write_document_to_path(
        self,
        text: str,
        file_path: Path,
    ) -> None:
        """Write the given text to the destination directory."""
        if not file_path.parent.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch()
        file_path.write_text(text, encoding="utf8")
