from pathlib import Path


class WikiBuildTask:
    destination: Path

    def launch(self) -> None:
        pass

    def write_document_to_destination(self, text: str) -> None:
        """Write the given text to the destination."""
        self.destination.write_text(text)

    def write_document_to_destination_directory(
        self,
        text: str,
        file_path: str,
    ) -> None:
        """Write the given text to the destination directory."""
        path = self.destination / file_path
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
        path.write_text(text, encoding="utf8")
