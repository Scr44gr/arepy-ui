from __future__ import annotations


if __package__ in {None, ""}:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from game_ui.app import GameInterfaceApp
else:
    from .app import GameInterfaceApp


def main(locale: str = "es") -> None:
    GameInterfaceApp(locale=locale).run()


if __name__ == "__main__":
    main()
