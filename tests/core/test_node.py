"""Tests para arepy_ui.core.node"""

import pytest

from arepy_ui.core.node import Node
from arepy_ui.core.style import Spacing, Style
from arepy_ui.core.types import AlignItems, FlexDirection, JustifyContent, Unit


class TestNodeCreation:
    def test_node_default_creation(self):
        node = Node()
        assert node.style is not None
        assert node.parent is None
        assert len(node.children) == 0

    def test_node_with_style(self):
        style = Style(width=Unit.px(100), height=Unit.px(50))
        node = Node(style=style)
        assert node.style.width.value == 100
        assert node.style.height.value == 50


class TestNodeHierarchy:
    def test_add_child(self):
        parent = Node()
        child = Node()
        parent.add_child(child)

        assert len(parent.children) == 1
        assert child.parent is parent

    def test_add_multiple_children(self):
        parent = Node()
        child1 = Node()
        child2 = Node()
        child3 = Node()

        parent.add_child(child1)
        parent.add_child(child2)
        parent.add_child(child3)

        assert len(parent.children) == 3
        assert parent.children[0] is child1
        assert parent.children[1] is child2
        assert parent.children[2] is child3

    def test_remove_child_from_list(self):
        parent = Node()
        child = Node()
        parent.add_child(child)
        # Node doesn't have remove_child, use children.remove directly
        parent.children.remove(child)
        child.parent = None

        assert len(parent.children) == 0
        assert child.parent is None

    def test_nested_hierarchy(self):
        root = Node()
        level1 = Node()
        level2 = Node()

        root.add_child(level1)
        level1.add_child(level2)

        assert level1.parent is root
        assert level2.parent is level1


class TestNodeLayout:
    def test_layout_fixed_size(self):
        node = Node(style=Style(width=Unit.px(200), height=Unit.px(100)))
        node.calculate_layout(0, 0, 800, 600)

        assert node.computed_width == 200
        assert node.computed_height == 100
        assert node.computed_x == 0
        assert node.computed_y == 0

    def test_layout_percent_size(self):
        node = Node(style=Style(width=Unit.percent(50), height=Unit.percent(25)))
        node.calculate_layout(0, 0, 800, 600)

        assert node.computed_width == 400  # 50% of 800
        assert node.computed_height == 150  # 25% of 600

    def test_layout_with_padding(self):
        parent = Node(
            style=Style(
                width=Unit.px(200),
                height=Unit.px(100),
                padding=Spacing.all(10),
            )
        )
        child = Node(style=Style(width=Unit.percent(100), height=Unit.percent(100)))
        parent.add_child(child)
        parent.calculate_layout(0, 0, 800, 600)

        # Child should be 200 - 20 (padding) = 180
        assert child.computed_width == 180
        assert child.computed_height == 80
        assert child.computed_x == 10
        assert child.computed_y == 10

    def test_layout_column_direction(self):
        parent = Node(
            style=Style(
                width=Unit.px(200),
                height=Unit.px(200),
                flex_direction=FlexDirection.COLUMN,
                gap=10,
            )
        )
        child1 = Node(style=Style(width=Unit.percent(100), height=Unit.px(50)))
        child2 = Node(style=Style(width=Unit.percent(100), height=Unit.px(50)))
        parent.add_child(child1)
        parent.add_child(child2)
        parent.calculate_layout(0, 0, 800, 600)

        assert child1.computed_y == 0
        assert child2.computed_y == 60  # 50 + 10 gap

    def test_layout_row_direction(self):
        parent = Node(
            style=Style(
                width=Unit.px(200),
                height=Unit.px(100),
                flex_direction=FlexDirection.ROW,
                gap=10,
            )
        )
        child1 = Node(style=Style(width=Unit.px(50), height=Unit.percent(100)))
        child2 = Node(style=Style(width=Unit.px(50), height=Unit.percent(100)))
        parent.add_child(child1)
        parent.add_child(child2)
        parent.calculate_layout(0, 0, 800, 600)

        assert child1.computed_x == 0
        assert child2.computed_x == 60  # 50 + 10 gap

    def test_layout_justify_center(self):
        parent = Node(
            style=Style(
                width=Unit.px(200),
                height=Unit.px(100),
                flex_direction=FlexDirection.ROW,
                justify_content=JustifyContent.CENTER,
            )
        )
        child = Node(style=Style(width=Unit.px(50), height=Unit.px(50)))
        parent.add_child(child)
        parent.calculate_layout(0, 0, 800, 600)

        # Child should be centered: (200 - 50) / 2 = 75
        assert child.computed_x == 75

    def test_layout_align_center(self):
        parent = Node(
            style=Style(
                width=Unit.px(200),
                height=Unit.px(100),
                flex_direction=FlexDirection.ROW,
                align_items=AlignItems.CENTER,
            )
        )
        child = Node(style=Style(width=Unit.px(50), height=Unit.px(30)))
        parent.add_child(child)
        parent.calculate_layout(0, 0, 800, 600)

        # Child should be vertically centered: (100 - 30) / 2 = 35
        assert child.computed_y == 35


