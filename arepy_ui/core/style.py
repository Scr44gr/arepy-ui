from dataclasses import dataclass, field
from typing import Optional

from .types import (
    AlignItems,
    Color,
    CursorType,
    FlexDirection,
    JustifyContent,
    PositionType,
    Unit,
)


@dataclass
class Spacing:
    top: Unit = field(default_factory=lambda: Unit.px(0))
    right: Unit = field(default_factory=lambda: Unit.px(0))
    bottom: Unit = field(default_factory=lambda: Unit.px(0))
    left: Unit = field(default_factory=lambda: Unit.px(0))

    @staticmethod
    def all(value: float) -> "Spacing":
        u = Unit.px(value)
        return Spacing(u, u, u, u)

    @staticmethod
    def symmetric(vertical: float, horizontal: float) -> "Spacing":
        v = Unit.px(vertical)
        h = Unit.px(horizontal)
        return Spacing(v, h, v, h)


@dataclass
class Style:
    # Layout
    width: Unit = field(default_factory=Unit.auto)
    height: Unit = field(default_factory=Unit.auto)

    min_width: Optional[Unit] = None
    max_width: Optional[Unit] = None
    min_height: Optional[Unit] = None
    max_height: Optional[Unit] = None

    margin: Spacing = field(default_factory=Spacing)
    padding: Spacing = field(default_factory=Spacing)

    flex_direction: FlexDirection = FlexDirection.COLUMN
    justify_content: JustifyContent = JustifyContent.START
    align_items: AlignItems = AlignItems.STRETCH
    gap: float = 0.0  # In pixels for simplicity

    position: PositionType = PositionType.RELATIVE
    top: Optional[Unit] = None
    left: Optional[Unit] = None
    right: Optional[Unit] = None
    bottom: Optional[Unit] = None

    # Appearance
    background_color: Optional[Color] = None
    border_color: Optional[Color] = None
    border_width: float = 0.0
    border_radius: float = 0.0

    opacity: float = 1.0
    visible: bool = True

    # Text (inherited by text nodes usually, but useful here)
    text_color: Optional[Color] = None
    font_size: float = 16.0

    z_index: int = 0

    # Cursor
    cursor: Optional[CursorType] = None
