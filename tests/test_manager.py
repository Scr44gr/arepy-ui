"""Tests para arepy_ui.manager"""

from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest
from arepy.ecs.systems import SystemPipeline
from arepy.engine.input import Key
from arepy.engine.time import Time

from arepy_ui.config import ResizeMode, UIConfig
from arepy_ui.core.node import Node
from arepy_ui.core.style import Style
from arepy_ui.core.types import FlexDirection, Unit


def _make_time(delta_seconds: float) -> SimpleNamespace:
    return SimpleNamespace(delta_seconds=delta_seconds)


@pytest.fixture
def mock_runtime():
    """Mock runtime for UIManager tests."""
    mock = MagicMock()
    mock.display.get_window_size.return_value = (1280, 720)
    mock.renderer.get_font_default.return_value = MagicMock()
    mock.renderer.is_stencil_available.return_value = True
    mock.renderer.measure_text_ex.return_value = (100.0, 20.0)
    mock.input.get_mouse_position.return_value = (0, 0)
    mock.input.is_mouse_button_pressed.return_value = False

    with patch("arepy_ui.manager.get_runtime", return_value=mock):
        with patch("arepy_ui.runtime.get_runtime", return_value=mock):
            with patch("arepy_ui.core.node.get_runtime", return_value=mock):
                with patch("arepy_ui.core.fonts.get_runtime", return_value=mock):
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
        assert (
            manager._dirty_layout_root is None
            or manager._dirty_layout_root is manager.root
        )

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

    def test_from_world(self, mock_runtime):
        """Test creating UIManager from a World's shared resources."""
        from arepy_ui.manager import UIManager

        mock_world = MagicMock()
        renderer = MagicMock()
        input_device = MagicMock()
        display = MagicMock()
        asset_store = MagicMock()
        audio_device = MagicMock()

        def get_resource(resource_type):
            resources = {
                "Renderer2D": renderer,
                "Input": input_device,
                "Display": display,
                "AssetStore": asset_store,
                "AudioDevice": audio_device,
            }
            return resources[resource_type.__name__]

        mock_world.get_resource.side_effect = get_resource

        with patch("arepy_ui.manager.configure_runtime") as mock_configure:
            manager = UIManager.from_world(mock_world, config=UIConfig())

        mock_configure.assert_called_once_with(
            renderer=renderer,
            input=input_device,
            display=display,
            asset_store=asset_store,
            audio_device=audio_device,
        )
        assert manager.config is not None

    def test_install_registers_resource_and_systems(self, mock_runtime):
        from arepy_ui.manager import (
            UIManager,
            _world_render_system,
            _world_update_system,
        )

        mock_world = MagicMock()
        renderer = MagicMock()
        input_device = MagicMock()
        display = MagicMock()

        def get_resource(resource_type):
            resources = {
                "Renderer2D": renderer,
                "Input": input_device,
                "Display": display,
            }
            if resource_type.__name__ not in resources:
                raise KeyError(resource_type.__name__)
            return resources[resource_type.__name__]

        mock_world.get_resource.side_effect = get_resource
        root = Node(style=Style(width=Unit.px(100), height=Unit.px(50)))

        manager = UIManager.install(mock_world, root=root, config=UIConfig())

        mock_world.add_resource.assert_called_once_with(manager)
        assert mock_world.add_system.call_count == 2
        assert mock_world.add_system.call_args_list[0].args == (
            SystemPipeline.UPDATE,
            _world_update_system,
        )
        assert mock_world.add_system.call_args_list[1].args == (
            SystemPipeline.RENDER_UI,
            _world_render_system,
        )
        assert manager.root is root

    def test_install_accepts_root_factory_after_runtime_setup(self, mock_runtime):
        from arepy_ui.manager import UIManager

        mock_world = MagicMock()
        renderer = MagicMock()
        input_device = MagicMock()
        display = MagicMock()

        def get_resource(resource_type):
            resources = {
                "Renderer2D": renderer,
                "Input": input_device,
                "Display": display,
            }
            if resource_type.__name__ not in resources:
                raise KeyError(resource_type.__name__)
            return resources[resource_type.__name__]

        mock_world.get_resource.side_effect = get_resource
        created_root = Node(style=Style(width=Unit.px(120), height=Unit.px(60)))
        root_factory = MagicMock(return_value=created_root)

        manager = UIManager.install(mock_world, root=root_factory, config=UIConfig())

        root_factory.assert_called_once_with()
        assert manager.root is created_root

    def test_update_system_uses_injected_time_and_input(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()
        time = _make_time(0.25)
        input_device = MagicMock()
        input_device.get_mouse_wheel_delta.return_value = -2.0

        with patch.object(manager, "update") as mock_update:
            manager.update_system(time, input_device)

        mock_update.assert_called_once_with(0.25, wheel_scroll=-2.0)

    def test_installed_world_system_receives_ui_manager_resources(self, mock_runtime):
        from arepy_ui.manager import UIManager, _world_update_system

        time = Time(0.0)
        time.delta_seconds = 0.5
        input_device = MagicMock()
        input_device.get_mouse_wheel_delta.return_value = 1.25

        manager = UIManager()
        with patch.object(manager, "update") as mock_update:
            _world_update_system(manager, time, input_device)

        mock_update.assert_called_once_with(0.5, wheel_scroll=1.25)

    def test_update_toggles_integrated_debugger_with_default_key(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()
        mock_runtime.input.is_key_pressed.side_effect = lambda key: key == Key.F3

        manager.update(0.016)

        assert manager.get_debugger().enabled is True

    def test_set_font_scale_updates_font_nodes_recursively(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()
        root = Node()
        child = Node()
        root.add_child(child)

        root_node = cast(Any, root)
        child_node = cast(Any, child)

        root_node.font_size = 12.0
        root_node._cached_metrics = object()
        root_node._update_size = MagicMock()
        child_node.font_size = 8.0
        child_node._cached_metrics = object()
        child_node._update_size = MagicMock()

        manager.set_root(root)
        manager.set_font_scale(1.5)

        assert root_node._aui_base_font_size == 12.0
        assert root_node.font_size == 18.0
        assert root_node._cached_metrics is None
        root_node._update_size.assert_called_once()

        assert child_node._aui_base_font_size == 8.0
        assert child_node.font_size == 12.0
        assert child_node._cached_metrics is None
        child_node._update_size.assert_called_once()

    def test_set_debug_toggle_key_uses_custom_key(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()
        manager.set_debug_toggle_key(Key.F2)
        mock_runtime.input.is_key_pressed.side_effect = lambda key: key == Key.F2

        manager.update(0.016)

        assert manager.get_debugger().enabled is True
        assert manager.get_debugger().toggle_hotkey_label == "F2"

    def test_render_calls_integrated_debugger(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()
        root = Node(style=Style(width=Unit.px(100), height=Unit.px(60)))
        manager.set_root(root)
        manager.enable_debug_overlay(True)
        manager.get_debugger().render = MagicMock()  # type: ignore

        with patch("arepy_ui.core.node.get_runtime", return_value=mock_runtime):
            manager.render()

        manager.get_debugger().render.assert_called_once_with(root)  # type: ignore

    def test_config_can_start_with_debug_enabled(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager(UIConfig(debug_enabled=True))

        assert manager.get_debugger().enabled is True

    def test_debugger_props_handle_video_string_state(self, mock_runtime):
        from arepy_ui.components.video import Video, VideoState
        from arepy_ui.manager import UIManager

        manager = UIManager()
        video = Video(source="demo.mp4", controls=False)
        video._state = VideoState.PLAYING
        video._duration = 12.34

        props = manager.get_debugger()._get_component_props(video)

        assert "state: playing" in props
        assert "duration: 12.3s" in props

    def test_debugger_frame_tracks_scrollview_visual_offset(self, mock_runtime):
        from arepy_ui.components.scroll import ScrollView
        from arepy_ui.manager import UIManager

        manager = UIManager()

        child = Node(style=Style(width=Unit.px(80), height=Unit.px(40)))
        content = Node(
            style=Style(
                width=Unit.px(200),
                height=Unit.px(400),
            ),
            children=[child],
        )
        scrollview = ScrollView(
            width=Unit.px(200),
            height=Unit.px(120),
            content=content,
        )

        manager.set_root(scrollview)
        scrollview.scroll_y = -50
        content.computed_x = 0
        content.computed_y = 0
        content.computed_width = 200
        content.computed_height = 400
        child.computed_x = 10
        child.computed_y = 90
        child.computed_width = 80
        child.computed_height = 40

        debugger = manager.get_debugger()
        debugger._build_frame(scrollview)
        frame = debugger._frame_index[child]

        assert frame.rect == (10, 40, 80, 40)
        assert frame.visible_rect == (10, 40, 80, 40)

    def test_debugger_hover_respects_scrollview_clip(self, mock_runtime):
        from arepy_ui.components.scroll import ScrollView
        from arepy_ui.manager import UIManager

        manager = UIManager()

        child = Node(style=Style(width=Unit.px(100), height=Unit.px(40)))
        content = Node(style=Style(width=Unit.px(200), height=Unit.px(300)))
        content.add_child(child)
        scrollview = ScrollView(
            width=Unit.px(200),
            height=Unit.px(100),
            content=content,
        )

        manager.set_root(scrollview)
        scrollview.scroll_y = -30
        content.computed_x = 0
        content.computed_y = 0
        content.computed_width = 200
        content.computed_height = 300
        child.computed_x = 0
        child.computed_y = 100
        child.computed_width = 100
        child.computed_height = 40

        debugger = manager.get_debugger()
        debugger._build_frame(scrollview)

        assert debugger._frame_index[child].visible_rect == (0, 70, 100, 30)
        assert debugger._find_node_at(10, 95) == child
        assert debugger._find_node_at(150, 95) == content


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
        node1._on_blur = MagicMock()  # type: ignore
        node2 = Node()

        manager.request_focus(node1)
        manager.request_focus(node2)

        node1._on_blur.assert_called_once()  # type: ignore
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
        node._on_blur = MagicMock()  # type: ignore

        manager.request_focus(node)
        manager.clear_focus()

        node._on_blur.assert_called_once()  # type: ignore


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

        config = UIConfig(layout_debounce_ms=100, resize_mode=ResizeMode.RESPONSIVE)
        manager = UIManager(config=config)
        root = Node(style=Style(width=Unit.vw(50), height=Unit.vh(25)))
        manager.set_root(root)

        assert root.computed_width == 640
        assert root.computed_height == 180

        # Simulate resize
        mock_runtime.display.get_window_size.return_value = (1920, 1080)
        manager.update(0.016)

        # Layout should still be debounced
        assert root.computed_width == 640
        assert root.computed_height == 180

        # After debounce time passes
        manager.update(0.1)

        assert root.computed_width == 960
        assert root.computed_height == 270


class TestUIManagerPartialLayout:
    def test_mark_dirty_node_merges_to_common_ancestor(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()
        root = Node()
        left = Node()
        right = Node()
        left_child = Node()
        right_child = Node()

        root.add_child(left)
        root.add_child(right)
        left.add_child(left_child)
        right.add_child(right_child)

        manager.set_root(root)
        manager.mark_dirty_node(left)
        manager.mark_dirty_node(right)

        assert manager._dirty_layout_root is root

    def test_recalculate_layout_uses_partial_root_when_available(self, mock_runtime):
        from arepy_ui.manager import UIManager

        class CountingNode(Node):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.layout_calls = 0

            def calculate_layout(self, parent_x, parent_y, parent_width, parent_height):
                self.layout_calls += 1
                return super().calculate_layout(
                    parent_x, parent_y, parent_width, parent_height
                )

        manager = UIManager()
        root = CountingNode(style=Style(width=Unit.px(800), height=Unit.px(600)))
        container = CountingNode(style=Style(width=Unit.px(200), height=Unit.px(100)))
        child = CountingNode(style=Style(width=Unit.px(50), height=Unit.px(20)))
        sibling = CountingNode(style=Style(width=Unit.px(60), height=Unit.px(20)))

        root.add_child(container)
        root.add_child(sibling)
        container.add_child(child)

        manager.set_root(root)

        root.layout_calls = 0
        container.layout_calls = 0
        child.layout_calls = 0
        sibling.layout_calls = 0

        child.mark_dirty()
        manager._recalculate_layout()

        assert root.layout_calls == 0
        assert container.layout_calls == 1
        assert child.layout_calls == 1
        assert sibling.layout_calls == 0

    def test_partial_relayout_preserves_final_flex_position(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()
        root = Node(
            style=Style(
                width=Unit.px(200),
                height=Unit.px(200),
                flex_direction=FlexDirection.COLUMN,
                gap=10,
            )
        )
        first = Node(style=Style(width=Unit.px(50), height=Unit.px(50)))
        second = Node(style=Style(width=Unit.px(50), height=Unit.px(50)))

        root.add_child(first)
        root.add_child(second)

        manager.set_root(root)

        assert second.computed_y == 60

        manager.mark_dirty_node(second)
        manager._recalculate_layout()

        assert second.computed_y == 60

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
        root.render = MagicMock()  # type: ignore
        manager.set_root(root)

        manager.render()

        root.render.assert_called_once()  # type: ignore

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
        node.tooltip = "Test tooltip"  # type: ignore
        manager._hovered_node = node

        manager._update_tooltip(Vector2(100, 100))
        assert manager._tooltip_visible is False

        manager.timers.update(0.3)
        assert manager._tooltip_visible is False

        manager.timers.update(0.3)
        assert manager._tooltip_visible is True

    def test_update_tooltip_resets_on_change(self, mock_runtime):
        from arepy_ui.core.types import Vector2
        from arepy_ui.manager import UIManager

        manager = UIManager()
        manager._tooltip_delay = 0.1

        node1 = Node()
        node1.tooltip = "Tooltip 1"  # type: ignore
        manager._hovered_node = node1

        manager._update_tooltip(Vector2(100, 100))
        manager.timers.update(0.2)
        assert manager._tooltip_visible is True

        # Change to new tooltip
        node2 = Node()
        node2.tooltip = "Tooltip 2"  # type: ignore
        manager._hovered_node = node2

        manager._update_tooltip(Vector2(100, 100))
        assert manager._tooltip_visible is False

        manager.timers.update(0.05)
        assert manager._tooltip_visible is False

    def test_update_tooltip_clears_when_no_tooltip(self, mock_runtime):
        from arepy_ui.core.types import Vector2
        from arepy_ui.manager import UIManager

        manager = UIManager()

        node = Node()
        node.tooltip = "Test"  # type: ignore
        manager._hovered_node = node
        manager._tooltip_delay = 0.1

        manager._update_tooltip(Vector2(100, 100))
        manager.timers.update(0.2)
        assert manager._tooltip_visible is True

        # Clear hovered node
        manager._hovered_node = Node()  # No tooltip

        manager._update_tooltip(Vector2(100, 100))
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
        root.handle_input = MagicMock(return_value=False)  # type: ignore
        manager.set_root(root)

        modal = Node(style=Style(width=Unit.px(100), height=Unit.px(100)))
        modal.handle_input = MagicMock(return_value=True)  # type: ignore
        manager.show_modal(modal)

        mock_runtime.input.get_mouse_position.return_value = (50, 50)
        manager.update(0.016)

        # Modal handles input, root does not
        modal.handle_input.assert_called()  # type: ignore
        root.handle_input.assert_not_called()  # type: ignore

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
        assert manager._dirty_layout_root is manager.root

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
        assert manager._dirty_layout_root is manager.root

    def test_handle_resize_overrides_partial_dirty_root(self, mock_runtime):
        from arepy_ui.manager import UIManager

        config = UIConfig(resize_mode=ResizeMode.RESPONSIVE)
        manager = UIManager(config=config)
        root = Node()
        child = Node()
        root.add_child(child)
        manager.set_root(root)

        manager.mark_dirty_node(child)
        assert manager._dirty_layout_root is child

        manager._handle_resize()

        assert manager.is_dirty is True
        assert manager._dirty_layout_root is root

    def test_update_with_scale_mode_transforms_mouse(self, mock_runtime):
        from arepy_ui.manager import UIManager

        config = UIConfig(
            resize_mode=ResizeMode.SCALE_FIT,
            reference_width=1280,
            reference_height=720,
        )
        manager = UIManager(config=config)
        root = Node()
        root.handle_input = MagicMock(return_value=False)  # type: ignore
        manager.set_root(root)

        mock_runtime.input.get_mouse_position.return_value = (640, 360)

        manager.update(0.016)

        # Just verify update doesn't crash with scale mode
        root.handle_input.assert_called()  # type: ignore

    def test_resize_updates_viewport_units_layout(self, mock_runtime):
        from arepy_ui.manager import UIManager
        from unittest.mock import patch

        with patch("arepy_ui.core.node.get_runtime", return_value=mock_runtime):
            config = UIConfig(resize_mode=ResizeMode.RESPONSIVE)
            manager = UIManager(config=config)
            root = Node(style=Style(width=Unit.vw(50), height=Unit.vh(25)))
            manager.set_root(root)

            assert root.computed_width == 640
            assert root.computed_height == 180

            mock_runtime.display.get_window_size.return_value = (1920, 1080)
            manager.update(0.016)

            assert root.computed_width == 960
            assert root.computed_height == 270


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
        modal._has_backdrop = True  # type: ignore
        modal.render = MagicMock()  # type: ignore
        manager._modals = [modal]

        with patch("arepy_ui.manager.get_runtime", return_value=mock_runtime):
            manager._render_modals()

        mock_runtime.renderer.draw_rectangle.assert_called()
        modal.render.assert_called_once()  # type: ignore

    def test_render_modals_without_backdrop(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()
        modal = Node()
        modal._has_backdrop = False  # type: ignore
        modal.render = MagicMock()  # type: ignore
        manager._modals = [modal]

        with patch("arepy_ui.manager.get_runtime", return_value=mock_runtime):
            manager._render_modals()

        mock_runtime.renderer.draw_rectangle.assert_not_called()
        modal.render.assert_called_once()  # type: ignore

    def test_render_multiple_modals(self, mock_runtime):
        from arepy_ui.manager import UIManager

        manager = UIManager()
        modal1 = Node()
        modal1._has_backdrop = True  # type: ignore
        modal1.render = MagicMock()  # type: ignore
        modal2 = Node()
        modal2._has_backdrop = True  # type: ignore
        modal2.render = MagicMock()  # type: ignore
        manager._modals = [modal1, modal2]

        with patch("arepy_ui.manager.get_runtime", return_value=mock_runtime):
            manager._render_modals()

        modal1.render.assert_called_once()  # type: ignore
        modal2.render.assert_called_once()  # type: ignore
        assert mock_runtime.renderer.draw_rectangle.call_count == 2


class TestScrollViewCursorAdjustment:
    def test_find_node_with_cursor_in_scrollview(self, mock_runtime):
        """Test that mouse coords are adjusted for ScrollView scroll offset."""
        from arepy_ui.components.scroll import ScrollView
        from arepy_ui.manager import UIManager

        manager = UIManager()

        # Create a ScrollView with a child
        content = Node()
        scrollview = ScrollView(
            width=Unit.px(200), height=Unit.px(200), content=content
        )
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