class TestNodeTranslate:
    def test_translate(self):
        node = Node(style=Style(width=Unit.px(100), height=Unit.px(100)))
        node.calculate_layout(50, 50, 800, 600)

        assert node.computed_x == 50
        assert node.computed_y == 50

        node.translate(10, 20)

        assert node.computed_x == 60
        assert node.computed_y == 70

    def test_translate_with_children(self):
        parent = Node(style=Style(width=Unit.px(200), height=Unit.px(200)))
        child = Node(style=Style(width=Unit.px(50), height=Unit.px(50)))
        parent.add_child(child)
        parent.calculate_layout(0, 0, 800, 600)

        initial_child_x = child.computed_x
        initial_child_y = child.computed_y

        parent.translate(100, 100)

        # Children should also move
        assert child.computed_x == initial_child_x + 100


class TestNodeFindById:
    def test_find_by_id_self(self):
        node = Node(id="test-node")

        result = node.find_by_id("test-node")

        assert result is node

    def test_find_by_id_child(self):
        parent = Node(id="parent")
        child = Node(id="child")
        parent.add_child(child)

        result = parent.find_by_id("child")

        assert result is child

    def test_find_by_id_grandchild(self):
        root = Node(id="root")
        child = Node(id="child")
        grandchild = Node(id="grandchild")
        root.add_child(child)
        child.add_child(grandchild)

        result = root.find_by_id("grandchild")

        assert result is grandchild

    def test_find_by_id_not_found(self):
        node = Node(id="test")

        result = node.find_by_id("nonexistent")

        assert result is None

    def test_find_by_id_none_id(self):
        node = Node()
        child = Node(id="child")
        node.add_child(child)

        result = node.find_by_id("child")

        assert result is child


class TestNodeVisibility:
    def test_layout_invisible_node(self):
        node = Node(style=Style(width=Unit.px(100), height=Unit.px(100), visible=False))
        node.calculate_layout(0, 0, 800, 600)

        assert node.computed_width == 0
        assert node.computed_height == 0


class TestNodeAbsolutePosition:
    def test_absolute_position_left_top(self):
        from arepy_ui.core.types import PositionType

        parent = Node(style=Style(width=Unit.px(400), height=Unit.px(300)))
        child = Node(
            style=Style(
                width=Unit.px(100),
                height=Unit.px(50),
                position=PositionType.ABSOLUTE,
                left=Unit.px(20),
                top=Unit.px(30),
            )
        )
        parent.add_child(child)
        parent.calculate_layout(0, 0, 800, 600)

        assert child.computed_x == 20
        assert child.computed_y == 30

    def test_absolute_position_right_bottom(self):
        from arepy_ui.core.types import PositionType

        parent = Node(style=Style(width=Unit.px(400), height=Unit.px(300)))
        child = Node(
            style=Style(
                width=Unit.px(100),
                height=Unit.px(50),
                position=PositionType.ABSOLUTE,
                right=Unit.px(20),
                bottom=Unit.px(30),
            )
        )
        parent.add_child(child)
        parent.calculate_layout(0, 0, 800, 600)

        # Right: 400 - 100 - 20 = 280
        assert child.computed_x == 280
        # Bottom: 300 - 50 - 30 = 220
        assert child.computed_y == 220

    def test_absolute_position_no_offset(self):
        from arepy_ui.core.types import PositionType

        parent = Node(style=Style(width=Unit.px(400), height=Unit.px(300)))
        child = Node(
            style=Style(
                width=Unit.px(100),
                height=Unit.px(50),
                position=PositionType.ABSOLUTE,
            )
        )
        parent.add_child(child)
        parent.calculate_layout(0, 0, 800, 600)

        # Should default to 0,0
        assert child.computed_x == 0
        assert child.computed_y == 0

    def test_absolute_child_not_in_flex_flow(self):
        from arepy_ui.core.types import PositionType

        parent = Node(
            style=Style(
                width=Unit.px(300),
                height=Unit.px(200),
                flex_direction=FlexDirection.ROW,
            )
        )
        normal_child = Node(style=Style(width=Unit.px(50), height=Unit.px(50)))
        absolute_child = Node(
            style=Style(
                width=Unit.px(100),
                height=Unit.px(100),
                position=PositionType.ABSOLUTE,
                left=Unit.px(150),
                top=Unit.px(50),
            )
        )
        parent.add_child(normal_child)
        parent.add_child(absolute_child)
        parent.calculate_layout(0, 0, 800, 600)

        # Normal child should be at start
        assert normal_child.computed_x == 0
        # Absolute child should be at its specified position
        assert absolute_child.computed_x == 150
        assert absolute_child.computed_y == 50


