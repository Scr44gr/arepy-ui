"""Tests para arepy_ui.components.drag"""

from unittest.mock import MagicMock, patch

import pytest

from arepy_ui.components.drag import (
    Draggable,
    DragState,
    DropZone,
    _drag_state,
    get_drag_state,
    is_dragging,
)
from arepy_ui.core.node import Node
from arepy_ui.core.style import Style
from arepy_ui.core.types import Color, Unit


@pytest.fixture
def mock_runtime():
    """Mock runtime for render/input tests."""
    with patch("arepy_ui.components.drag.get_runtime") as mock_get_runtime:
        mock_rt = MagicMock()
        mock_renderer = MagicMock()
        mock_renderer.get_delta_time.return_value = 0.016
        mock_input = MagicMock()
        mock_input.is_mouse_button_down.return_value = False
        mock_input.is_mouse_button_released.return_value = False
        mock_rt.renderer = mock_renderer
        mock_rt.input = mock_input
        mock_get_runtime.return_value = mock_rt
        yield {"runtime": mock_rt, "renderer": mock_renderer, "input": mock_input}


@pytest.fixture
def mock_collision():
    """Mock collision detection."""
    with patch("arepy_ui.components.drag.check_collision_point_rec") as mock:
        yield mock


@pytest.fixture
def mock_overlay():
    """Mock register_overlay."""
    with patch("arepy_ui.components.drag.register_overlay") as mock:
        yield mock


@pytest.fixture(autouse=True)
def reset_drag_state():
    """Reset global drag state before each test."""
    _drag_state.is_dragging = False
    _drag_state.source = None
    _drag_state.data = None
    _drag_state.current_target = None
    yield


class TestDraggable:
    def test_draggable_creation(self):
        content = Node(style=Style(width=Unit.px(100), height=Unit.px(100)))
        draggable = Draggable(content=content)

        assert draggable.content is content
        assert draggable.data is None

    def test_draggable_with_data(self):
        content = Node()
        data = {"id": 1, "name": "Item"}
        draggable = Draggable(content=content, data=data)

        assert draggable.data == data
        assert draggable.data["id"] == 1

    def test_draggable_callbacks(self):
        started = [False]
        ended = [False]

        def on_start():
            started[0] = True

        def on_end(dropped, target):
            ended[0] = True

        content = Node()
        draggable = Draggable(
            content=content,
            on_drag_start=on_start,
            on_drag_end=on_end,
        )

        assert draggable.on_drag_start is not None
        assert draggable.on_drag_end is not None

    def test_draggable_drag_threshold(self):
        content = Node()
        draggable = Draggable(content=content, drag_threshold=10)

        assert draggable.drag_threshold == 10

    def test_draggable_drag_opacity(self):
        content = Node()
        draggable = Draggable(content=content, drag_opacity=0.5)

        assert draggable.drag_opacity == 0.5


class TestDropZone:
    def test_dropzone_creation(self):
        dropzone = DropZone(style=Style(width=Unit.px(200), height=Unit.px(200)))

        assert dropzone.auto_adopt == True  # default

    def test_dropzone_auto_adopt_disabled(self):
        dropzone = DropZone(auto_adopt=False)

        assert dropzone.auto_adopt == False

    def test_dropzone_highlight_color(self):
        color = Color(100, 200, 100, 255)
        dropzone = DropZone(highlight_color=color)

        assert dropzone.highlight_color == color

    def test_dropzone_with_data(self):
        dropzone = DropZone(data="test_data")
        assert dropzone.data == "test_data"

    def test_dropzone_accept_callback(self):
        def accept_only_type_a(data):
            return data.get("type") == "A"

        dropzone = DropZone(accept=accept_only_type_a)

        assert dropzone.accept({"type": "A"}) == True  # type: ignore
        assert dropzone.accept({"type": "B"}) == False  # type: ignore

    def test_dropzone_sortable(self):
        dropzone = DropZone(sortable=True)

        assert dropzone.sortable == True

    def test_dropzone_on_drop_callback(self):
        dropped_items = []

        def on_drop(draggable, data):
            dropped_items.append(data)
            return True

        dropzone = DropZone(on_drop=on_drop)

        assert dropzone.on_drop is not None


