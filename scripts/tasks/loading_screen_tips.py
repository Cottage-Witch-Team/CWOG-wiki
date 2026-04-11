import json
from io import TextIOWrapper

from scripts.core.constants import DOCS_ROOT, MODPACK_ROOT
from scripts.core.functions import get_all_files
from scripts.core.wiki_builder import WikiBuildTask


class LoadingScreenTips(WikiBuildTask):
    source_directory = MODPACK_ROOT / "kubejs/assets/cottagewitch/tips/"
    destination = DOCS_ROOT / "wiki/all_loading_screen_tips.md"

    def launch(self) -> None:
        """Task to get all loading screen tips, and updates the wiki page."""
        tip_list = self.__build_tip_list_from_files()
        document = self.__build_document_from_tip_list(tip_list)

        self.write_document_to_destination(document)

    def __build_tip_list_from_files(self) -> list[str]:
        """Build the list of tip texts from the files in the directory."""
        tip_list = []
        for tip_file in get_all_files(self.source_directory):
            with tip_file.open("r", encoding="utf8") as f:
                tip_list.append(self.__get_tip_from_file(f))
        return tip_list

    @staticmethod
    def __get_tip_from_file(file: TextIOWrapper) -> dict[str, str]:
        """Load the tip text from the file."""
        return json.load(file)["tip"]["text"]

    def __build_document_from_tip_list(self, tip_list: list[str]) -> str:
        """Build the Markdown document from the list of tip texts."""
        tip_list_text = "\n---\n".join(tip_list)

        self.text_ = f"""
        # All loading screen tips!

        {tip_list_text}
        """
        return self.text_