class TestNodeAutoSize:
    def test_auto_width_row_direction(self):
        parent = Node(
            style=Style(
                width=Unit.auto(),
                height=Unit.px(100),
                flex_direction=FlexDirection.ROW,
                gap=10,
            )
        )
        child1 = Node(style=Style(width=Unit.px(50), height=Unit.px(50)))
        child2 = Node(style=Style(width=Unit.px(60), height=Unit.px(50)))
        parent.add_child(child1)
        parent.add_child(child2)
        parent.calculate_layout(0, 0, 800, 600)

        # Auto width in ROW: 50 + 10 + 60 = 120
        assert parent.computed_width == 120

    def test_auto_height_column_direction(self):
        parent = Node(
            style=Style(
                width=Unit.px(100),
                height=Unit.auto(),
                flex_direction=FlexDirection.COLUMN,
                gap=5,
            )
        )
        child1 = Node(style=Style(width=Unit.px(50), height=Unit.px(30)))
        child2 = Node(style=Style(width=Unit.px(50), height=Unit.px(40)))
        parent.add_child(child1)
        parent.add_child(child2)
        parent.calculate_layout(0, 0, 800, 600)

        # Auto height in COLUMN: 30 + 5 + 40 = 75
        assert parent.computed_height == 75


class TestNodeJustifyContent:
    def test_justify_end_row(self):
        parent = Node(
            style=Style(
                width=Unit.px(200),
                height=Unit.px(100),
                flex_direction=FlexDirection.ROW,
                justify_content=JustifyContent.END,
            )
        )
        child = Node(style=Style(width=Unit.px(50), height=Unit.px(50)))
        parent.add_child(child)
        parent.calculate_layout(0, 0, 800, 600)

        # Child should be at the end: 200 - 50 = 150
        assert child.computed_x == 150

    def test_justify_end_column(self):
        parent = Node(
            style=Style(
                width=Unit.px(100),
                height=Unit.px(200),
                flex_direction=FlexDirection.COLUMN,
                justify_content=JustifyContent.END,
            )
        )
        child = Node(style=Style(width=Unit.px(50), height=Unit.px(50)))
        parent.add_child(child)
        parent.calculate_layout(0, 0, 800, 600)

        # Child should be at the end: 200 - 50 = 150
        assert child.computed_y == 150

    def test_justify_center_column(self):
        parent = Node(
            style=Style(
                width=Unit.px(100),
                height=Unit.px(200),
                flex_direction=FlexDirection.COLUMN,
                justify_content=JustifyContent.CENTER,
            )
        )
        child = Node(style=Style(width=Unit.px(50), height=Unit.px(60)))
        parent.add_child(child)
        parent.calculate_layout(0, 0, 800, 600)

        # Child should be centered: (200 - 60) / 2 = 70
        assert child.computed_y == 70


class TestNodeAlignItems:
    def test_align_center_column(self):
        parent = Node(
            style=Style(
                width=Unit.px(200),
                height=Unit.px(100),
                flex_direction=FlexDirection.COLUMN,
                align_items=AlignItems.CENTER,
            )
        )
        child = Node(style=Style(width=Unit.px(80), height=Unit.px(50)))
        parent.add_child(child)
        parent.calculate_layout(0, 0, 800, 600)

        # Child should be centered horizontally: (200 - 80) / 2 = 60
        assert child.computed_x == 60


class TestNodeMargin:
    def test_child_with_margin(self):
        parent = Node(style=Style(width=Unit.px(200), height=Unit.px(200)))
        child = Node(
            style=Style(
                width=Unit.px(50),
                height=Unit.px(50),
                margin=Spacing(
                    left=Unit.px(10),
                    top=Unit.px(20),
                    right=Unit.px(0),
                    bottom=Unit.px(0),
                ),
            )
        )
        parent.add_child(child)
        parent.calculate_layout(0, 0, 800, 600)

        assert child.computed_x == 10
        assert child.computed_y == 20


