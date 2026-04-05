import json
import urllib.request

from constants import MODPACK_ROOT, REPO_ROOT

from core.constants import DOCS_ROOT

output_folder = REPO_ROOT / "temp"

output_folder.mkdir(parents=True, exist_ok=True)

source_loc = output_folder / "en_us.json"
cw_loc = MODPACK_ROOT / "kubejs/assets/ae2/lang/en_us.json"

urllib.request.urlretrieve(
    "https://raw.githubusercontent.com/AppliedEnergistics/Applied-Energistics-2/refs/heads/main/src/generated/resources/assets/ae2/lang/en_us.json",
    source_loc,
)

with source_loc.open(encoding="utf8") as f:
    en_us_true = json.load(f)

with cw_loc.open(encoding="utf8") as f:
    kubejs_true = json.load(f)

diff = {
    k: (v, kubejs_true.get(k))
    for k, v in en_us_true.items()
    if kubejs_true.get(k) != v and kubejs_true.get(k) is not None and (("item.") in k or ("block.") in k)
}

import re

with open(MODPACK_ROOT / "kubejs/startup_scripts/globals/global_consts.js", encoding="utf-8") as f:
    content = f.read()

match = re.search(r"global\.ae2_disabled_items\s*=\s*\[(.*?)\]", content, re.DOTALL)

if match:
    raw_items = match.group(1)

    items = re.findall(r'"(.*?)"', raw_items)
else:
    print("Variable not found")

diff2 = {
    re.sub(r"(?:item|block)\.([^.]+)\.(.+)", r"\1:\2", k): {
        "old": v[0],
        "new": v[1],
    }
    for k, v in diff.items()
}

diff3 = {k: v | {"enabled": k not in items} for k, v in diff2.items()}

string = """
# AE2 - item renames

---

| item id | old name | new name | enabled |
| ------- | -------- | -------- | ------- |"""

for k, v in diff3.items():
    string += f"""
| {k} | {v["old"]} | {v["new"]} | {v["enabled"]} |"""

ae2_rename = DOCS_ROOT / "wiki" / "ae2_item_renames.md"

ae2_rename.write_text(string, encoding="utf8")
