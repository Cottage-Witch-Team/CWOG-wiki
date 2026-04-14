import re

from scripts.core.entities import GitRawFile, MarkdownPage, ModpackFile
from scripts.core.markdown_funcs import create_table_base, create_table_row
from scripts.core.parsers import JsonParser, JsParser
from scripts.core.wiki_builder import WikiBuildTask


class AE2RenameTask(WikiBuildTask):
    ae2_base_names_source = GitRawFile(
        url="https://raw.githubusercontent.com/AppliedEnergistics/Applied-Energistics-2/refs/heads/main/src/generated/resources/assets/ae2/lang/en_us.json",
        rel_path="ae2_item_names.json",
    )
    ae2_renames_source = ModpackFile(rel_path="kubejs/assets/ae2/lang/en_us.json")
    kjs_globals_source = ModpackFile(rel_path="kubejs/startup_scripts/globals/global_consts.js")

    def __init__(self) -> None:
        """Initialize transient state used during a run."""
        self.diff: dict[str, dict[str, str | bool]] = {}
        self.file_content = ""

    def prepare_data(self) -> None:
        ae2_renames = JsonParser().parse(self.ae2_renames_source).content
        ae2_base_names = JsonParser().parse(self.ae2_base_names_source.get_file()).content
        self.ae2_base_names_source.delete_file()
        name_diff = self.__diff_names(ae2_base_names, ae2_renames)

        ae2_disabled_items = set(
            JsParser().parse(self.kjs_globals_source, get_list="global.ae2_disabled_items").content["list"],
        )

        self.diff = {
            item_id: names_map | {"enabled": item_id not in ae2_disabled_items}
            for item_id, names_map in name_diff.items()
        }

    def render_output(self) -> None:
        table = create_table_base({"Item ID": "l", "Original Name": "r", "New Name": "l", "Enabled?": "c"})

        for item_id, data in self.diff.items():
            old_name = data["old_name"]
            new_name = data["new_name"]
            item_disabled = not data["enabled"]

            item_id_str = f"`{item_id}`"
            old_name_str = f"~~{old_name}~~" if item_disabled else old_name
            new_name_str = f"~~{new_name}~~" if item_disabled else f"**{new_name}**"
            enabled_str = ":lucide-x:{.red}" if item_disabled else ":lucide-check:{.green}"

            table += "\n" + create_table_row(item_id_str, old_name_str, new_name_str, enabled_str)

        self.file_content = table

    def write_output(self) -> None:
        MarkdownPage(
            title="AE2 - Renamed Items",
            description="Many of the items in AE2 have been renamed to a more magical vibe. See a list of those here!",
            content=self.file_content,
            rel_output_path="generated/ae2_renames.md",
        ).write_to_file()

    def __diff_names(self, base_name_map: dict[str, str], new_name_map: dict[str, str]) -> dict[str, dict[str, str]]:
        return {
            re.sub(
                r"(?:item|block)\.([^.]+)\.(.+)",
                r"\1:\2",
                item_path,
            ): {"old_name": base_name, "new_name": new_name}
            for item_path, base_name in base_name_map.items()
            if (new_name := new_name_map.get(item_path)) is not None
            and new_name != base_name
            and (re.search(r"^(?:item|block)\.", item_path))
        }