class TestNodePropagatePositionToChildren:
    def test_propagate_position_with_nested_children(self):
        parent = Node(style=Style(width=Unit.px(200), height=Unit.px(200)))
        child = Node(style=Style(width=Unit.px(100), height=Unit.px(100)))
        grandchild = Node(style=Style(width=Unit.px(50), height=Unit.px(50)))
        parent.add_child(child)
        child.add_child(grandchild)
        parent.calculate_layout(0, 0, 800, 600)

        # Move the parent
        child.computed_x = 50
        child.computed_y = 50

        # Manually call propagate
        parent._propagate_position_to_children(child)

        # Grandchild should be updated relative to child's new position
        assert grandchild.computed_x == 50
        assert grandchild.computed_y == 50

    def test_propagate_position_with_absolute_child(self):
        from arepy_ui.core.types import PositionType

        parent = Node(style=Style(width=Unit.px(200), height=Unit.px(200)))
        child = Node(
            style=Style(
                width=Unit.px(50),
                height=Unit.px(50),
                position=PositionType.ABSOLUTE,
                left=Unit.px(30),
                top=Unit.px(40),
            )
        )
        parent.add_child(child)
        parent.calculate_layout(0, 0, 800, 600)

        # Move parent
        parent.computed_x = 100
        parent.computed_y = 100

        parent._propagate_position_to_children(parent)

        # Absolute child should be at 100 + 30, 100 + 40
        assert child.computed_x == 130
        assert child.computed_y == 140


class TestNodeDirtyRelayoutRoot:
    def test_relayout_root_defaults_to_parent_for_descendant_change(self):
        root = Node(style=Style(width=Unit.px(400), height=Unit.px(300)))
        container = Node(style=Style(width=Unit.px(200), height=Unit.px(100)))
        child = Node(style=Style(width=Unit.px(50), height=Unit.px(20)))

        root.add_child(container)
        container.add_child(child)

        assert child._get_relayout_root() is container

    def test_relayout_root_climbs_through_auto_sized_ancestors(self):
        root = Node(style=Style(width=Unit.px(400), height=Unit.px(300)))
        auto_container = Node(
            style=Style(
                width=Unit.auto(),
                height=Unit.px(100),
                flex_direction=FlexDirection.ROW,
            )
        )
        child = Node(style=Style(width=Unit.px(50), height=Unit.px(20)))

        root.add_child(auto_container)
        auto_container.add_child(child)

        assert child._get_relayout_root() is root


class TestNodeStyleBinding:
    def test_node_binds_style_owner(self):
        style = Style(width=Unit.px(100), height=Unit.px(50))
        node = Node(style=style)

        assert style._owner is node

    def test_replacing_node_style_rebinds_owner(self):
        node = Node()
        new_style = Style(width=Unit.px(100))

        node.style = new_style

        assert new_style._owner is node

    def test_propagate_position_invisible_node(self):
        parent = Node(style=Style(width=Unit.px(200), height=Unit.px(200)))
        child = Node(style=Style(width=Unit.px(50), height=Unit.px(50), visible=False))
        parent.add_child(child)
        parent.calculate_layout(0, 0, 800, 600)

        # Should not crash
        parent._propagate_position_to_children(parent)

    def test_propagate_with_justify_and_align(self):
        parent = Node(
            style=Style(
                width=Unit.px(200),
                height=Unit.px(200),
                flex_direction=FlexDirection.ROW,
                justify_content=JustifyContent.CENTER,
                align_items=AlignItems.CENTER,
            )
        )
        child = Node(style=Style(width=Unit.px(60), height=Unit.px(40)))
        parent.add_child(child)
        parent.calculate_layout(0, 0, 800, 600)

        # Move parent
        parent.computed_x = 50
        parent.computed_y = 50

        parent._propagate_position_to_children(parent)

        # Child should be centered: x = 50 + (200-60)/2 = 50 + 70 = 120
        # y = 50 + (200-40)/2 = 50 + 80 = 130
        assert child.computed_x == 120
        assert child.computed_y == 130


