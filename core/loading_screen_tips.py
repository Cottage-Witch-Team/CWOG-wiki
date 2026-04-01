import json
import os
from pathlib import Path
from typing import Generator


def main():
    root = Path(__file__).absolute().parent.parent

    tips_dir = root / "repo_code/kubejs/assets/cottagewitch/tips/"

    dest_file = root / "docs/wiki/all_loading_screen_tips.md"

    tip_list = _get_tips(tips_dir)

    all_tips = "# All loading screen tips!\n\n> " + "---\n> ".join(tip_list)

    with open(dest_file, "w") as f:
        f.write(all_tips)


def _get_tips(tips_path: Path) -> Generator[str]:
    for dir, _, files in os.walk(tips_path):
        for file in files:
            with open(Path(dir) / file) as f:
                file_object = json.load(f)
                yield file_object["tip"]["text"]


if __name__ == "__main__":
    main()