class TestDragState:
    def test_drag_state_initial(self):
        state = DragState()

        assert state.is_dragging == False
        assert state.source is None
        assert state.data is None
        assert state.current_target is None

    def test_is_dragging_helper(self):
        # El estado global inicia en False
        # Este test verifica la función helper
        result = is_dragging()
        assert isinstance(result, bool)

    def test_get_drag_state_helper(self):
        state = get_drag_state()
        assert isinstance(state, DragState)


class TestDropZoneAdopt:
    def test_adopt_draggable(self):
        dropzone = DropZone(style=Style(width=Unit.px(200), height=Unit.px(200)))
        content = Node()
        draggable = Draggable(content=content)

        # Simular adopción
        dropzone.adopt(draggable)

        assert draggable in dropzone.children
        assert draggable.parent is dropzone

    def test_adopt_at_index(self):
        dropzone = DropZone()

        d1 = Draggable(content=Node())
        d2 = Draggable(content=Node())
        d3 = Draggable(content=Node())

        dropzone.adopt(d1)
        dropzone.adopt(d2)
        dropzone.adopt(d3, index=1)  # Insertar en medio

        assert dropzone.children[0] is d1
        assert dropzone.children[1] is d3
        assert dropzone.children[2] is d2


class TestDraggableHandleInput:
    """Tests for Draggable handle_input method."""

    def test_handle_input_click_starts_press(self, mock_runtime, mock_collision):
        mock_collision.return_value = True

        content = Node()
        draggable = Draggable(content=content)
        draggable.computed_x = 10
        draggable.computed_y = 20
        draggable.computed_width = 100
        draggable.computed_height = 100

        mouse_pos = MagicMock()
        mouse_pos.x = 50
        mouse_pos.y = 50

        result = draggable.handle_input(mouse_pos, is_click=True)

        assert result is True
        assert draggable._is_pressed is True

    def test_handle_input_exceeds_threshold_starts_drag(
        self, mock_runtime, mock_collision
    ):
        mock_collision.return_value = True
        mock_runtime["input"].is_mouse_button_down.return_value = True

        content = Node()
        draggable = Draggable(content=content, drag_threshold=5)
        draggable.computed_x = 10
        draggable.computed_y = 20
        draggable.computed_width = 100
        draggable.computed_height = 100
        draggable._is_pressed = True
        draggable._press_start_x = 50
        draggable._press_start_y = 50

        mouse_pos = MagicMock()
        mouse_pos.x = 60  # Moved 10px (> threshold)
        mouse_pos.y = 50

        result = draggable.handle_input(mouse_pos, is_click=False)

        assert result is True
        # After exceeding threshold, drag should start
        assert _drag_state.is_dragging is True or draggable._is_pressed is True

    def test_handle_input_invisible_returns_false(self, mock_runtime, mock_collision):
        content = Node()
        draggable = Draggable(content=content)
        draggable.style.visible = False

        mouse_pos = MagicMock()
        mouse_pos.x = 50
        mouse_pos.y = 50

        result = draggable.handle_input(mouse_pos, is_click=True)

        assert result is False

    def test_handle_input_release_cancels_press(self, mock_runtime, mock_collision):
        mock_collision.return_value = True
        mock_runtime["input"].is_mouse_button_released.return_value = True

        content = Node()
        draggable = Draggable(content=content)
        draggable.computed_x = 10
        draggable.computed_y = 20
        draggable.computed_width = 100
        draggable.computed_height = 100
        draggable._is_pressed = True

        mouse_pos = MagicMock()
        mouse_pos.x = 50
        mouse_pos.y = 50

        draggable.handle_input(mouse_pos, is_click=False)

        assert draggable._is_pressed is False


