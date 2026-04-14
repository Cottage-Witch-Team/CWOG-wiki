import logging

from scripts.core.wiki_builder import WikiBuildTask
from scripts.tasks import AE2RenameTask, LoadingScreenTips, Quests

logger = logging.getLogger(__name__)


def _run_task(task: WikiBuildTask) -> None:
    task_name = task.__class__.__name__
    logger.info("Starting task: %s", task_name)
    try:
        task.run()
    except Exception:
        logger.exception("Task failed: %s", task_name)
        raise
    logger.info("Task completed: %s", task_name)

def main() -> None:
    """Run all wiki build tasks in a fixed order."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    task_sequence: list[WikiBuildTask] = [Quests(), LoadingScreenTips(), AE2RenameTask()]

    for task in task_sequence:
        _run_task(task)


if __name__ == "__main__":
    main()
