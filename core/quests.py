import pprint
import shutil
from string import capwords

from constants import DOCS_ROOT, MODPACK_ROOT
from functions import get_all_files, snbt_to_dict
from markdown.extensions.toc import slugify
from wiki_builder import WikiBuildTask


class Quests(WikiBuildTask):
    source_directory = MODPACK_ROOT / "config/ftbquests/quests/chapters"
    destination = DOCS_ROOT / "quests"

    def launch(self):

        shutil.rmtree(self.destination, ignore_errors=True)

        chapters = self._build_chapter_dict_from_files()

        for chapter_title, chapter in chapters.items():
            print(chapter_title)

            chapter_group = self.__get_chapter_group(chapter)
            print(chapter_group)

            for q in chapter["quests"]:
                if not q.get("secret"):
                    quest_title, text = self._process_quest_to_string(q)

                    if not quest_title or not text:
                        continue

                    self.write_document_to_destination_directory(
                        text,
                        (
                            self.destination
                            / (chapter_group + chapter_title).lower().replace(" ", "_")
                            / (slugify(quest_title, "_") + ".md")
                        ),
                    )

    def _build_chapter_dict_from_files(self):
        chapters = {}
        for chapter in get_all_files(self.source_directory):
            with chapter.open("r", encoding="utf8") as f:
                chapters[chapter.stem] = snbt_to_dict(f)
        return chapters

    def _process_quest_to_string(self, quest: dict) -> tuple[str | None, str | None]:

        new_dict = {
            "title": quest.get("title"),
            "subtitle": quest.get("subtitle"),
            "description": quest.get("description"),
            "item": quest.get("tasks")[0].get("item"),
            "advancement": quest.get("tasks")[0].get("advancement"),
            "to_observe": quest.get("tasks")[0].get("to_observe"),
            "task_title": quest.get("tasks")[0].get("title"),
        }

        if isinstance(new_dict["item"], dict) and "id" in new_dict["item"]:
            new_dict["item"] = new_dict["item"]["id"]
        if isinstance(new_dict["description"], str):
            new_dict["description"] = [new_dict["description"]]
        if not new_dict["description"]:
            return None, None

        title_array = [
            capwords(thing)
            for thing in [
                new_dict["title"],
                new_dict["task_title"],
                self.__advancement_to_string(new_dict["advancement"]),
                self.__item_to_string(new_dict["item"]),
                self.__item_to_string(new_dict["to_observe"]),
                new_dict["subtitle"],
            ]
            if thing
        ]

        if not title_array or not new_dict["description"]:
            return None, None

        print(title_array[0], new_dict["description"][0])
        return (
            title_array[0],
            f"""
# {title_array[0]}

{"> " + title_array[-1] if len(title_array) > 1 else ""}

---
{"\n".join(new_dict["description"])}

            """,
        )

    def __get_chapter_group(self, chapter: dict) -> dict:
        group_code = chapter["group"]

        chapter_group_file = MODPACK_ROOT / "config/ftbquests/quests/chapter_groups.snbt"

        with chapter_group_file.open("r", encoding="utf8") as f:
            chapter_group_map = snbt_to_dict(f)["chapter_groups"]

        for group in chapter_group_map:
            if group_code == group["id"]:
                return group["title"] + "/"
        return None

    def __convert_description_to_string(self, desc: list[str]) -> str:
        """Convert the description to string."""
        return "\n".join(desc)

    @staticmethod
    def __item_to_string(item: str):
        if not item:
            return None
        return item.rsplit(":", maxsplit=1)[-1].replace("_", " ").title()

    def __advancement_to_string(self, advancement: str):
        if not advancement:
            return None
        return advancement.rsplit("/", maxsplit=1)[-1].replace("_", " ").title()


Quests().launch()
