"""Tests para arepy_ui.components.tabs"""

from unittest.mock import MagicMock, patch

import pytest

from arepy_ui.core.fonts import TextMetrics


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