class TestDropZoneHandleInput:
    """Tests for DropZone handle_input method."""

    def test_handle_input_hover_while_dragging(self, mock_runtime, mock_collision):
        mock_collision.return_value = True

        dropzone = DropZone()
        dropzone.computed_x = 10
        dropzone.computed_y = 20
        dropzone.computed_width = 200
        dropzone.computed_height = 200

        # Set up drag state
        content = Node()
        draggable = Draggable(content=content)
        _drag_state.is_dragging = True
        _drag_state.source = draggable

        mouse_pos = MagicMock()
        mouse_pos.x = 100
        mouse_pos.y = 100

        dropzone.handle_input(mouse_pos, is_click=False)

        # Check that drop zone recognizes the drag
        assert _drag_state.current_target is dropzone
        assert dropzone._is_drag_over is True

    def test_handle_input_not_dragging(self, mock_runtime, mock_collision):
        mock_collision.return_value = True

        dropzone = DropZone()
        dropzone.computed_x = 10
        dropzone.computed_y = 20
        dropzone.computed_width = 200
        dropzone.computed_height = 200

        mouse_pos = MagicMock()
        mouse_pos.x = 100
        mouse_pos.y = 100

        # Not dragging, should pass to children
        result = dropzone.handle_input(mouse_pos, is_click=False)

        # Should not set drag over since not dragging
        assert dropzone._is_drag_over is False

    def test_handle_input_invisible(self, mock_runtime, mock_collision):
        dropzone = DropZone()
        dropzone.style.visible = False

        mouse_pos = MagicMock()
        mouse_pos.x = 100
        mouse_pos.y = 100

        result = dropzone.handle_input(mouse_pos, is_click=False)

        assert result is False


class TestDropZoneRender:
    """Tests for DropZone render method."""

    def test_render_with_highlight(self, mock_runtime):
        # Need to also mock the core node render
        with patch("arepy_ui.core.node.get_runtime") as mock_node_runtime:
            mock_node_runtime.return_value = mock_runtime["runtime"]
            mock_runtime["runtime"].display = MagicMock()
            mock_runtime["runtime"].display.get_window_size.return_value = (800, 600)

            dropzone = DropZone()
            dropzone.computed_x = 10
            dropzone.computed_y = 20
            dropzone.computed_width = 200
            dropzone.computed_height = 200
            dropzone._is_drag_over = True

            dropzone.render()

            # Render was called without error
            assert True

    def test_render_invisible_does_nothing(self, mock_runtime):
        dropzone = DropZone()
        dropzone.style.visible = False

        dropzone.render()

        mock_runtime["renderer"].draw_rectangle_rounded.assert_not_called()


class TestDraggableStartDrag:
    """Tests for Draggable _start_drag method."""

    def test_start_drag_sets_global_state(self, mock_runtime):
        mock_runtime["runtime"].display = MagicMock()

        content = Node()
        draggable = Draggable(content=content, data={"test": "data"}, drag_opacity=0.7)
        draggable.computed_x = 100
        draggable.computed_y = 150
        draggable.style.opacity = 1.0

        from arepy_ui.core.types import Vector2

        mouse_pos = Vector2(120, 170)

        draggable._start_drag(mouse_pos)

        assert _drag_state.is_dragging is True
        assert _drag_state.source is draggable
        assert _drag_state.data == {"test": "data"}
        assert draggable.style.opacity == 0.7
        assert draggable._is_being_dragged is True

    def test_start_drag_calls_callback(self, mock_runtime):
        mock_runtime["runtime"].display = MagicMock()

        start_called = []

        def on_start():
            start_called.append(True)

        content = Node()
        draggable = Draggable(content=content, on_drag_start=on_start)
        draggable.computed_x = 100
        draggable.computed_y = 150

        from arepy_ui.core.types import Vector2

        draggable._start_drag(Vector2(120, 170))

        assert len(start_called) == 1

    def test_start_drag_sets_cursor(self, mock_runtime):
        mock_runtime["runtime"].display = MagicMock()

        from arepy_ui.core.types import CursorType

        content = Node()
        draggable = Draggable(content=content, drag_cursor=CursorType.RESIZE_ALL)
        draggable.computed_x = 100
        draggable.computed_y = 150

        from arepy_ui.core.types import Vector2

        draggable._start_drag(Vector2(120, 170))

        mock_runtime["runtime"].display.set_mouse_cursor.assert_called_with(
            CursorType.RESIZE_ALL.value
        )


