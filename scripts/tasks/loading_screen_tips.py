from scripts.core.entities import MarkdownPage, ModpackDirectory
from scripts.core.parsers import JsonParser
from scripts.core.wiki_builder import WikiBuildTask


class LoadingScreenTips(WikiBuildTask):
    source_directory = ModpackDirectory(rel_path="kubejs/assets/cottagewitch/tips/")
    destination = "generated/all_loading_screen_tips.md"

    def __init__(self) -> None:
        """Initialize transient state used during a run."""
        self.tip_list: list[str] = []
        self.document = ""

    def prepare_data(self) -> None:
        """Collect loading screen tip text from source files."""
        self.tip_list = self.__build_tip_list_from_files()

    def render_output(self) -> None:
        """Render the final markdown document."""
        self.document = self.__build_document_from_tip_list(self.tip_list)

    def write_output(self) -> None:
        """Write the rendered document to the destination page."""
        MarkdownPage(
            title="All loading screen tips!",
            description="A compiled list of all **loading screen tips**{.gold} in the modpack. See if you recognise any!",
            content=self.document,
            rel_output_path=self.destination,
        ).write_to_file()

    def __build_tip_list_from_files(self) -> list[str]:
        """Build the list of tip texts from the files in the directory."""
        return [JsonParser().parse(tip_file).content["tip"]["text"] for tip_file in self.source_directory.get_files()]

    def __build_document_from_tip_list(self, tip_list: list[str]) -> str:
        """Build the Markdown document from the list of tip texts."""
        return "\n\n---\n\n".join(tip_list)
