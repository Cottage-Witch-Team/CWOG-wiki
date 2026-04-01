import json
import os
from pathlib import Path
from typing import Generator

import ftb_snbt_lib as slib


def main():
    root = Path(__file__).absolute().parent.parent

    quest_dir = root / "repo_code/config/ftbquests/quests/chapters/ars_nouveau.snbt"

    with open(quest_dir) as f:
        quests = json.loads(json.dumps(slib.load(f)))

        descs = [(qu.get("description"),
                  qu.get("title") or qu.get("subtitle") or qu.get("tasks")[0]) for qu in quests["quests"]]

        for d, t in descs:
            if type(d) == str:
                d = [d]

            if not d: return

            text = '\n'.join(d)

            print(('\n' if t is 'None' else t) + '\n' + text + '\n')

    # dest_file = root / "docs/wiki/all_loading_screen_tips.md"


#
# tip_list = _get_tips(quest_dir)
#
# all_tips = print([y for x in tip_list
#                  for y in x])

# with open(dest_file, "w") as f:
#    f.write(all_tips)


def _get_tips(tips_path: Path) -> Generator[str]:
    for dir, _, files in os.walk(tips_path):
        for file in files:
            with open(Path(dir) / file) as f:
                file_object = slib.load(f)
                yield file_object["quests"]


if __name__ == "__main__":
    main()
