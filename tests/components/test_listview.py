"""Tests for ListView component."""

from unittest.mock import MagicMock, patch

import pytest


class TestListView:
    """Tests for ListView component."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up mocks for runtime."""
        with (
            patch("arepy_ui.components.listview.get_runtime") as mock_get_runtime,
            patch(
                "arepy_ui.components.listview.check_collision_point_rec"
            ) as mock_collision,
        ):
            self.mock_runtime = MagicMock()
            self.mock_renderer = MagicMock()
            self.mock_renderer.measure_text.return_value = 100
            self.mock_runtime.renderer = self.mock_renderer
            self.mock_runtime.input = MagicMock()
            self.mock_runtime.input.is_key_pressed.return_value = False
            self.mock_runtime.input.is_mouse_button_pressed.return_value = False
            mock_get_runtime.return_value = self.mock_runtime

            self.mock_collision = mock_collision
            mock_collision.return_value = False

            yield

    def test_listview_creation_empty(self):
        """Test creating an empty ListView."""
        from arepy_ui.components.listview import ListView

        listview = ListView(items=[])

        assert listview is not None
        assert len(listview.items) == 0

    def test_listview_creation_with_items(self):
        """Test creating a ListView with items."""
        from arepy_ui.components.listview import ListItem, ListView

        items = [
            ListItem(label="Item 1", value="v1"),
            ListItem(label="Item 2", value="v2"),
            ListItem(label="Item 3", value="v3"),
        ]
        listview = ListView(items=items)

        assert len(listview.items) == 3
        assert listview.items[0].label == "Item 1"

    def test_listview_single_selection(self):
        """Test ListView single selection mode."""
        from arepy_ui.components.listview import ListItem, ListView

        items = [
            ListItem(label="Item 1", value="v1"),
            ListItem(label="Item 2", value="v2"),
        ]
        listview = ListView(items=items, multi_select=False)

        assert listview.multi_select == False

    def test_listview_multi_selection(self):
        """Test ListView multi-selection mode."""
        from arepy_ui.components.listview import ListItem, ListView

        items = [
            ListItem(label="Item 1", value="v1"),
            ListItem(label="Item 2", value="v2"),
        ]
        listview = ListView(items=items, multi_select=True)

        assert listview.multi_select == True

    def test_listview_item_height(self):
        """Test ListView with custom item height."""
        from arepy_ui.components.listview import ListView

        listview = ListView(items=[], item_height=50)

        assert listview.item_height == 50

    def test_listview_on_select_callback(self):
        """Test ListView on_select callback."""
        from arepy_ui.components.listview import ListItem, ListView

        on_select_callback = MagicMock()
        items = [ListItem(label="Item 1", value="v1")]
        listview = ListView(items=items, on_select=on_select_callback)

        assert listview.on_select == on_select_callback

    def test_listview_selected_values_empty(self):
        """Test getting selected values when none are selected."""
        from arepy_ui.components.listview import ListItem, ListView

        items = [
            ListItem(label="Item 1", value="v1"),
            ListItem(label="Item 2", value="v2"),
        ]
        listview = ListView(items=items)

        assert len(listview.selected_values) == 0

    def test_listview_select_index(self):
        """Test selecting an item by index."""
        from arepy_ui.components.listview import ListItem, ListView

        items = [
            ListItem(label="Item 1", value="v1"),
            ListItem(label="Item 2", value="v2"),
        ]
        listview = ListView(items=items)

        listview.select_index(0)

        assert len(listview.selected_values) == 1
        assert listview.selected_values[0] == "v1"

    def test_listview_scroll_state(self):
        """Test ListView scroll state."""
        from arepy_ui.components.listview import ListView

        listview = ListView(items=[])

        assert listview.scroll_y == 0

    def test_listview_handle_input_in_bounds(self):
        """Test ListView input handling within bounds."""
        from arepy_ui.components.listview import ListItem, ListView

        items = [ListItem(label="Item 1", value="v1")]
        listview = ListView(items=items)
        listview.computed_x = 0
        listview.computed_y = 0
        listview.computed_width = 200
        listview.computed_height = 100

        mock_mouse = MagicMock()
        mock_mouse.x = 100
        mock_mouse.y = 20

        result = listview.handle_input(mock_mouse, False)

        assert isinstance(result, bool)

    def test_listview_render(self):
        """Test ListView rendering."""
        from arepy_ui.components.listview import ListItem, ListView

        items = [
            ListItem(label="Item 1", value="v1"),
            ListItem(label="Item 2", value="v2"),
        ]
        listview = ListView(items=items)
        listview.computed_x = 0
        listview.computed_y = 0
        listview.computed_width = 200
        listview.computed_height = 100

        # Should not raise
        listview.render()

    def test_listview_with_custom_size(self):
        """Test ListView with custom dimensions."""
        from arepy_ui.components.listview import ListView
        from arepy_ui.core.types import Unit

        listview = ListView(items=[], width=Unit.px(300), height=Unit.px(400))

        assert listview is not None

    def test_listitem_with_value(self):
        """Test ListItem with custom value."""
        from arepy_ui.components.listview import ListItem

        item = ListItem(label="Test", value={"key": "value"})

        assert item.label == "Test"
        assert item.value == {"key": "value"}

    def test_listview_selected_items_property(self):
        """Test selected_items property."""
        from arepy_ui.components.listview import ListItem, ListView

        items = [
            ListItem(label="Item 1", value="v1"),
            ListItem(label="Item 2", value="v2"),
        ]
        listview = ListView(items=items)
        listview.select_index(0)

        selected = listview.selected_items
        assert len(selected) == 1
        assert selected[0].label == "Item 1"