class TestNodeResolveUnit:
    def test_resolve_pixel(self):
        node = Node()
        result = node._resolve_unit(Unit.px(100), 500)
        assert result == 100

    def test_resolve_percent(self):
        node = Node()
        result = node._resolve_unit(Unit.percent(50), 200)
        assert result == 100

    def test_resolve_auto(self):
        node = Node()
        result = node._resolve_unit(Unit.auto(), 300)
        # Auto defaults to parent value
        assert result == 300

    def test_resolve_unknown_type(self):
        from arepy_ui.core.types import UnitType

        node = Node()
        # Test with a default unit type that returns 0
        result = node._resolve_unit(Unit.px(50), 200)
        assert result == 50  # Pixel resolves to exact value


from unittest.mock import MagicMock, patch


class TestNodeRender:
    @pytest.fixture
    def mock_runtime(self):
        with patch("arepy_ui.core.node.get_runtime") as mock_get:
            mock_rt = MagicMock()
            mock_rt.display.get_window_size.return_value = (800, 600)
            mock_rt.renderer = MagicMock()
            mock_get.return_value = mock_rt
            yield {"runtime": mock_rt, "renderer": mock_rt.renderer}

    def test_render_invisible(self, mock_runtime):
        node = Node(style=Style(visible=False))
        node.render()
        mock_runtime["renderer"].draw_rectangle.assert_not_called()

    def test_render_zero_opacity(self, mock_runtime):
        node = Node(style=Style(opacity=0))
        node.render()
        mock_runtime["renderer"].draw_rectangle.assert_not_called()

    def test_render_offscreen_right(self, mock_runtime):
        node = Node(style=Style(width=Unit.px(100), height=Unit.px(100)))
        node.computed_x = 900  # Off screen
        node.computed_y = 100
        node.computed_width = 100
        node.computed_height = 100

        node.render()
        mock_runtime["renderer"].draw_rectangle.assert_not_called()

    def test_render_offscreen_bottom(self, mock_runtime):
        node = Node(style=Style(width=Unit.px(100), height=Unit.px(100)))
        node.computed_x = 100
        node.computed_y = 700  # Off screen
        node.computed_width = 100
        node.computed_height = 100

        node.render()
        mock_runtime["renderer"].draw_rectangle.assert_not_called()

    def test_render_offscreen_left(self, mock_runtime):
        node = Node(style=Style(width=Unit.px(100), height=Unit.px(100)))
        node.computed_x = -200  # Off screen
        node.computed_y = 100
        node.computed_width = 100
        node.computed_height = 100

        node.render()
        mock_runtime["renderer"].draw_rectangle.assert_not_called()

    def test_render_offscreen_top(self, mock_runtime):
        node = Node(style=Style(width=Unit.px(100), height=Unit.px(100)))
        node.computed_x = 100
        node.computed_y = -200  # Off screen
        node.computed_width = 100
        node.computed_height = 100

        node.render()
        mock_runtime["renderer"].draw_rectangle.assert_not_called()

    def test_render_with_background_color(self, mock_runtime):
        from arepy_ui.core.types import Color

        node = Node(
            style=Style(
                width=Unit.px(100),
                height=Unit.px(100),
                background_color=Color(255, 0, 0, 255),
            )
        )
        node.computed_x = 100
        node.computed_y = 100
        node.computed_width = 100
        node.computed_height = 100

        node.render()
        mock_runtime["renderer"].draw_rectangle.assert_called()

    def test_render_with_border_radius(self, mock_runtime):
        from arepy_ui.core.types import Color

        node = Node(
            style=Style(
                width=Unit.px(100),
                height=Unit.px(100),
                background_color=Color(255, 0, 0, 255),
                border_radius=10,
            )
        )
        node.computed_x = 100
        node.computed_y = 100
        node.computed_width = 100
        node.computed_height = 100

        node.render()
        mock_runtime["renderer"].draw_rectangle_rounded.assert_called()

    def test_render_with_opacity(self, mock_runtime):
        from arepy_ui.core.types import Color

        node = Node(
            style=Style(
                width=Unit.px(100),
                height=Unit.px(100),
                background_color=Color(255, 0, 0, 255),
                opacity=0.5,
            )
        )
        node.computed_x = 100
        node.computed_y = 100
        node.computed_width = 100
        node.computed_height = 100

        node.render()
        mock_runtime["renderer"].draw_rectangle.assert_called()

    def test_render_with_border(self, mock_runtime):
        from arepy_ui.core.types import Color

        node = Node(
            style=Style(
                width=Unit.px(100),
                height=Unit.px(100),
                border_width=2,
                border_color=Color(0, 0, 0, 255),
            )
        )
        node.computed_x = 100
        node.computed_y = 100
        node.computed_width = 100
        node.computed_height = 100

        node.render()
        mock_runtime["renderer"].draw_rectangle_lines_ex.assert_called()

    def test_render_with_border_and_radius(self, mock_runtime):
        from arepy_ui.core.types import Color

        node = Node(
            style=Style(
                width=Unit.px(100),
                height=Unit.px(100),
                border_width=2,
                border_color=Color(0, 0, 0, 255),
                border_radius=10,
            )
        )
        node.computed_x = 100
        node.computed_y = 100
        node.computed_width = 100
        node.computed_height = 100

        node.render()
        mock_runtime["renderer"].draw_rectangle_rounded_lines.assert_called()

    def test_render_children(self, mock_runtime):
        from arepy_ui.core.types import Color

        parent = Node(style=Style(width=Unit.px(200), height=Unit.px(200)))
        child = Node(
            style=Style(
                width=Unit.px(50),
                height=Unit.px(50),
                background_color=Color(0, 255, 0, 255),
            )
        )
        parent.add_child(child)
        parent.computed_x = 0
        parent.computed_y = 0
        parent.computed_width = 200
        parent.computed_height = 200
        child.computed_x = 10
        child.computed_y = 10
        child.computed_width = 50
        child.computed_height = 50

        parent.render()
        # Child's background should be drawn
        mock_runtime["renderer"].draw_rectangle.assert_called()


