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
    quest_book = {}

    def launch(self):

        shutil.rmtree(self.destination, ignore_errors=True)

        self.build_quest_book()

        for chapter_group_title, chapter_group in sorted(self.quest_book.items(), key=self.ordinal_sort):
            print(chapter_group_title + "\n---\n")
            print(chapter_group)
            for chapter_title, chapter in sorted(chapter_group.items(), key=self.ordinal_sort):
                if chapter_title == "ordinal":
                    continue
                print(chapter_title + "\n---")
                print(chapter)
                for quest_title, quest in sorted(chapter.items(), key=self.ordinal_sort):
                    if quest_title == "ordinal":
                        continue
                    print(quest_title)
                    print(quest)
                    path_to_write = (
                        self.destination
                        / slugify(chapter_group_title, "_")
                        / slugify(chapter_title, "_")
                        / slugify(quest_title, "_")
                    )
                    self.write_document_to_path(quest["text"], path_to_write)

    @staticmethod
    def ordinal_sort(x):
        if x[0] == "ordinal":
            return 0
        return x[1].get("ordinal") + 1

    def build_quest_book(self) -> None:
        self.quest_book = {}

        chapters = self._build_chapter_dict_from_files()

        for chapter_title, chapter in chapters.items():
            chapter_title = chapter_title.replace("__", "_and_")
            chapter_group, group_ordinal = self.__get_chapter_group(chapter)

            chapter_quests = chapter["quests"]
            chapter_ordinal = chapter["order_index"]

            if chapter_group not in self.quest_book:
                self.quest_book[chapter_group] = {"ordinal": group_ordinal}
            if chapter_title not in self.quest_book[chapter_group]:
                self.quest_book[chapter_group][chapter_title] = {"ordinal": chapter_ordinal}

            for i, quest in enumerate(chapter_quests):
                quest_is_secret = quest.get("secret")
                if not quest_is_secret:
                    quest_title, quest_text = self._process_quest_to_string(quest)
                    quest_title = quest_title or chapter_title

                    if not quest_text:
                        continue

                    if quest_title not in self.quest_book[chapter_group][chapter_title]:
                        self.quest_book[chapter_group][chapter_title][quest_title] = {
                            "ordinal": i,
                            "text": "",
                        }

                    self.quest_book[chapter_group][chapter_title][quest_title]["text"] += quest_text

    def _build_chapter_dict_from_files(self) -> dict:
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

        quest_title = title_array[0]
        quest_subtitle = f"\n>  {title_array[-1]}\n" if len(title_array) > 1 else ""
        quest_description = self.__convert_description_to_string(new_dict["description"])

        return (
            quest_title,
            f"""
# {quest_title}
{quest_subtitle}
---
{quest_description}
            """,
        )

    def __get_chapter_group(self, chapter: dict) -> tuple[str, int] | None:
        group_code = chapter["group"]

        chapter_group_file = MODPACK_ROOT / "config/ftbquests/quests/chapter_groups.snbt"

        with chapter_group_file.open("r", encoding="utf8") as f:
            chapter_group_map = snbt_to_dict(f)["chapter_groups"]

        for i, group in enumerate(chapter_group_map):
            if group_code == group["id"]:
                return slugify(group["title"], "_"), i
        return None

    def __convert_description_to_string(self, desc: list[str]) -> str:
        """Convert the description to string."""
        return "\n".join(desc)

    @staticmethod
    def __item_to_string(item: str) -> str | None:
        """Convert the item to string."""
        if not item:
            return None
        return item.rsplit(":", maxsplit=1)[-1].replace("_", " ").title()

    @staticmethod
    def __advancement_to_string(advancement: str) -> str | None:
        """Convert the advancement to string."""
        if not advancement:
            return None
        return advancement.rsplit("/", maxsplit=1)[-1].replace("_", " ").title()


Quests().launch()
