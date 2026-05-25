"""Tests para arepy_ui.components.tabs"""

from unittest.mock import MagicMock, patch

import pytest

from arepy_ui.core.fonts import TextMetrics
from arepy_ui.core.types import FlexDirection


@pytest.fixture(autouse=True)
def mock_runtime():
    """Mock runtime for all tests in this module."""
    mock_metrics = TextMetrics(width=100.0, height=20.0, line_height=24.0)

    with patch("arepy_ui.core.fonts.get_font_manager") as mock_fm:
        mock_fm.return_value.measure_text_ex.return_value = mock_metrics
        yield mock_fm


class TestTabs:
    def test_tabs_creation(self, mock_runtime):
        from arepy_ui.components.tabs import Tabs

        tabs = Tabs(tabs=[])
        assert len(tabs.tabs_data) == 0

    def test_tabs_with_content(self, mock_runtime):
        from arepy_ui.components.tabs import Tabs
        from arepy_ui.core.node import Node

        content1 = Node()
        content2 = Node()
        tabs = Tabs(
            tabs=[
                ("Tab 1", content1),
                ("Tab 2", content2),
            ]
        )

        assert len(tabs.tabs_data) == 2
        assert tabs.tabs_data[0][0] == "Tab 1"
        assert tabs.tabs_data[0][1] is content1

    def test_tabs_active_index_default(self, mock_runtime):
        from arepy_ui.components.tabs import Tabs
        from arepy_ui.core.node import Node

        tabs = Tabs(
            tabs=[
                ("A", Node()),
                ("B", Node()),
            ]
        )

        assert tabs.active_index == 0

    def test_tabs_set_active(self, mock_runtime):
        from arepy_ui.components.tabs import Tabs
        from arepy_ui.core.node import Node

        tabs = Tabs(
            tabs=[
                ("X", Node()),
                ("Y", Node()),
                ("Z", Node()),
            ]
        )

        tabs.set_tab(2)
        assert tabs.active_index == 2

    def test_tabs_only_active_content_is_visible(self, mock_runtime):
        from arepy_ui.components.tabs import Tabs
        from arepy_ui.core.node import Node

        first = Node()
        second = Node()
        tabs = Tabs(tabs=[("One", first), ("Two", second)])

        assert first.style.visible is True
        assert second.style.visible is False

        tabs.set_tab(1)

        assert first.style.visible is False
        assert second.style.visible is True

    def test_tabs_set_same_index_is_noop(self, mock_runtime):
        from arepy_ui.components.tabs import Tabs
        from arepy_ui.core.node import Node

        tabs = Tabs(tabs=[("One", Node()), ("Two", Node())])
        tabs._set_tab_active_state = MagicMock(wraps=tabs._set_tab_active_state)  # type: ignore

        tabs.set_tab(0)

        tabs._set_tab_active_state.assert_not_called()  # type: ignore

    def test_tabs_set_tab_marks_root_dirty_when_managed(self, mock_runtime):
        from arepy_ui.components.tabs import Tabs
        from arepy_ui.core.node import Node

        tabs = Tabs(tabs=[("One", Node()), ("Two", Node())])
        tabs._manager = MagicMock()

        tabs.set_tab(1)

        tabs._manager.mark_dirty.assert_called_once()

    def test_tabs_has_tab_bar(self, mock_runtime):
        from arepy_ui.components.tabs import Tabs
        from arepy_ui.core.node import Node

        tabs = Tabs(tabs=[("Tab", Node())])

        assert tabs.tab_bar is not None

    def test_tabs_has_content_wrapper(self, mock_runtime):
        from arepy_ui.components.tabs import Tabs
        from arepy_ui.core.node import Node

        tabs = Tabs(tabs=[("Tab", Node())])

        assert tabs.content_wrapper is not None
        assert tabs.children[-1] is tabs.content_wrapper

    def test_tabs_custom_style_preserves_default_column_layout(self, mock_runtime):
        from arepy_ui.components.tabs import Tabs
        from arepy_ui.core.node import Node
        from arepy_ui.core.style import Style
        from arepy_ui.core.types import Color

        tabs = Tabs(
            tabs=[("Tab", Node())],
            style=Style(background_color=Color(1, 2, 3, 255)),
        )

        assert tabs.style.flex_direction == FlexDirection.COLUMN
        assert tabs.style.background_color == Color(1, 2, 3, 255)

    def test_tabs_auto_height_updates_with_active_content(self, mock_runtime):
        from arepy_ui.components.tabs import Tabs
        from arepy_ui.core.node import Node
        from arepy_ui.core.style import Style
        from arepy_ui.core.types import Unit

        short_content = Node(style=Style(width=Unit.percent(100), height=Unit.px(40)))
        tall_content = Node(style=Style(width=Unit.percent(100), height=Unit.px(120)))
        tabs = Tabs(
            tabs=[("Short", short_content), ("Tall", tall_content)],
            width=Unit.px(300),
        )

        tabs.calculate_layout(0, 0, 300, 400)
        short_height = tabs.computed_height

        tabs.set_tab(1)
        tabs.calculate_layout(0, 0, 300, 400)
        tall_height = tabs.computed_height

        assert tall_height > short_height

    def test_tabs_keep_following_container_positioned_below(self, mock_runtime):
        from arepy_ui.components.tabs import Tabs
        from arepy_ui.core.node import Node
        from arepy_ui.core.style import Style
        from arepy_ui.core.types import FlexDirection, Unit

        root = Node(
            style=Style(
                width=Unit.px(400),
                height=Unit.auto(),
                flex_direction=FlexDirection.COLUMN,
                gap=12,
            )
        )
        short_content = Node(style=Style(width=Unit.percent(100), height=Unit.px(40)))
        tall_content = Node(style=Style(width=Unit.percent(100), height=Unit.px(120)))
        tabs = Tabs(
            tabs=[("Short", short_content), ("Tall", tall_content)],
            width=Unit.percent(100),
        )
        sibling = Node(style=Style(width=Unit.percent(100), height=Unit.px(30)))

        root.add_child(tabs)
        root.add_child(sibling)

        root.calculate_layout(0, 0, 400, 600)
        initial_sibling_y = sibling.computed_y
        assert initial_sibling_y >= tabs.computed_y + tabs.computed_height

        tabs.set_tab(1)
        root.calculate_layout(0, 0, 400, 600)

        assert sibling.computed_y >= tabs.computed_y + tabs.computed_height
        assert sibling.computed_y > initial_sibling_y
