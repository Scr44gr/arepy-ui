from typing import List, Optional, Tuple

from ..core.node import Node
from ..core.style import Spacing, Style
from ..core.types import Color, FlexDirection, JustifyContent, Unit
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
        super().__init__(style=style or default_style, **kwargs)

        self.tabs_data = tabs
        self.active_index = 0

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
        # Use a ScrollView for the content to prevent overflow
        from .scroll import ScrollView

        self.content_wrapper = Node(
            style=Style(
                width=Unit.percent(100),
                height=Unit.percent(90),  # Remaining height
                padding=Spacing.all(10),
            )
        )
        # We don't add content_wrapper directly, we add a ScrollView that contains it?
        # No, the content itself changes.
        # We should make the content_container a ScrollView?
        # But ScrollView takes a 'content' node in init.

        # Let's make a container for the active tab content.
        self.content_container = Node(
            style=Style(width=Unit.percent(100), height=Unit.percent(100))
        )

        # We wrap this container in a ScrollView?
        # Or we wrap each tab content in a ScrollView when we add it?
        # The user's Inventory tab already has a ScrollView.
        # The Settings tab does not.

        # Let's just add the content_container to self.
        self.add_child(self.content_container)

        self._build_ui()

    def _build_ui(self):
        # Optimization: Don't destroy buttons if they exist, just update style
        if not self.tab_bar.children:
            # First build - create buttons and add content
            for i, (title, content) in enumerate(self.tabs_data):
                btn = Button(
                    text=title,
                    on_click=lambda idx=i: self.set_tab(idx),
                    width=Unit.auto(),
                    bg_color=Color(30, 30, 40, 255),
                    border_radius=0.0,
                )
                btn.style.padding = Spacing.symmetric(8, 16)
                self.tab_bar.add_child(btn)

                # Add content directly - don't wrap if already ScrollView
                from .scroll import ScrollView

                content.style.visible = False
                self.content_container.add_child(content)

        # Update button styles
        for i, child in enumerate(self.tab_bar.children):
            is_active = i == self.active_index
            if isinstance(child, Button):
                child.style.background_color = (
                    Color(50, 50, 60, 255) if is_active else Color(30, 30, 40, 255)
                )
                child.style.border_radius = 4.0 if is_active else 0.0

        # Update content visibility
        for i, child in enumerate(self.content_container.children):
            child.style.visible = i == self.active_index

        self.mark_dirty()

    def set_tab(self, index: int):
        if 0 <= index < len(self.tabs_data):
            self.active_index = index
            self._build_ui()