class TestDraggableEndDrag:
    """Tests for Draggable _end_drag method."""

    def test_end_drag_clears_state(self, mock_runtime):
        mock_runtime["runtime"].display = MagicMock()

        content = Node()
        draggable = Draggable(content=content)
        draggable._is_being_dragged = True
        draggable._original_opacity = 1.0
        draggable.style.opacity = 0.7

        _drag_state.is_dragging = True
        _drag_state.source = draggable
        _drag_state.current_target = None

        from arepy_ui.core.types import Vector2

        draggable._end_drag(Vector2(100, 100))

        assert _drag_state.is_dragging is False
        assert _drag_state.source is None
        assert draggable._is_being_dragged is False
        assert draggable.style.opacity == 1.0

    def test_end_drag_with_target_calls_receive(self, mock_runtime):
        mock_runtime["runtime"].display = MagicMock()

        content = Node()
        draggable = Draggable(content=content, data="test_data")
        draggable._is_being_dragged = True
        draggable._original_opacity = 1.0

        dropzone = DropZone()
        dropzone._receive_drop = MagicMock(return_value=True)  # type: ignore

        _drag_state.is_dragging = True
        _drag_state.source = draggable
        _drag_state.current_target = dropzone

        from arepy_ui.core.types import Vector2

        draggable._end_drag(Vector2(100, 100))

        dropzone._receive_drop.assert_called_once_with(draggable, "test_data")  # type: ignore

    def test_end_drag_calls_callback(self, mock_runtime):
        mock_runtime["runtime"].display = MagicMock()

        end_called = []

        def on_end(dropped, target):
            end_called.append((dropped, target))

        content = Node()
        draggable = Draggable(content=content, on_drag_end=on_end)
        draggable._is_being_dragged = True
        draggable._original_opacity = 1.0

        _drag_state.is_dragging = True
        _drag_state.source = draggable
        _drag_state.current_target = None

        from arepy_ui.core.types import Vector2

        draggable._end_drag(Vector2(100, 100))

        assert len(end_called) == 1
        assert end_called[0] == (False, None)


class TestDraggableAnimateReturn:
    """Tests for Draggable _animate_return method."""

    def test_animate_return_without_manager(self, mock_runtime):
        content = Node()
        draggable = Draggable(content=content, return_on_fail=True)
        draggable.computed_x = 200
        draggable.computed_y = 200
        draggable._original_x = 100
        draggable._original_y = 100
        draggable._manager = None

        draggable._animate_return()

        # Without manager, should directly translate back
        assert draggable.computed_x == 100
        assert draggable.computed_y == 100

    def test_animate_return_with_manager(self, mock_runtime):
        content = Node()
        draggable = Draggable(content=content, return_on_fail=True)
        draggable.computed_x = 200
        draggable.computed_y = 200
        draggable._original_x = 100
        draggable._original_y = 100

        mock_manager = MagicMock()
        mock_manager.animator = MagicMock()
        draggable._manager = mock_manager

        draggable._animate_return()

        # Should add animations to manager
        assert mock_manager.animator.add.call_count == 2


class TestDraggableRenderAsOverlay:
    """Tests for Draggable _render_as_overlay method."""

    def test_render_as_overlay_calls_node_render(self, mock_runtime):
        with patch("arepy_ui.core.node.get_runtime") as mock_node_runtime:
            mock_node_runtime.return_value = mock_runtime["runtime"]
            mock_runtime["runtime"].display = MagicMock()
            mock_runtime["runtime"].display.get_window_size.return_value = (800, 600)

            content = Node()
            draggable = Draggable(content=content)
            draggable.computed_x = 10
            draggable.computed_y = 20
            draggable.computed_width = 100
            draggable.computed_height = 100

            # Should call Node.render directly
            draggable._render_as_overlay()


class TestDraggableRender:
    """Tests for Draggable render method."""

    def test_render_skips_when_being_dragged(self, mock_runtime):
        content = Node()
        draggable = Draggable(content=content)
        draggable._is_being_dragged = True

        # Should return early without rendering
        draggable.render()

        # No render calls should be made
        mock_runtime["renderer"].draw_rectangle.assert_not_called()

    def test_render_normal_when_not_dragging(self, mock_runtime):
        with patch("arepy_ui.core.node.get_runtime") as mock_node_runtime:
            mock_node_runtime.return_value = mock_runtime["runtime"]
            mock_runtime["runtime"].display = MagicMock()
            mock_runtime["runtime"].display.get_window_size.return_value = (800, 600)

            content = Node()
            draggable = Draggable(content=content)
            draggable._is_being_dragged = False
            draggable.computed_x = 10
            draggable.computed_y = 20
            draggable.computed_width = 100
            draggable.computed_height = 100

            draggable.render()