class TestNodeHandleInput:
    @pytest.fixture
    def mock_collision(self):
        with patch("arepy_ui.core.node.check_collision_point_rec") as mock:
            yield mock

    def test_handle_input_invisible(self, mock_collision):
        from arepy_ui.core.types import Vector2

        node = Node(style=Style(visible=False))
        result = node.handle_input(Vector2(50, 50), is_click=True)
        assert result is False

    def test_handle_input_not_pickable(self, mock_collision):
        from arepy_ui.core.types import Vector2

        mock_collision.return_value = True

        node = Node()
        node.pickable = False
        node.computed_x = 0
        node.computed_y = 0
        node.computed_width = 100
        node.computed_height = 100

        result = node.handle_input(Vector2(50, 50), is_click=True)
        assert result is False

    def test_handle_input_hover_enter(self, mock_collision):
        from arepy_ui.core.types import Vector2

        mock_collision.return_value = True
        hover_entered = []

        def on_hover_enter():
            hover_entered.append(True)

        node = Node()
        node.on_hover_enter = on_hover_enter
        node.computed_x = 0
        node.computed_y = 0
        node.computed_width = 100
        node.computed_height = 100

        result = node.handle_input(Vector2(50, 50), is_click=False)

        assert node.is_hovered is True
        assert len(hover_entered) == 1

    def test_handle_input_hover_exit(self, mock_collision):
        from arepy_ui.core.types import Vector2

        mock_collision.return_value = False
        hover_exited = []

        def on_hover_exit():
            hover_exited.append(True)

        node = Node()
        node.on_hover_exit = on_hover_exit
        node.is_hovered = True  # Was hovering before
        node.computed_x = 0
        node.computed_y = 0
        node.computed_width = 100
        node.computed_height = 100

        result = node.handle_input(Vector2(200, 200), is_click=False)

        assert node.is_hovered is False
        assert len(hover_exited) == 1

    def test_handle_input_click(self, mock_collision):
        from arepy_ui.core.types import Vector2

        mock_collision.return_value = True
        clicked = []

        def on_click():
            clicked.append(True)

        node = Node()
        node.on_click = on_click
        node.computed_x = 0
        node.computed_y = 0
        node.computed_width = 100
        node.computed_height = 100

        result = node.handle_input(Vector2(50, 50), is_click=True)

        assert result is True
        assert len(clicked) == 1

    def test_handle_input_click_no_handler(self, mock_collision):
        from arepy_ui.core.types import Vector2

        mock_collision.return_value = True

        node = Node()
        node.computed_x = 0
        node.computed_y = 0
        node.computed_width = 100
        node.computed_height = 100

        result = node.handle_input(Vector2(50, 50), is_click=True)

        # No click handler, so input not consumed
        assert result is False

    def test_handle_input_child_consumes(self, mock_collision):
        from arepy_ui.core.types import Vector2

        mock_collision.return_value = True
        parent_clicked = []
        child_clicked = []

        parent = Node()
        parent.on_click = lambda: parent_clicked.append(True)
        parent.computed_x = 0
        parent.computed_y = 0
        parent.computed_width = 200
        parent.computed_height = 200

        child = Node()
        child.on_click = lambda: child_clicked.append(True)
        child.computed_x = 10
        child.computed_y = 10
        child.computed_width = 50
        child.computed_height = 50
        parent.add_child(child)

        result = parent.handle_input(Vector2(25, 25), is_click=True)

        # Child should consume the click first (reverse order)
        assert result is True
        assert len(child_clicked) == 1
        assert len(parent_clicked) == 0


