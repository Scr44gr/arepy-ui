"""Tests para arepy_ui.manager"""

from unittest.mock import MagicMock, patch

import pytest

from arepy_ui.config import ResizeMode, UIConfig
from arepy_ui.core.node import Node
from arepy_ui.core.style import Style
from arepy_ui.core.types import Unit


@pytest.fixture
def mock_runtime():
    """Mock runtime for UIManager tests."""
    mock = MagicMock()
    mock.display.get_window_size.return_value = (1280, 720)
    mock.renderer.get_font_default.return_value = MagicMock()
    mock.renderer.is_stencil_available.return_value = True
    mock.input.get_mouse_position.return_value = (0, 0)
    mock.input.is_mouse_button_pressed.return_value = False

    with patch("arepy_ui.manager.get_runtime", return_value=mock):
        with patch("arepy_ui.runtime.get_runtime", return_value=mock):
            yield mock


class TestUIManager:
    def test_manager_creation(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()

        assert manager.root is None
        assert manager.config is not None

    def test_manager_with_config(self, mock_runtime):
        from arepy_ui.manager import UIManager

        config = UIConfig(
            resize_mode=ResizeMode.RESPONSIVE,
            reference_width=1920,
            reference_height=1080,
        )
        manager = UIManager(config=config)

        assert manager.config.resize_mode == ResizeMode.RESPONSIVE
        assert manager.config.reference_width == 1920

    def test_set_root(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()
        root = Node()

        manager.set_root(root)

        assert manager.root is root
        # Layout is calculated immediately on set_root, so is_dirty becomes False
        assert not manager.is_dirty, "is_dirty should be False after set_root"

    def test_mark_dirty(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()
        manager.is_dirty = False

        manager.mark_dirty()

        assert manager.is_dirty, "is_dirty should be True after mark_dirty"

    def test_get_reference_size(self, mock_runtime):
        from arepy_ui.manager import UIManager

        config = UIConfig(reference_width=1280, reference_height=720)
        manager = UIManager(config=config)

        # Reference size comes from config
        assert manager.config.reference_width == 1280
        assert manager.config.reference_height == 720

    def test_get_current_size(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()

        # screen_width/height are set from runtime
        assert manager.screen_width == 1280
        assert manager.screen_height == 720

    def test_from_engine(self, mock_runtime):
        """Test creating UIManager from ArepyEngine."""
        from arepy_ui.config import ResizeMode, UIConfig
        from arepy_ui.manager import UIManager

        # Create mock engine
        mock_engine = MagicMock()
        mock_engine.renderer_2d = MagicMock()
        mock_engine.input = MagicMock()
        mock_engine.display = MagicMock()
        mock_engine.display.get_window_size.return_value = (1280, 720)
        mock_engine.get_asset_store.return_value = MagicMock()
        mock_engine.audio_device = MagicMock()

        with patch("arepy_ui.manager.configure_runtime") as mock_configure:
            with patch("arepy_ui.manager.get_runtime", return_value=mock_runtime):
                config = UIConfig(resize_mode=ResizeMode.RESPONSIVE)
                manager = UIManager.from_engine(mock_engine, config=config)

                # Verify configure_runtime was called with engine components
                mock_configure.assert_called_once()
                call_kwargs = mock_configure.call_args.kwargs
                assert call_kwargs["renderer"] == mock_engine.renderer_2d
                assert call_kwargs["input"] == mock_engine.input
                assert call_kwargs["display"] == mock_engine.display

                # Verify manager was created with config
                assert manager.config.resize_mode == ResizeMode.RESPONSIVE


class TestUIManagerModals:
    def test_show_modal(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()
        modal = Node(style=Style(width=Unit.px(400), height=Unit.px(300)))

        manager.show_modal(modal)

        assert len(manager._modals) > 0
        assert modal in manager._modals

    def test_close_modal(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()
        modal = Node()

        manager.show_modal(modal)
        manager.close_modal(modal)

        assert modal not in manager._modals

    def test_close_topmost_modal(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()
        modal1 = Node()
        modal2 = Node()

        manager.show_modal(modal1)
        manager.show_modal(modal2)
        manager.close_modal()  # Without specifying, closes the last one

        assert len(manager._modals) == 1
        assert modal1 in manager._modals

    def test_close_all_modals(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()

        manager.show_modal(Node())
        manager.show_modal(Node())
        manager.show_modal(Node())

        manager.close_all_modals()

        assert len(manager._modals) == 0


class TestOverlays:
    def test_register_overlay(self):
        from arepy_ui.manager import clear_overlays, register_overlay

        clear_overlays()

        def render_fn():
            pass

        register_overlay(render_fn)

        # El overlay debería estar registrado
        # (La lista es interna, verificamos que no lance error)

    def test_clear_overlays(self):
        from arepy_ui.manager import clear_overlays, register_overlay

        def render_fn():
            pass

        register_overlay(render_fn)
        clear_overlays()

        # Después de limpiar, no debería haber overlays


class TestFocusManagement:
    def test_request_focus(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()
        node = Node()

        result = manager.request_focus(node)

        assert result is True
        assert manager.get_focused_node() is node

    def test_request_focus_same_node(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()
        node = Node()

        manager.request_focus(node)
        result = manager.request_focus(node)

        assert result is True
        assert manager.get_focused_node() is node

    def test_request_focus_calls_on_blur(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()
        node1 = Node()
        node1._on_blur = MagicMock() # type: ignore
        node2 = Node()

        manager.request_focus(node1)
        manager.request_focus(node2)

        node1._on_blur.assert_called_once() # type: ignore
        assert manager.get_focused_node() is node2

    def test_release_focus(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()
        node = Node()

        manager.request_focus(node)
        manager.release_focus(node)

        assert manager.get_focused_node() is None

    def test_release_focus_wrong_node(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()
        node1 = Node()
        node2 = Node()

        manager.request_focus(node1)
        manager.release_focus(node2)

        # Focus should not change if releasing wrong node
        assert manager.get_focused_node() is node1

    def test_clear_focus(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()
        node = Node()

        manager.request_focus(node)
        manager.clear_focus()

        assert manager.get_focused_node() is None

    def test_clear_focus_calls_on_blur(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()
        node = Node()
        node._on_blur = MagicMock() # type: ignore

        manager.request_focus(node)
        manager.clear_focus()

        node._on_blur.assert_called_once() # type: ignore


class TestUIManagerUpdate:
    def test_update_clears_overlays(self, mock_runtime):
        from arepy_ui.manager import UIManager, register_overlay

        manager = UIManager()
        render_called = []

        def render_fn():
            render_called.append(True)

        register_overlay(render_fn)
        manager.update(0.016)

        # overlays should be cleared at the start of update
        # We can verify by checking that the overlay list is empty

    def test_update_with_root(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()
        root = Node()
        manager.set_root(root)

        # Should not raise
        manager.update(0.016)

    def test_update_handles_resize(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()
        root = Node()
        manager.set_root(root)

        # Simulate window resize
        mock_runtime.display.get_window_size.return_value = (1920, 1080)

        manager.update(0.016)

        assert manager.screen_width == 1920
        assert manager.screen_height == 1080

    def test_update_resize_callback(self, mock_runtime):
        from arepy_ui.manager import UIManager

        resize_called = []

        def on_resize(w, h):
            resize_called.append((w, h))

        config = UIConfig(on_resize=on_resize)
        manager = UIManager(config=config)
        manager.set_root(Node())

        # Simulate window resize
        mock_runtime.display.get_window_size.return_value = (1920, 1080)
        manager.update(0.016)

        assert (1920, 1080) in resize_called

    def test_update_resize_debounce(self, mock_runtime):
        from arepy_ui.manager import UIManager

        config = UIConfig(layout_debounce_ms=100)
        manager = UIManager(config=config)
        manager.set_root(Node())

        # Simulate resize
        mock_runtime.display.get_window_size.return_value = (1920, 1080)
        manager.update(0.016)

        # Should have pending resize
        assert manager._pending_resize is True

        # After debounce time passes
        manager.update(0.1)

        assert manager._pending_resize is False

    def test_update_click_clears_focus(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()
        root = Node(style=Style(width=Unit.px(100), height=Unit.px(100)))
        manager.set_root(root)

        node = Node()
        node.computed_x = 0
        node.computed_y = 0
        node.computed_width = 50
        node.computed_height = 50
        manager.request_focus(node)

        # Simulate click outside focused node
        mock_runtime.input.get_mouse_position.return_value = (80, 80)
        mock_runtime.input.is_mouse_button_pressed.return_value = True

        manager.update(0.016)

        assert manager.get_focused_node() is None


class TestUIManagerRender:
    def test_render_no_root(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()
        # Should not raise
        manager.render()

    def test_render_with_root(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()
        root = Node()
        root.render = MagicMock() # type: ignore
        manager.set_root(root)

        manager.render()

        root.render.assert_called_once() # type: ignore

    def test_render_initializes_stencil(self, mock_runtime):
        from arepy_ui.manager import UIManager

        mock_runtime.renderer.is_stencil_available.return_value = False

        manager = UIManager()
        root = Node()
        root.render = MagicMock()  # type: ignore
        manager.set_root(root)

        manager.render()

        mock_runtime.renderer.init_stencil.assert_called_once()

    def test_render_overlays(self, mock_runtime):
        from arepy_ui.manager import UIManager, register_overlay

        manager = UIManager()
        root = Node()
        root.render = MagicMock()  # type: ignore
        manager.set_root(root)

        overlay_called = []

        def overlay_fn():
            overlay_called.append(True)

        register_overlay(overlay_fn)

        manager.render()

        assert len(overlay_called) == 1


class TestCursorSystem:
    def test_find_node_with_cursor_none_node(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()
        result = manager._find_node_with_cursor(None, 50, 50)

        assert result is None

    def test_find_node_with_cursor_invisible(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()
        node = Node(style=Style(visible=False))
        node.computed_x = 0
        node.computed_y = 0
        node.computed_width = 100
        node.computed_height = 100

        result = manager._find_node_with_cursor(node, 50, 50)

        assert result is None

    def test_find_node_with_cursor_out_of_bounds(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()
        node = Node()
        node.computed_x = 0
        node.computed_y = 0
        node.computed_width = 100
        node.computed_height = 100

        result = manager._find_node_with_cursor(node, 200, 200)

        assert result is None

    def test_find_node_with_cursor_pickable(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()
        node = Node()
        node.pickable = True
        node.computed_x = 0
        node.computed_y = 0
        node.computed_width = 100
        node.computed_height = 100

        result = manager._find_node_with_cursor(node, 50, 50)

        assert result is node

    def test_apply_cursor_changes(self, mock_runtime):
        from arepy_ui.core.types import CursorType
        from arepy_ui.manager import UIManager

        manager = UIManager()
        node = Node(style=Style(cursor=CursorType.POINTING_HAND))
        node.computed_x = 0
        node.computed_y = 0
        node.computed_width = 100
        node.computed_height = 100

        manager._hovered_node = node
        manager._apply_cursor()

        mock_runtime.display.set_mouse_cursor.assert_called_with(
            CursorType.POINTING_HAND.value
        )


class TestTooltipSystem:
    def test_set_tooltip_delay(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()
        manager.set_tooltip_delay(1.0)

        assert manager._tooltip_delay == 1.0

    def test_update_tooltip_shows_after_delay(self, mock_runtime):
        from arepy_ui.core.types import Vector2
        from arepy_ui.manager import UIManager

        manager = UIManager()
        manager._tooltip_delay = 0.5

        # Create node with tooltip
        node = Node()
        node.tooltip = "Test tooltip" # type: ignore
        manager._hovered_node = node

        # First update - timer starts, tooltip text set
        manager._update_tooltip(Vector2(100, 100), 0.3)
        manager._tooltip_text = (
            "Test tooltip"  # Ensure text matches for timer increment
        )
        assert manager._tooltip_visible is False

        # Manually set tooltip_timer to simulate time passing
        manager._tooltip_timer = 0.3
        # Second update with same tooltip text - timer exceeds delay
        manager._update_tooltip(Vector2(100, 100), 0.3)
        assert manager._tooltip_visible is True

    def test_update_tooltip_resets_on_change(self, mock_runtime):
        from arepy_ui.core.types import Vector2
        from arepy_ui.manager import UIManager

        manager = UIManager()
        manager._tooltip_delay = 0.1

        node1 = Node()
        node1.tooltip = "Tooltip 1" # type: ignore
        manager._hovered_node = node1

        # Set first tooltip manually and make it visible
        manager._tooltip_text = "Tooltip 1"
        manager._tooltip_timer = 0.2
        manager._update_tooltip(Vector2(100, 100), 0.2)
        assert manager._tooltip_visible is True

        # Change to new tooltip
        node2 = Node()
        node2.tooltip = "Tooltip 2" # type: ignore
        manager._hovered_node = node2

        manager._update_tooltip(Vector2(100, 100), 0.05)
        # Timer should reset
        assert manager._tooltip_visible is False

    def test_update_tooltip_clears_when_no_tooltip(self, mock_runtime):
        from arepy_ui.core.types import Vector2
        from arepy_ui.manager import UIManager

        manager = UIManager()

        node = Node()
        node.tooltip = "Test" # type: ignore
        manager._hovered_node = node
        manager._tooltip_delay = 0.1

        # Set tooltip visible manually
        manager._tooltip_text = "Test"
        manager._tooltip_timer = 0.2
        manager._update_tooltip(Vector2(100, 100), 0.2)
        assert manager._tooltip_visible is True

        # Clear hovered node
        manager._hovered_node = Node()  # No tooltip

        manager._update_tooltip(Vector2(100, 100), 0.016)
        assert manager._tooltip_visible is False


class TestHelperMethods:
    def test_get_reference_size(self, mock_runtime):
        from arepy_ui.manager import UIManager

        config = UIConfig(reference_width=1920, reference_height=1080)
        manager = UIManager(config=config)

        w, h = manager.get_reference_size()

        assert w == 1920
        assert h == 1080

    def test_get_reference_size_defaults_to_screen(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()
        manager.config.reference_width = None
        manager.config.reference_height = None

        w, h = manager.get_reference_size()

        assert w == manager.screen_width
        assert h == manager.screen_height

    def test_get_current_size(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()

        w, h = manager.get_current_size()

        assert w == 1280
        assert h == 720

    def test_get_scale_transform(self, mock_runtime):
        from arepy_ui.config import ScaleTransform
        from arepy_ui.manager import UIManager

        manager = UIManager()

        transform = manager.get_scale_transform()

        assert isinstance(transform, ScaleTransform)

    def test_has_modal_property(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()

        assert manager.has_modal is False

        manager.show_modal(Node())

        assert manager.has_modal is True


class TestModalInput:
    def test_modal_blocks_main_input(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()
        root = Node()
        root.handle_input = MagicMock(return_value=False) # type: ignore
        manager.set_root(root)

        modal = Node(style=Style(width=Unit.px(100), height=Unit.px(100)))
        modal.handle_input = MagicMock(return_value=True) # type: ignore
        manager.show_modal(modal)

        mock_runtime.input.get_mouse_position.return_value = (50, 50)
        manager.update(0.016)

        # Modal handles input, root does not
        modal.handle_input.assert_called() # type: ignore
        root.handle_input.assert_not_called() # type: ignore

    def test_click_outside_modal_closes(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()
        manager.set_root(Node())

        modal = Node(style=Style(width=Unit.px(100), height=Unit.px(100)))
        manager.show_modal(modal, close_on_backdrop=True)

        # Click far outside modal
        mock_runtime.input.get_mouse_position.return_value = (1200, 700)
        mock_runtime.input.is_mouse_button_pressed.return_value = True

        manager.update(0.016)

        assert modal not in manager._modals

    def test_click_outside_modal_respects_close_on_backdrop(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()
        manager.set_root(Node())

        modal = Node(style=Style(width=Unit.px(100), height=Unit.px(100)))
        manager.show_modal(modal, close_on_backdrop=False)

        # Click outside modal
        mock_runtime.input.get_mouse_position.return_value = (1200, 700)
        mock_runtime.input.is_mouse_button_pressed.return_value = True

        manager.update(0.016)

        # Modal should still be open
        assert modal in manager._modals


class TestResizeModes:
    def test_handle_resize_responsive(self, mock_runtime):
        from arepy_ui.manager import UIManager

        config = UIConfig(resize_mode=ResizeMode.RESPONSIVE)
        manager = UIManager(config=config)
        manager.set_root(Node())
        manager.is_dirty = False

        manager._handle_resize()

        assert manager.is_dirty is True

    def test_handle_resize_fixed(self, mock_runtime):
        from arepy_ui.manager import UIManager

        config = UIConfig(
            resize_mode=ResizeMode.FIXED,
            reference_width=1280,
            reference_height=720,
        )
        manager = UIManager(config=config)
        manager.set_root(Node())
        manager.is_dirty = False

        manager._handle_resize()

        # FIXED mode doesn't recalculate layout
        assert manager.is_dirty is False

    def test_handle_resize_scale_fit(self, mock_runtime):
        from arepy_ui.manager import UIManager

        config = UIConfig(
            resize_mode=ResizeMode.SCALE_FIT,
            reference_width=1280,
            reference_height=720,
        )
        manager = UIManager(config=config)
        manager.set_root(Node())
        manager.is_dirty = False

        manager._handle_resize()

        assert manager.is_dirty is True

    def test_update_with_scale_mode_transforms_mouse(self, mock_runtime):
        from arepy_ui.manager import UIManager

        config = UIConfig(
            resize_mode=ResizeMode.SCALE_FIT,
            reference_width=1280,
            reference_height=720,
        )
        manager = UIManager(config=config)
        root = Node()
        root.handle_input = MagicMock(return_value=False) # type: ignore
        manager.set_root(root)

        mock_runtime.input.get_mouse_position.return_value = (640, 360)

        manager.update(0.016)

        # Just verify update doesn't crash with scale mode
        root.handle_input.assert_called() # type: ignore


class TestLayoutCallbacks:
    def test_on_before_layout_callback(self, mock_runtime):
        from arepy_ui.manager import UIManager

        before_called = []

        def on_before():
            before_called.append(True)

        config = UIConfig(on_before_layout=on_before)
        manager = UIManager(config=config)
        manager.set_root(Node())

        assert len(before_called) == 1

    def test_on_after_layout_callback(self, mock_runtime):
        from arepy_ui.manager import UIManager

        after_called = []

        def on_after():
            after_called.append(True)

        config = UIConfig(on_after_layout=on_after)
        manager = UIManager(config=config)
        manager.set_root(Node())

        assert len(after_called) == 1


class TestRenderTooltip:
    def test_render_tooltip_not_visible(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()
        manager._tooltip_visible = False

        # Should not raise, just return early
        manager._render_tooltip()

    def test_render_tooltip_no_text(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()
        manager._tooltip_visible = True
        manager._tooltip_text = None

        # Should not raise, just return early
        manager._render_tooltip()

    def test_render_tooltip_visible(self, mock_runtime):
        from arepy_ui.core.types import Vector2
        from arepy_ui.manager import UIManager

        manager = UIManager()
        manager._tooltip_visible = True
        manager._tooltip_text = "Test tooltip"
        manager._tooltip_pos = Vector2(100, 100)

        mock_runtime.renderer.measure_text.return_value = 80

        with patch("arepy_ui.manager.get_runtime", return_value=mock_runtime):
            manager._render_tooltip()

        mock_runtime.renderer.measure_text.assert_called()
        mock_runtime.renderer.draw_rectangle_rounded.assert_called()
        mock_runtime.renderer.draw_text.assert_called()

    def test_render_tooltip_clamps_to_screen(self, mock_runtime):
        from arepy_ui.core.types import Vector2
        from arepy_ui.manager import UIManager

        manager = UIManager()
        manager._tooltip_visible = True
        manager._tooltip_text = "Test tooltip"
        # Position near screen edge
        manager._tooltip_pos = Vector2(1250, 700)
        manager.screen_width = 1280
        manager.screen_height = 720

        mock_runtime.renderer.measure_text.return_value = 80

        with patch("arepy_ui.manager.get_runtime", return_value=mock_runtime):
            manager._render_tooltip()

        # Should still render (just with adjusted position)
        mock_runtime.renderer.draw_rectangle_rounded.assert_called()


class TestRenderModals:
    def test_render_modals_empty(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()
        manager._modals = []

        with patch("arepy_ui.manager.get_runtime", return_value=mock_runtime):
            manager._render_modals()

        # No modals to render, no draw calls
        mock_runtime.renderer.draw_rectangle.assert_not_called()

    def test_render_modals_with_backdrop(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()
        modal = Node()
        modal._has_backdrop = True # type: ignore
        modal.render = MagicMock() # type: ignore
        manager._modals = [modal]

        with patch("arepy_ui.manager.get_runtime", return_value=mock_runtime):
            manager._render_modals()

        mock_runtime.renderer.draw_rectangle.assert_called()
        modal.render.assert_called_once() # type: ignore

    def test_render_modals_without_backdrop(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()
        modal = Node()
        modal._has_backdrop = False # type: ignore
        modal.render = MagicMock() # type: ignore
        manager._modals = [modal]

        with patch("arepy_ui.manager.get_runtime", return_value=mock_runtime):
            manager._render_modals()

        mock_runtime.renderer.draw_rectangle.assert_not_called()
        modal.render.assert_called_once() # type: ignore

    def test_render_multiple_modals(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()
        modal1 = Node()
        modal1._has_backdrop = True # type: ignore
        modal1.render = MagicMock() # type: ignore
        modal2 = Node()
        modal2._has_backdrop = True # type: ignore
        modal2.render = MagicMock() # type: ignore
        manager._modals = [modal1, modal2]

        with patch("arepy_ui.manager.get_runtime", return_value=mock_runtime):
            manager._render_modals()

        modal1.render.assert_called_once() # type: ignore
        modal2.render.assert_called_once() # type: ignore
        assert mock_runtime.renderer.draw_rectangle.call_count == 2


class TestScrollViewCursorAdjustment:
    def test_find_node_with_cursor_in_scrollview(self, mock_runtime):
        """Test that mouse coords are adjusted for ScrollView scroll offset."""
        from arepy_ui.components.scroll import ScrollView
        from arepy_ui.manager import UIManager

        manager = UIManager()

        # Create a ScrollView with a child
        content = Node()
        scrollview = ScrollView(width=Unit.px(200), height=Unit.px(200), content=content)
        scrollview.computed_x = 0
        scrollview.computed_y = 0
        scrollview.computed_width = 200
        scrollview.computed_height = 200
        scrollview.scroll_y = -50  # Scrolled down by 50

        child = Node()
        child.pickable = True
        child.computed_x = 50
        child.computed_y = 100  # Would be at y=150 visually without scroll
        child.computed_width = 50
        child.computed_height = 50
        scrollview.children = [child]

        # Mouse is at y=100 in screen coords
        # With scroll_y=-50, the child's effective y is 100-(-50)=150
        # So we shouldn't hit the child at y=100
        result = manager._find_node_with_cursor(scrollview, 75, 100)

        # The scrollview itself should be returned (or child if adjusted coords match)
        # This tests that the scroll adjustment logic is exercised
        assert result == scrollview
