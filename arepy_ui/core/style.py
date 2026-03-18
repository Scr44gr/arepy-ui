from dataclasses import dataclass, field
from typing import Iterable, Optional

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

    def __post_init__(self):
        object.__setattr__(self, "_owner_style", None)

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
        if name.startswith("_"):
            return

        if "_owner_style" not in self.__dict__:
            return

        owner_style = self._owner_style
        if owner_style is not None:
            owner_style._notify_spacing_changed()

    def _bind_style(self, style: Optional["Style"]):
        object.__setattr__(self, "_owner_style", style)

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

    _LAYOUT_FIELDS = {
        "width",
        "height",
        "min_width",
        "max_width",
        "min_height",
        "max_height",
        "margin",
        "padding",
        "flex_direction",
        "justify_content",
        "align_items",
        "gap",
        "position",
        "top",
        "left",
        "right",
        "bottom",
        "visible",
    }

    def __post_init__(self):
        object.__setattr__(self, "_owner", None)
        self._bind_spacing_owner(self.margin)
        self._bind_spacing_owner(self.padding)

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
        if name.startswith("_"):
            return

        if "_owner" not in self.__dict__:
            return

        if name in {"margin", "padding"} and isinstance(value, Spacing):
            self._bind_spacing_owner(value)

        if name in self._LAYOUT_FIELDS:
            self._notify_layout_changed()

    def _bind_owner(self, owner) -> None:
        object.__setattr__(self, "_owner", owner)
        self._bind_spacing_owner(self.margin)
        self._bind_spacing_owner(self.padding)

    def _bind_spacing_owner(self, spacing: Spacing) -> None:
        spacing._bind_style(self)

    def _notify_spacing_changed(self) -> None:
        self._notify_layout_changed()

    def _notify_layout_changed(self) -> None:
        owner = getattr(self, "_owner", None)
        if owner is not None and hasattr(owner, "mark_dirty"):
            owner.mark_dirty()


def clone_spacing(spacing: Spacing) -> Spacing:
    return Spacing(
        top=spacing.top,
        right=spacing.right,
        bottom=spacing.bottom,
        left=spacing.left,
    )


_DEFAULT_STYLE_REFERENCE = Style()


def merge_style_fields(
    base_style: Style, override_style: Optional[Style], fields: Iterable[str]
) -> Style:
    if override_style is None:
        return base_style

    for field_name in fields:
        value = getattr(override_style, field_name)
        if isinstance(value, Spacing):
            value = clone_spacing(value)
        setattr(base_style, field_name, value)

    return base_style


def merge_non_default_style_fields(
    base_style: Style,
    override_style: Optional[Style],
    fields: Iterable[str],
    default_style: Optional[Style] = None,
) -> Style:
    if override_style is None:
        return base_style

    reference_style = default_style or _DEFAULT_STYLE_REFERENCE

    for field_name in fields:
        value = getattr(override_style, field_name)
        reference_value = getattr(reference_style, field_name)
        if value == reference_value:
            continue
        if isinstance(value, Spacing):
            value = clone_spacing(value)
        setattr(base_style, field_name, value)

    return base_style