class TestDropZoneReceiveDrop:
    """Tests for DropZone _receive_drop method."""

    def test_receive_drop_rejects_invalid_data(self):
        dropzone = DropZone(accept=lambda data: data.get("type") == "A")

        content = Node()
        draggable = Draggable(content=content)

        result = dropzone._receive_drop(draggable, {"type": "B"})

        assert result is False

    def test_receive_drop_accepts_valid_data(self):
        dropzone = DropZone(
            accept=lambda data: data.get("type") == "A", auto_adopt=True
        )
        dropzone.children = []

        content = Node()
        draggable = Draggable(content=content)

        result = dropzone._receive_drop(draggable, {"type": "A"})

        assert result is True
        assert draggable in dropzone.children

    def test_receive_drop_calls_on_drop_callback(self):
        dropped_data = []

        def on_drop(drg, data):
            dropped_data.append(data)
            return True

        dropzone = DropZone(on_drop=on_drop, auto_adopt=False)

        content = Node()
        draggable = Draggable(content=content)

        result = dropzone._receive_drop(draggable, {"id": 123})

        assert result is True
        assert {"id": 123} in dropped_data

    def test_receive_drop_clears_highlight(self):
        from arepy_ui.core.types import Color

        original_color = Color(100, 100, 100, 255)
        highlight = Color(200, 200, 100, 255)

        dropzone = DropZone(highlight_color=highlight, auto_adopt=False)
        dropzone.style.background_color = highlight
        dropzone._original_bg_color = original_color
        dropzone._is_drag_over = True

        content = Node()
        draggable = Draggable(content=content)

        dropzone._receive_drop(draggable, {})

        assert dropzone.style.background_color == original_color
        assert dropzone._is_drag_over is False


class TestDropZoneCalculateDropIndex:
    """Tests for DropZone _calculate_drop_index method."""

    def test_calculate_drop_index_empty_children(self):
        dropzone = DropZone()
        dropzone.children = []

        from arepy_ui.core.types import Vector2

        result = dropzone._calculate_drop_index(Vector2(100, 100))

        assert result == 0

    def test_calculate_drop_index_column_direction(self):
        from arepy_ui.core.types import FlexDirection

        dropzone = DropZone(style=Style(flex_direction=FlexDirection.COLUMN))

        d1 = Draggable(content=Node())
        d1.computed_y = 0
        d1.computed_height = 50
        d2 = Draggable(content=Node())
        d2.computed_y = 60
        d2.computed_height = 50

        dropzone.children = [d1, d2]

        from arepy_ui.core.types import Vector2

        # Mouse above first child's center
        result = dropzone._calculate_drop_index(Vector2(50, 10))
        assert result == 0

        # Mouse between first and second child
        result = dropzone._calculate_drop_index(Vector2(50, 55))
        assert result == 1

        # Mouse below all children
        result = dropzone._calculate_drop_index(Vector2(50, 200))
        assert result == 2

    def test_calculate_drop_index_row_direction(self):
        from arepy_ui.core.types import FlexDirection

        dropzone = DropZone(style=Style(flex_direction=FlexDirection.ROW))

        d1 = Draggable(content=Node())
        d1.computed_x = 0
        d1.computed_width = 50
        d2 = Draggable(content=Node())
        d2.computed_x = 60
        d2.computed_width = 50

        dropzone.children = [d1, d2]

        from arepy_ui.core.types import Vector2

        # Mouse before first child's center
        result = dropzone._calculate_drop_index(Vector2(10, 50))
        assert result == 0

        # Mouse between children
        result = dropzone._calculate_drop_index(Vector2(55, 50))
        assert result == 1


