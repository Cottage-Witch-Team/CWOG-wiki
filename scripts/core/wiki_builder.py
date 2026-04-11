from pathlib import Path


class WikiBuildTask:
    destination: Path

    def launch(self) -> None:
        pass

    def write_document_to_destination(self, text: str) -> None:
        """Write the given text to the destination."""
        self.destination.write_text(text)

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
