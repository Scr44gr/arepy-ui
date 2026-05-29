from __future__ import annotations

from pathlib import Path

from arepy import TextureFilter

from arepy_ui import FontLoadRequest, get_font_manager, load_fonts


FONT_UI = "pixel-chip-ui"
FONT_DISPLAY = "pixel-chip-display"


def font_path() -> str:
    return str(
        Path(__file__).resolve().parents[2]
        / "arepy_ui"
        / "assets"
        / "fonts"
        / "pixel_chip_xl_v1.0.0.ttf"
    )


def setup_game_ui_fonts() -> None:
    font_manager = get_font_manager()
    requests: list[FontLoadRequest] = []
    path = font_path()

    if not font_manager.has_font(FONT_UI):
        requests.append(
            FontLoadRequest(
                name=FONT_UI,
                path=path,
                base_size=32,
                set_as_default=True,
                texture_filter=TextureFilter.NEAREST,
            )
        )
    else:
        font_manager.set_default_font(FONT_UI)

    if not font_manager.has_font(FONT_DISPLAY):
        requests.append(
            FontLoadRequest(
                name=FONT_DISPLAY,
                path=path,
                base_size=96,
                texture_filter=TextureFilter.NEAREST,
            )
        )

    if requests:
        load_fonts(requests)
        font_manager.set_default_font(FONT_UI)


def font_for(role: str = "ui") -> str:
    if role == "display":
        return FONT_DISPLAY
    return FONT_UI
