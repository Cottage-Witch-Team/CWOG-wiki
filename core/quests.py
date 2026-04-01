import json
import re
from pathlib import Path

import ftb_snbt_lib as slib


def main():
    root = Path(__file__).absolute().parent.parent

    quest_dir = root / "repo_code/config/ftbquests/quests/chapters/ars_nouveau.snbt"

    full = ['# Ars Nouveau Quests\n\n']

    with open(quest_dir) as f:
        quests = json.loads(json.dumps(slib.load(f)))

        descs = [(qu.get("description"),
                  qu.get("title") or qu.get("subtitle")) for qu in quests["quests"]]

        for d, t in descs:
            if type(d) == str:
                d = [d]

            if not d: continue

            text = '\n'.join(d)

            quest = ('---\n# ' + t if t else '---') + '\n' + text + '\n'

            full.append(quest)

    dest_file = root / "docs/wiki/ars_quests.md"

    fulltext = re.sub(
        r'&[a-zA-Z0-9]', r'**', '\n'.join(full))

    with open(dest_file, "w") as f:
        print("writing", dest_file)
        f.write(fulltext)


if __name__ == "__main__":
    main()
