from typing import List, Optional, Tuple

from ..core.node import Node
from ..core.style import Spacing, Style, merge_non_default_style_fields
from ..core.types import Color, FlexDirection, Unit
from .button import Button


class Tabs(Node):
    def __init__(
        self,
        tabs: List[Tuple[str, Node]],  # List of (Title, ContentNode)
        width: Unit = Unit.auto(),
        height: Unit = Unit.auto(),
        style: Optional[Style] = None,
        **kwargs,
    ):
        default_style = Style(
            width=width, height=height, flex_direction=FlexDirection.COLUMN
        )
        merge_non_default_style_fields(
            default_style,
            style,
            (
                "width",
                "height",
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
                "opacity",
                "background_color",
                "border_color",
                "border_width",
                "border_radius",
                "cursor",
            ),
        )
        super().__init__(style=default_style, **kwargs)

        self.tabs_data = tabs
        self.active_index = 0
        self._tab_buttons: list[Button] = []
        self._tab_contents: list[Node] = []

        # Tab Bar
        # Use a ScrollView for the tab bar if it overflows?
        # Or just allow wrapping? FlexDirection.ROW wraps by default? No, we haven't implemented wrap.
        # Let's assume for now we just want them to fit.
        self.tab_bar = Node(
            style=Style(
                width=Unit.percent(100),
                height=Unit.px(40),
                flex_direction=FlexDirection.ROW,
                gap=2.0,
                # overflow='hidden' # Not implemented
            )
        )
        # Wrap tab bar in a container that could scroll if needed, but for now let's just keep it simple.
        self.add_child(self.tab_bar)

        # Content Container
        self.content_wrapper = Node(
            style=Style(
                width=Unit.percent(100),
                height=Unit.auto(),
                padding=Spacing.all(10),
            )
        )
        self.content_container = Node(
            style=Style(
                width=Unit.percent(100),
                height=Unit.auto(),
                flex_direction=FlexDirection.COLUMN,
            )
        )
        self.content_wrapper.add_child(self.content_container)
        self.add_child(self.content_wrapper)

        self._build_ui()

    def _build_ui(self):
        if self._tab_buttons:
            return

        for index, (title, content) in enumerate(self.tabs_data):
            button = Button(
                text=title,
                on_click=lambda idx=index: self.set_tab(idx),
                width=Unit.auto(),
                bg_color=Color(30, 30, 40, 255),
                border_radius=0.0,
            )
            button.style.padding = Spacing.symmetric(8, 16)
            self.tab_bar.add_child(button)
            self._tab_buttons.append(button)

            content.style.visible = False
            self.content_container.add_child(content)
            self._tab_contents.append(content)

        self._set_tab_active_state(self.active_index, True)

    def _set_tab_active_state(self, index: int, is_active: bool):
        if not 0 <= index < len(self._tab_buttons):
            return

        button = self._tab_buttons[index]
        content = self._tab_contents[index]
        button.style.background_color = (
            Color(50, 50, 60, 255) if is_active else Color(30, 30, 40, 255)
        )
        button.style.border_radius = 4.0 if is_active else 0.0
        content.style.visible = is_active

    def set_tab(self, index: int):
        if not 0 <= index < len(self.tabs_data):
            return
        if index == self.active_index:
            return

        previous_index = self.active_index
        self.active_index = index
        self._set_tab_active_state(previous_index, False)
        self._set_tab_active_state(index, True)

        if self._manager is not None:
            self._manager.mark_dirty()
        else:
            self.mark_dirty()