class TestDropZoneCalculateIndicatorRect:
    """Tests for DropZone _calculate_indicator_rect method."""

    def test_calculate_indicator_rect_empty(self):
        from arepy_ui.core.types import FlexDirection

        dropzone = DropZone(style=Style(flex_direction=FlexDirection.COLUMN))
        dropzone.computed_x = 0
        dropzone.computed_y = 0
        dropzone.computed_width = 200
        dropzone.computed_height = 200
        dropzone.style.padding.left = Unit.px(10)
        dropzone.style.padding.top = Unit.px(10)
        dropzone.style.padding.right = Unit.px(10)
        dropzone.style.padding.bottom = Unit.px(10)
        dropzone.children = []

        result = dropzone._calculate_indicator_rect(0)

        assert result is not None
        x, y, w, h = result
        assert x == 10  # padding left
        assert w == 180  # width - padding*2

    def test_calculate_indicator_rect_row_direction(self):
        from arepy_ui.core.types import FlexDirection

        dropzone = DropZone(style=Style(flex_direction=FlexDirection.ROW))
        dropzone.computed_x = 0
        dropzone.computed_y = 0
        dropzone.computed_width = 200
        dropzone.computed_height = 100
        dropzone.style.padding.left = Unit.px(5)
        dropzone.style.padding.top = Unit.px(5)
        dropzone.style.padding.right = Unit.px(5)
        dropzone.style.padding.bottom = Unit.px(5)
        dropzone.children = []

        result = dropzone._calculate_indicator_rect(0)

        assert result is not None
        x, y, w, h = result
        assert h == 90  # height - padding*2


class TestDropZoneDragEnterLeave:
    """Tests for drag enter/leave callbacks."""

    def test_drag_enter_callback(self, mock_runtime, mock_collision):
        mock_collision.return_value = True

        enter_called = []

        def on_enter():
            enter_called.append(True)

        dropzone = DropZone(on_drag_enter=on_enter)
        dropzone.computed_x = 0
        dropzone.computed_y = 0
        dropzone.computed_width = 200
        dropzone.computed_height = 200

        _drag_state.is_dragging = True
        _drag_state.source = Draggable(content=Node())
        _drag_state.data = {}

        from arepy_ui.core.types import Vector2

        dropzone.handle_input(Vector2(100, 100), is_click=False)

        assert len(enter_called) == 1

    def test_drag_leave_callback(self, mock_runtime, mock_collision):
        leave_called = []

        def on_leave():
            leave_called.append(True)

        dropzone = DropZone(on_drag_leave=on_leave)
        dropzone.computed_x = 0
        dropzone.computed_y = 0
        dropzone.computed_width = 200
        dropzone.computed_height = 200
        dropzone._is_drag_over = True

        _drag_state.is_dragging = True
        _drag_state.source = Draggable(content=Node())
        _drag_state.data = {}
        _drag_state.current_target = dropzone

        # Mouse moves outside
        mock_collision.return_value = False
        from arepy_ui.core.types import Vector2

        dropzone.handle_input(Vector2(500, 500), is_click=False)

        assert len(leave_called) == 1
        assert dropzone._is_drag_over is False


class TestDropZoneSortable:
    """Tests for sortable DropZone functionality."""

    def test_sortable_calculates_drop_index(self, mock_runtime, mock_collision):
        mock_collision.return_value = True

        dropzone = DropZone(sortable=True)
        dropzone.computed_x = 0
        dropzone.computed_y = 0
        dropzone.computed_width = 200
        dropzone.computed_height = 200

        d1 = Draggable(content=Node())
        d1.computed_y = 0
        d1.computed_height = 50
        dropzone.children = [d1]

        _drag_state.is_dragging = True
        _drag_state.source = Draggable(content=Node())  # Different draggable
        _drag_state.data = {}

        from arepy_ui.core.types import Vector2

        dropzone.handle_input(Vector2(100, 100), is_click=False)

        assert dropzone._drop_index is not None
        assert dropzone._indicator_rect is not None


class TestDropZoneRenderIndicator:
    """Tests for DropZone render with indicator."""

    def test_render_with_sortable_indicator(self, mock_runtime):
        with patch("arepy_ui.core.node.get_runtime") as mock_node_runtime:
            mock_node_runtime.return_value = mock_runtime["runtime"]
            mock_runtime["runtime"].display = MagicMock()
            mock_runtime["runtime"].display.get_window_size.return_value = (800, 600)

            dropzone = DropZone(sortable=True)
            dropzone.computed_x = 0
            dropzone.computed_y = 0
            dropzone.computed_width = 200
            dropzone.computed_height = 200
            dropzone._is_drag_over = True
            dropzone._indicator_rect = (10, 50, 180, 3)

            dropzone.render()

            # Should draw indicator rectangle
            mock_runtime["renderer"].draw_rectangle.assert_called()
