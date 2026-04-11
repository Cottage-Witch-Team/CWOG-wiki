from scripts.tasks import LoadingScreenTips, ae2_rename
from scripts.tasks.quests import Quests


def main():
    Quests().launch()
    LoadingScreenTips().launch()
    ae2_rename.main()


if __name__ == "__main__":
    main()