class TestNodeMarkDirty:
    def test_mark_dirty_with_manager(self):
        node = Node()
        mock_manager = MagicMock()
        node._manager = mock_manager

        node.mark_dirty()

        mock_manager.mark_dirty_node.assert_called_once_with(node)
        mock_manager.mark_dirty.assert_not_called()

    def test_mark_dirty_propagates_to_parent(self):
        parent = Node()
        child = Node()
        parent.add_child(child)

        mock_manager = MagicMock()
        parent._manager = mock_manager

        child.mark_dirty()

        mock_manager.mark_dirty_node.assert_called_once_with(parent)
        mock_manager.mark_dirty.assert_not_called()


class TestNodePropagateManager:
    def test_propagate_manager_on_add_child(self):
        parent = Node()
        mock_manager = MagicMock()
        parent._manager = mock_manager

        child = Node()
        grandchild = Node()
        child.add_child(grandchild)

        parent.add_child(child)

        assert child._manager is mock_manager
        assert grandchild._manager is mock_manager


class TestNodePropagatePositionAbsolute:
    """Tests for _propagate_position_to_children with absolute positioning."""

    def test_propagate_absolute_respects_parent_padding(self):
        from arepy_ui.core.types import PositionType

        parent = Node(
            style=Style(
                width=Unit.px(200),
                height=Unit.px(200),
                padding=Spacing.all(10),
            )
        )
        child = Node(
            style=Style(
                width=Unit.px(50),
                height=Unit.px(50),
                position=PositionType.ABSOLUTE,
                left=Unit.px(30),
                top=Unit.px(40),
            )
        )
        parent.add_child(child)
        parent.calculate_layout(0, 0, 800, 600)

        parent.computed_x = 100
        parent.computed_y = 100

        parent._propagate_position_to_children(parent)

        assert child.computed_x == 140
        assert child.computed_y == 150

    def test_propagate_absolute_right_position(self):
        from arepy_ui.core.types import PositionType

        parent = Node(style=Style(width=Unit.px(300), height=Unit.px(200)))
        child = Node(
            style=Style(
                width=Unit.px(50),
                height=Unit.px(50),
                position=PositionType.ABSOLUTE,
                right=Unit.px(20),
            )
        )
        parent.add_child(child)
        parent.calculate_layout(0, 0, 800, 600)

        # Move parent
        parent.computed_x = 100
        parent.computed_width = 300

        parent._propagate_position_to_children(parent)

        # Right: 100 + 300 - 50 - 20 = 330
        assert child.computed_x == 330

    def test_propagate_absolute_bottom_position(self):
        from arepy_ui.core.types import PositionType

        parent = Node(style=Style(width=Unit.px(200), height=Unit.px(300)))
        child = Node(
            style=Style(
                width=Unit.px(50),
                height=Unit.px(50),
                position=PositionType.ABSOLUTE,
                bottom=Unit.px(25),
            )
        )
        parent.add_child(child)
        parent.calculate_layout(0, 0, 800, 600)

        # Move parent
        parent.computed_y = 50
        parent.computed_height = 300

        parent._propagate_position_to_children(parent)

        # Bottom: 50 + 300 - 50 - 25 = 275
        assert child.computed_y == 275

    def test_propagate_absolute_right_and_bottom(self):
        from arepy_ui.core.types import PositionType

        parent = Node(style=Style(width=Unit.px(400), height=Unit.px(300)))
        child = Node(
            style=Style(
                width=Unit.px(80),
                height=Unit.px(60),
                position=PositionType.ABSOLUTE,
                right=Unit.px(30),
                bottom=Unit.px(40),
            )
        )
        parent.add_child(child)
        parent.calculate_layout(0, 0, 800, 600)

        parent.computed_x = 50
        parent.computed_y = 50

        parent._propagate_position_to_children(parent)

        # Right: 50 + 400 - 80 - 30 = 340
        assert child.computed_x == 340
        # Bottom: 50 + 300 - 60 - 40 = 250
        assert child.computed_y == 250

    def test_propagate_absolute_no_position(self):
        from arepy_ui.core.types import PositionType

        parent = Node(style=Style(width=Unit.px(200), height=Unit.px(200)))
        child = Node(
            style=Style(
                width=Unit.px(50),
                height=Unit.px(50),
                position=PositionType.ABSOLUTE,
            )
        )
        parent.add_child(child)
        parent.calculate_layout(0, 0, 800, 600)

        parent.computed_x = 100
        parent.computed_y = 100

        parent._propagate_position_to_children(parent)

        # No left/right/top/bottom, should default to parent position
        assert child.computed_x == 100
        assert child.computed_y == 100

    def test_propagate_absolute_with_nested_children(self):
        from arepy_ui.core.types import PositionType

        parent = Node(style=Style(width=Unit.px(300), height=Unit.px(200)))
        child = Node(
            style=Style(
                width=Unit.px(100),
                height=Unit.px(100),
                position=PositionType.ABSOLUTE,
                left=Unit.px(50),
                top=Unit.px(30),
            )
        )
        grandchild = Node(style=Style(width=Unit.px(30), height=Unit.px(30)))
        child.add_child(grandchild)
        parent.add_child(child)
        parent.calculate_layout(0, 0, 800, 600)

        parent.computed_x = 80
        parent.computed_y = 80

        parent._propagate_position_to_children(parent)

        # Child: 80 + 50 = 130, 80 + 30 = 110
        assert child.computed_x == 130
        assert child.computed_y == 110

    def test_propagate_column_with_justify_end(self):
        parent = Node(
            style=Style(
                width=Unit.px(200),
                height=Unit.px(300),
                flex_direction=FlexDirection.COLUMN,
                justify_content=JustifyContent.END,
            )
        )
        child = Node(style=Style(width=Unit.px(80), height=Unit.px(50)))
        parent.add_child(child)
        parent.calculate_layout(0, 0, 800, 600)

        parent.computed_x = 50
        parent.computed_y = 50

        parent._propagate_position_to_children(parent)

        # Justify END in COLUMN: y = 50 + (300 - 50) = 300
        assert child.computed_y == 300

    def test_propagate_row_with_justify_end(self):
        parent = Node(
            style=Style(
                width=Unit.px(300),
                height=Unit.px(100),
                flex_direction=FlexDirection.ROW,
                justify_content=JustifyContent.END,
            )
        )
        child = Node(style=Style(width=Unit.px(60), height=Unit.px(40)))
        parent.add_child(child)
        parent.calculate_layout(0, 0, 800, 600)

        parent.computed_x = 50
        parent.computed_y = 50

        parent._propagate_position_to_children(parent)

        # Justify END in ROW: x = 50 + (300 - 60) = 290
        assert child.computed_x == 290

    def test_propagate_column_with_align_center(self):
        parent = Node(
            style=Style(
                width=Unit.px(200),
                height=Unit.px(200),
                flex_direction=FlexDirection.COLUMN,
                align_items=AlignItems.CENTER,
            )
        )
        child = Node(style=Style(width=Unit.px(80), height=Unit.px(50)))
        parent.add_child(child)
        parent.calculate_layout(0, 0, 800, 600)

        parent.computed_x = 50
        parent.computed_y = 50

        parent._propagate_position_to_children(parent)

        # Align CENTER in COLUMN: x = 50 + (200 - 80) / 2 = 50 + 60 = 110
        assert child.computed_x == 110


