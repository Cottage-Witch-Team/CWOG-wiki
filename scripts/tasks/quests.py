import logging
import re
import shutil
from collections.abc import Generator
from pathlib import Path
from typing import Any

from markdown.extensions.toc import slugify

from scripts.core.constants import DOCS_ROOT
from scripts.core.entities import MarkdownPage, ModpackDirectory, ModpackFile
from scripts.core.markdown_funcs import ImageRegistry, advancement_to_string, item_to_string, tag_to_string
from scripts.core.mc_formatter import parse_mc_formatting_to_markdown
from scripts.core.parsers import SnbtParser
from scripts.core.wiki_builder import WikiBuildTask

logger = logging.getLogger(__name__)


class Quests(WikiBuildTask):
    quests_chapters_source = ModpackDirectory(rel_path="config/ftbquests/quests/chapters").get_files()
    chapter_groups_source = ModpackFile(rel_path="config/ftbquests/quests/chapter_groups.snbt")

    quest_pages: list[MarkdownPage] = []

    quest_root = "generated/quests"

    image_re = re.compile(r"\{image:cottagewitch:([^ \}]+)(.*?)\}")

    quest_book = None

    def run_task(self) -> None:
        self.prepare_data()
        self.render_files()
        self.write_files()

    def prepare_data(self) -> None:
        chapters = {}
        quest_book = {}

        for source_chapter in self.quests_chapters_source:
            parsed = SnbtParser().parse(source_chapter)
            chapters[parsed.title] = parsed.content

        chapter_groups_map = self._get_chapter_groups()

        image_processor = ImageRegistry(rel_source_root="kubejs/assets/cottagewitch")

        for raw_title, chapter in chapters.items():
            chapter_title = raw_title.replace("__", "_and_")
            chapter_group, group_ordinal = chapter_groups_map[chapter["group"]]

            group = quest_book.setdefault(
                chapter_group,
                {"ordinal": group_ordinal},
            )

            chapter_entry = group.setdefault(
                chapter_title,
                {"ordinal": chapter["order_index"]},
            )

            for i, quest in enumerate(chapter["quests"]):
                if quest.get("secret"):
                    continue

                quest_title, quest_subtitle, quest_desc, quest_task = self._process_quest_to_string(quest)

                if not quest_desc and not quest_task:
                    continue

                quest_title = quest_title or chapter_title

                quest_entry = chapter_entry.setdefault(
                    quest_title,
                    {"ordinal": i},
                )

                quest_entry["subtitle"] = quest_subtitle
                quest_entry["description"] = self.replace_images(quest_desc, image_processor)
                quest_entry["task"] = quest_task

            self.quest_book = quest_book

    def render_files(self) -> None:
        quest_book = self.quest_book

        for chapter_group_title, chapter_group in self._iter_sorted_entries(quest_book):
            logger.info("Chapter group: %s", chapter_group_title.upper())

            for chapter_title, chapter in self._iter_sorted_entries(chapter_group):
                logger.info("  Chapter: %s", chapter_title)

                for quest_title, quest in self._iter_sorted_entries(chapter):
                    logger.debug("    Quest: %s", quest_title)

                    path_to_write = self._quest_path(chapter_group_title, chapter_title, quest_title)

                    file = MarkdownPage(
                        title=quest_title,
                        subtitle=quest["subtitle"],
                        description=quest["description"],
                        content=quest["task"],
                        rel_output_path=path_to_write,
                    )
                    self.quest_pages.append(file)

    def write_files(self) -> None:
        shutil.rmtree(DOCS_ROOT / self.quest_root, ignore_errors=True)

        for page in self.quest_pages:
            page.write_to_file()

    # region Private

    def replace_images(self, text: str, registry: ImageRegistry) -> str:
        def repl(match: object) -> str:
            rel_path = match.group(1)

            return registry.process_image(rel_path)

        return self.image_re.sub(repl, text)

    def _get_chapter_groups(self) -> dict[str, tuple[str, int]]:
        chapter_groups = SnbtParser().parse(self.chapter_groups_source)

        return {
            group["id"]: (slugify(group["title"], "_"), i)
            for i, group in enumerate(chapter_groups.content["chapter_groups"])
        }

    def _iter_sorted_entries(self, mapping: dict) -> Generator[tuple[Any, Any], Any, None]:
        return (
            (k, v)
            for k, v in sorted(
                mapping.items(),
                key=self.ordinal_sort_key,
            )
            if k != "ordinal"
        )

    @staticmethod
    def ordinal_sort_key(item: tuple[str, dict]) -> int:
        key, value = item

        if key == "ordinal":
            return 0

        return value["ordinal"] + 1

    def _quest_path(self, group_title: str, chapter_title: str, quest_title: str) -> Path:
        return (
            Path(self.quest_root)
            / slugify(group_title, "_")
            / slugify(chapter_title, "_")
            / f"{slugify(quest_title, '_')}.md"
        )

    def _process_quest_to_string(self, quest: dict) -> tuple[str | None, str | None, str | None, str | None]:
        tasks = self._process_tasks_on_quest(quest)
        if not tasks:
            return None, None, None, None

        title = quest.get("title") or self._title_from_task(tasks)

        subtitle = quest.get("subtitle")
        subtitle = subtitle.capitalize() if subtitle else None

        description = quest.get("description", [""])
        if isinstance(description, str):
            description = [description]
        description_block = self._convert_description_to_string(description) if description else ""

        task_string = self._get_task_string(tasks)

        return title, subtitle, description_block, task_string

    def _process_tasks_on_quest(self, quest: dict) -> dict[str, list[str]] | None:
        quest_tasks = quest.get("tasks")
        if not quest_tasks:
            return None

        handlers = {
            "item": self._handle_item_task,
            "advancement": self._handle_advancement_task,
            "observation": self._handle_observation_task,
            "kill": self._handle_kill_task,
            "checkmark": self._handle_checkmark_task,
            "questsadditions:break": self._handle_break_task,
            "questsadditions:days": self._handle_survive_task,
            "stat": self._handle_stat_task,
            "structure": self._handle_tag_task,
            "biome": self._handle_tag_task,
            "dimension": self._handle_tag_task,
        }

        tasks_list: dict[str, list[str]] = {}

        for task in quest_tasks:
            task_type = task.get("type")
            handler = handlers.get(task_type)

            if not handler:
                continue

            normalized_type, task_goal = handler(task)

            if task_goal is None:
                continue

            tasks_list.setdefault(normalized_type, []).append(task_goal)

        return tasks_list

    def _handle_item_task(self, task: dict) -> tuple[str, str]:
        item = task.get("item")
        count = task.get("count", item.get("Count", 1) if isinstance(item, dict) else 1)

        suffix = "" if count == 1 else f" ({count})"
        return "item", f"{self._process_item(item)}{suffix}"

    @staticmethod
    def _handle_advancement_task(task: dict) -> tuple[str, str]:
        return "advancement", advancement_to_string(task.get("advancement"))

    @staticmethod
    def _handle_observation_task(task: dict) -> tuple[str, str]:
        return "observation", item_to_string(task["to_observe"])

    @staticmethod
    def _handle_kill_task(task: dict) -> tuple[str, str]:
        count = task["value"]
        suffix = "" if count == 1 else f" ({count})"

        return "kill", f"{item_to_string(task['entity'])}{suffix}"

    @staticmethod
    def _handle_survive_task(task: dict) -> tuple[str, str]:
        return "survive", f"{task['days']} days"

    @staticmethod
    def _handle_stat_task(task: dict) -> tuple[str, str]:
        count = task["value"]
        suffix = "" if count == 1 else f" ({count})"
        return "stat", f"{advancement_to_string(task['stat'])}{suffix}"

    @staticmethod
    def _handle_checkmark_task(task: dict) -> tuple[str, str | None]:
        return "checkmark", task.get("title")

    @staticmethod
    def _handle_tag_task(task: dict) -> tuple[str, str]:
        task_type = task["type"]
        return task_type, tag_to_string(task[task_type])

    @staticmethod
    def _handle_break_task(task: dict) -> tuple[str, str]:
        return "break", item_to_string(task["block"])

    @staticmethod
    def _title_from_task(task: dict) -> str | None:
        simple_keys = ("checkmark", "advancement", "item", "stat")
        visit_keys = ("structure", "biome", "dimension")

        for key in simple_keys:
            if key in task:
                return task[key][0]

        for key in visit_keys:
            if key in task:
                return f"Visit: {task[key][0]}"

        if "kill" in task:
            return f"Kill: {', '.join(m.split(' (')[0] for m in task['kill'])}"
        if "survive" in task:
            return f"Survive {task['survive'][0]}"
        if "break" in task:
            return task["break"][0].split(" (")[0]
        if "observation" in task:
            return f"Meet the {', '.join(task['observation'])}"

        return None

    @staticmethod
    def _process_item(item: str | dict) -> str:
        if isinstance(item, str):
            return item_to_string(item)

        if not isinstance(item, dict) or "id" not in item:
            raise TypeError(f"Unknown item type: {type(item)} -> {item!r}")

        item_id = item["id"]

        if "itemfilters:tag" in item_id:
            return "Any " + tag_to_string(item["tag"]["value"])

        if "itemfilters:or" in item_id:
            items = ", ".join([item_to_string(i["id"]) for i in item["tag"]["items"]])
            return f"Any of: {items}"

        return item_to_string(item_id)

    def _convert_description_to_string(self, desc: list[str]) -> str:
        """Convert the description to string."""
        joined_desc = "\n\n".join(desc).replace("{@pagebreak}", "\n\n---\n\n")

        return parse_mc_formatting_to_markdown(joined_desc)

    @staticmethod
    def _get_task_string(tasks: dict) -> str | None:
        if not tasks:
            return None

        task_matrix = {
            "checkmark": "",
            "advancement": "",
            "item": "Acquire",
            "stat": "Stats: ",
            "survive": "Survive",
            "break": "Break",
            "kill": "Kill",
            "dimension": "Enter",
            "biome": "Visit",
            "structure": "Find",
            "observation": "Meet",
        }
        task_string = '!!! tip "TASK" \n'

        for task_type, subtask in tasks.items():
            for sub in subtask:
                task_string += f"\n\t- [ ] {task_matrix[task_type]} **{sub}**"

        return task_string

    # endregion


Quests().run_task()
