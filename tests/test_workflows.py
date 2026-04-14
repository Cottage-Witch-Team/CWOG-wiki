# ruff: noqa: S101

import importlib
import os
import sys
import tomllib
import unittest
from pathlib import Path
from unittest.mock import patch

import scripts.main as main_module
from scripts.core.constants import DOCS_ROOT, TEMP_FILE_ROOT
from scripts.tasks import AE2RenameTask, LoadingScreenTips, Quests
from scripts.tasks.quests import Quests as QuestsTask


def snapshot_tree(root: Path) -> dict[str, tuple[int, int]]:
    """Build a file snapshot keyed by relative path."""
    if not root.exists():
        return {}
    return {
        str(path.relative_to(root)): (int(path.stat().st_mtime_ns), path.stat().st_size)
        for path in root.rglob("*")
        if path.is_file()
    }


class TestWorkflowImports(unittest.TestCase):
    def test_imports_have_no_file_side_effects(self) -> None:
        before_generated = snapshot_tree(DOCS_ROOT / "generated")
        before_temp = snapshot_tree(TEMP_FILE_ROOT)

        for module_name in (
            "scripts.tasks.ae2_rename",
            "scripts.tasks.loading_screen_tips",
            "scripts.tasks.quests",
        ):
            sys.modules.pop(module_name, None)
            importlib.import_module(module_name)

        after_generated = snapshot_tree(DOCS_ROOT / "generated")
        after_temp = snapshot_tree(TEMP_FILE_ROOT)

        assert before_generated == after_generated
        assert before_temp == after_temp


class TestWorkflowRunner(unittest.TestCase):
    def test_main_executes_tasks_once_in_fixed_order(self) -> None:
        execution_order: list[str] = []

        class FakeTask:
            def __init__(self, name: str) -> None:
                self.name = name

            def run(self) -> None:
                execution_order.append(self.name)

        with (
            patch.object(main_module, "Quests", return_value=FakeTask("Quests")),
            patch.object(main_module, "LoadingScreenTips", return_value=FakeTask("LoadingScreenTips")),
            patch.object(main_module, "AE2RenameTask", return_value=FakeTask("AE2RenameTask")),
        ):
            main_module.main()

        assert execution_order == ["Quests", "LoadingScreenTips", "AE2RenameTask"]


class TestWorkflowContract(unittest.TestCase):
    def test_task_classes_implement_phase_contract(self) -> None:
        for cls in (Quests, LoadingScreenTips, AE2RenameTask):
            assert hasattr(cls, "prepare_data")
            assert hasattr(cls, "render_output")
            assert hasattr(cls, "write_output")
            assert not hasattr(cls, "launch")
            assert not hasattr(cls, "run_task")

    def test_base_run_invokes_phase_methods_in_order(self) -> None:
        for task in (Quests(), LoadingScreenTips(), AE2RenameTask()):
            call_order: list[str] = []

            def record(name: str, seq: list[str] = call_order) -> None:
                seq.append(name)

            with (
                patch.object(task, "prepare_data", side_effect=lambda: record("prepare_data")),
                patch.object(task, "render_output", side_effect=lambda: record("render_output")),
                patch.object(task, "write_output", side_effect=lambda: record("write_output")),
            ):
                task.run()

            assert call_order == ["prepare_data", "render_output", "write_output"]


class TestWorkflowSmoke(unittest.TestCase):
    @unittest.skipUnless(
        os.getenv("RUN_WORKFLOW_SMOKE") == "1",
        "Set RUN_WORKFLOW_SMOKE=1 to run full workflow smoke test.",
    )
    def test_main_generates_expected_outputs(self) -> None:
        main_module.main()

        assert (DOCS_ROOT / "generated" / "ae2_renames.md").exists()
        assert (DOCS_ROOT / "wiki" / "all_loading_screen_tips.md").exists()
        assert (DOCS_ROOT / "generated" / "quests").exists()


class TestQuestNavSafety(unittest.TestCase):
    def test_guard_allows_nav_only_change(self) -> None:
        original = tomllib.loads(
            """
[project]
site_name = "Example"
nav = [{ "A" = ["a.md"] }]

[project.theme]
language = "en"
""",
        )
        updated = tomllib.loads(
            """
[project]
site_name = "Example"
nav = [{ "A" = ["a.md"] }, { "Quests" = ["generated/quests/q1.md"] }]

[project.theme]
language = "en"
""",
        )

        QuestsTask.assert_only_nav_changed(original, updated)

    def test_guard_rejects_non_nav_change(self) -> None:
        original = tomllib.loads(
            """
[project]
site_name = "Example"
nav = [{ "A" = ["a.md"] }]
""",
        )
        updated = tomllib.loads(
            """
[project]
site_name = "Changed"
nav = [{ "A" = ["a.md"] }, { "Quests" = ["generated/quests/q1.md"] }]
""",
        )

        raised = False
        try:
            QuestsTask.assert_only_nav_changed(original, updated)
        except ValueError:
            raised = True

        assert raised

    def test_generated_nav_block_preserves_iteration_order(self) -> None:
        task = QuestsTask()
        task.quest_nav = [
            (
                "group_a",
                [
                    (
                        "chapter_1",
                        [
                            "generated/quests/group_a/chapter_1/q2.md",
                            "generated/quests/group_a/chapter_1/q1.md",
                        ],
                    ),
                    ("chapter_2", ["generated/quests/group_a/chapter_2/q3.md"]),
                ],
            ),
            (
                "group_b",
                [
                    ("chapter_3", ["generated/quests/group_b/chapter_3/q4.md"]),
                ],
            ),
        ]

        block = task.build_generated_nav_block()
        first_index = block.index("generated/quests/group_a/chapter_1/q2.md")
        second_index = block.index("generated/quests/group_a/chapter_1/q1.md")
        third_index = block.index("generated/quests/group_a/chapter_2/q3.md")
        fourth_index = block.index("generated/quests/group_b/chapter_3/q4.md")

        assert first_index < second_index < third_index < fourth_index