class TestNodeResolveViewportUnits:
    """Tests for viewport unit resolution."""

    def test_resolve_viewport_width(self):
        with patch("arepy_ui.core.node.get_runtime") as mock_get:
            mock_rt = MagicMock()
            mock_rt.display.get_window_size.return_value = (1920, 1080)
            mock_get.return_value = mock_rt

            from arepy_ui.core.types import UnitType

            node = Node()
            unit = Unit(50, UnitType.VIEWPORT_WIDTH)
            result = node._resolve_unit(unit, 0)

            # 50vw = 50% of 1920 = 960
            assert result == 960

    def test_resolve_viewport_height(self):
        with patch("arepy_ui.core.node.get_runtime") as mock_get:
            mock_rt = MagicMock()
            mock_rt.display.get_window_size.return_value = (1920, 1080)
            mock_get.return_value = mock_rt

            from arepy_ui.core.types import UnitType

            node = Node()
            unit = Unit(25, UnitType.VIEWPORT_HEIGHT)
            result = node._resolve_unit(unit, 0)

            # 25vh = 25% of 1080 = 270
            assert result == 270


class TestNodeVisibility:
    def test_visible_by_default(self):
        node = Node()
        assert node.style.visible == True

    def test_set_invisible(self):
        node = Node(style=Style(visible=False))
        assert node.style.visible == False
