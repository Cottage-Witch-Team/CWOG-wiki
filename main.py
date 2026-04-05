from core import ae2_rename
from core.loading_screen_tips import LoadingScreenTips
from core.quests import Quests


def main():
    Quests().launch()
    LoadingScreenTips().launch()
    ae2_rename.main()


if __name__ == "__main__":
    main()
