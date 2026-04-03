import re
import shutil

from constants import DOCS_ROOT, MODPACK_ROOT
from functions import get_all_files, snbt_to_dict
from markdown.extensions.toc import slugify
from wiki_builder import WikiBuildTask


class Quests(WikiBuildTask):
    source_directory = MODPACK_ROOT / "config/ftbquests/quests/chapters"
    destination = DOCS_ROOT / "quests"
    quest_book = {}
    regex_sub = {
        "l": "***",
        "b": "**",
        "c": "*",
        "d": "^^",
        "a": "*",
        "e": "**",
        "6": "==",
    }

    def launch(self):

        shutil.rmtree(self.destination, ignore_errors=True)

        self.build_quest_book()

        for chapter_group_title, chapter_group in sorted(self.quest_book.items(), key=self.ordinal_sort):
            print(f"\n\n{chapter_group_title.center(30, '-')}")
            for chapter_title, chapter in sorted(chapter_group.items(), key=self.ordinal_sort):
                if chapter_title == "ordinal":
                    continue
                print(f"\n{chapter_title.center(20, '~')}")
                for quest_title, quest in sorted(chapter.items(), key=self.ordinal_sort):
                    if quest_title == "ordinal":
                        continue
                    print(f"-> {quest_title}")
                    path_to_write = (
                        self.destination
                        / slugify(chapter_group_title, "_")
                        / slugify(chapter_title, "_")
                        / (slugify(quest_title, "_") + ".md")
                    )
                    final_text = quest["text"].replace("{@pagebreak}", "\n---\n")

                    for l, r in self.regex_sub.items():
                        final_text = re.sub(r"&" + l + "(.*?)&r", r + r"\1" + r, final_text)

                    # TODO: Images

                    self.write_document_to_path(final_text, path_to_write)

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

        tasks = self.__process_tasks_on_quest(quest)

        task_string = self.__get_task_string(tasks)

        new_dict = {
            "title": quest.get("title", self.title_from_task(tasks)),
            "subtitle": quest.get("subtitle"),
            "description": quest.get("description", [""]),
            "tasks": task_string,
        }

        title, subtitle, task, description = new_dict.values()

        if subtitle:
            subtitle = f"\n> {subtitle.capitalize()}\n"

        if task:
            task = f"\n{task}\n---\n"

        if description and isinstance(description, str):
            description = [description]
            quest_description = self.__convert_description_to_string(description)
        else:
            quest_description = ""

        return (
            title,
            f"""
# {title}
{subtitle}
---
{quest_description}
---
{task}
            """,
        )

    def __process_tasks_on_quest(self, quest: dict) -> dict | None:
        quest_tasks = quest.get("tasks")
        if not quest_tasks:
            return None

        tasks_list = {}
        for task in quest_tasks:
            task_type = task.get("type")

            task_goal = task.get(task_type, task)

            if task_type == "item":
                number = task.get("count", task["item"].get("Count", 1) if isinstance(task["item"], dict) else 1)
                number = "" if number == 1 else f" ({number})"
                task_goal = f"{self.__process_item(task_goal)}{number}"
            elif task_type == "advancement":
                task_goal = self.__advancement_to_string(task_goal)
            elif task_type == "observation":
                task_goal = self.__item_to_string(task["to_observe"])
            elif task_type == "kill":
                number = "" if task["value"] == 1 else f" ({task['value']})"
                task_goal = f"{self.__item_to_string(task['entity'])}{number}"
            elif task_type == "checkmark":
                task_goal = task.get("title")
                if not task_goal:
                    continue
            elif task_type == "questsadditions:break":
                task_type = "break"
                task_goal = self.__item_to_string(task["block"])
            elif task_type in ["structure", "biome", "dimension"]:
                task_goal = self.__tag_to_string(task_goal)
            elif task_type == "questsadditions:days":
                task_type = "survive"
                task_goal = f"{task['days']} days"
            elif task_type == "stat":
                number = "" if task["value"] == 1 else f"s {task['value']} times"
                task_goal = f"{self.__advancement_to_string(task_goal)}{number}"

            if task_type not in tasks_list:
                tasks_list[task_type] = []

            tasks_list[task_type].append(task_goal)

        return tasks_list

    def title_from_task(self, task: dict) -> str | None:
        for k in ["checkmark", "advancement", "item", "stat"]:
            if k in task:
                return task[k][0]
        for k in ["structure", "biome", "dimension"]:
            if k in task:
                return "Visit: " + task[k][0]
        if "kill" in task:
            return "Kill: " + ", ".join([mob.split(" (")[0] for mob in task["kill"]])
        if "survive" in task:
            return "Survive " + task["survive"][0]
        if "break" in task:
            return task["break"][0].split(" (")[0]
        if "observation" in task:
            return "Meet the " + ", ".join(task["observation"])
        return None

    def __get_chapter_group(self, chapter: dict) -> tuple[str, int] | None:
        group_code = chapter["group"]

        chapter_group_file = MODPACK_ROOT / "config/ftbquests/quests/chapter_groups.snbt"

        with chapter_group_file.open("r", encoding="utf8") as f:
            chapter_group_map = snbt_to_dict(f)["chapter_groups"]

        for i, group in enumerate(chapter_group_map):
            if group_code == group["id"]:
                return slugify(group["title"], "_"), i
        return None

    def __process_item(self, item) -> str | list[str]:
        if isinstance(item, str):
            return self.__item_to_string(item)
        if isinstance(item, dict) and "id" in item:
            if "itemfilters:tag" in item["id"]:
                return "Any " + self.__tag_to_string(item["tag"]["value"])
            if "itemfilters:or" in item["id"]:
                return "Any of: " + ", ".join([self.__item_to_string(i["id"]) for i in item["tag"]["items"]])
            return self.__item_to_string(item["id"])

        raise TypeError("Unknown item type" + str(type(item)) + item)

    def __convert_description_to_string(self, desc: list[str]) -> str:
        """Convert the description to string."""
        return "\n".join(desc)

    def __item_to_string(self, item: str) -> str | None:
        """Convert the item to string."""
        return self.thing_to_string(item, [":"])

    def __tag_to_string(self, item: str) -> str | None:
        """Convert the item to string."""
        return self.thing_to_string(item, [":", "/"])

    def __advancement_to_string(self, advancement: str) -> str | None:
        """Convert the advancement to string."""
        return self.thing_to_string(advancement, [":", "/"])

    @staticmethod
    def thing_to_string(thing: str, sep: list[str]) -> str:
        if not thing:
            return None
        for s in sep:
            thing = thing.rsplit(s, maxsplit=1)[-1]
        return thing.replace("_", " ").title()

    def __get_task_string(self, tasks):
        task_matrix = {
            "checkmark": "",
            "advancement": "Unlock ",
            "item": "Acquire ",
            "stat": "Stats ",
            "survive": "Survive ",
            "break": "Break ",
            "kill": "Kill ",
            "dimension": "Enter ",
            "biome": "Visit ",
            "structure": "Find ",
            "observation": "Meet ",
        }
        single_task = len(tasks) == 1
        task_string = "# Task" + ("s" if not single_task else "") + ":\n"

        for task_type, subtask in tasks.items():
            single_subtask = len(subtask) == 1

            if single_subtask:
                task_string += f"\n- {task_matrix[task_type]}{subtask[0]}"
            else:
                task_string += "## " + task_matrix[task_type] + ":\n"
                for item in [f"- {t}\n" for t in subtask]:
                    task_string += item
        print(task_string)


Quests().launch()
