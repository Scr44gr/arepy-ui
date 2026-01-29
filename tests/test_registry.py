"""Tests for component registry."""

import pytest

from arepy_ui.core.node import Node
from arepy_ui.core.types import Color
from arepy_ui.registry import (
    ComponentMeta,
    ComponentRegistry,
    get_registry,
    register_component,
)


class TestComponentMeta:
    """Tests for ComponentMeta dataclass."""

    def test_component_meta_creation(self):
        meta = ComponentMeta(
            component_class=Node,
            name="Node",
            tags=("node", "container"),
            color=(100, 150, 200),
            category="core",
        )

        assert meta.component_class is Node
        assert meta.name == "Node"
        assert meta.tags == ("node", "container")
        assert meta.color == (100, 150, 200)
        assert meta.category == "core"

    def test_component_meta_default_category(self):
        meta = ComponentMeta(
            component_class=Node,
            name="Node",
            tags=("node",),
            color=(100, 100, 100),
        )

        assert meta.category == "custom"

    def test_component_meta_get_debug_color(self):
        meta = ComponentMeta(
            component_class=Node,
            name="Node",
            tags=("node",),
            color=(100, 150, 200),
        )

        debug_color = meta.get_debug_color(180)

        assert isinstance(debug_color, Color)
        assert debug_color.r == 100
        assert debug_color.g == 150
        assert debug_color.b == 200
        assert debug_color.a == 180

    def test_component_meta_get_debug_color_default_alpha(self):
        meta = ComponentMeta(
            component_class=Node,
            name="Node",
            tags=("node",),
            color=(50, 100, 150),
        )

        debug_color = meta.get_debug_color()

        assert debug_color.a == 180


class TestComponentRegistry:
    """Tests for ComponentRegistry singleton."""

    def test_registry_singleton(self):
        registry1 = ComponentRegistry()
        registry2 = ComponentRegistry()

        assert registry1 is registry2

    def test_get_registry_returns_initialized(self):
        registry = get_registry()

        assert registry is not None
        assert len(registry.get_all()) > 0

    def test_registry_has_builtin_components(self):
        registry = get_registry()

        assert registry.get("Node") is not None
        assert registry.get("Text") is not None
        assert registry.get("Button") is not None

    def test_registry_get_by_tag(self):
        registry = get_registry()

        meta = registry.get_by_tag("container")

        assert meta is not None
        assert meta.name == "Node"

    def test_registry_get_by_tag_case_insensitive(self):
        registry = get_registry()

        meta = registry.get_by_tag("CONTAINER")

        assert meta is not None
        assert meta.name == "Node"

    def test_registry_get_class(self):
        registry = get_registry()

        cls = registry.get_class("Node")

        assert cls is Node

    def test_registry_get_class_by_tag(self):
        registry = get_registry()

        cls = registry.get_class_by_tag("container")

        assert cls is Node

    def test_registry_get_class_not_found(self):
        registry = get_registry()

        cls = registry.get_class("NonExistent")

        assert cls is None

    def test_registry_get_components_dict(self):
        registry = get_registry()

        components = registry.get_components_dict()

        assert isinstance(components, dict)
        assert "Node" in components
        assert components["Node"] is Node

    def test_registry_get_valid_tags(self):
        registry = get_registry()

        tags = registry.get_valid_tags()

        assert isinstance(tags, set)
        assert "container" in tags
        assert "button" in tags
        assert "text" in tags

    def test_registry_is_valid_tag(self):
        registry = get_registry()

        assert registry.is_valid_tag("container") is True
        assert registry.is_valid_tag("button") is True
        assert registry.is_valid_tag("nonexistent") is False

    def test_registry_get_debug_color(self):
        registry = get_registry()

        color = registry.get_debug_color("Node")

        assert color is not None
        assert isinstance(color, tuple)
        assert len(color) == 3

    def test_registry_get_debug_color_not_found(self):
        registry = get_registry()

        color = registry.get_debug_color("NonExistent")

        assert color is None


class TestRegisterComponent:
    """Tests for register_component convenience function."""

    def test_register_custom_component(self):
        class CustomWidget(Node):
            pass

        register_component(
            CustomWidget,
            tags=["customwidget", "custom-widget"],
            color=(255, 100, 100),
            category="custom",
        )

        registry = get_registry()
        meta = registry.get("CustomWidget")

        assert meta is not None
        assert meta.component_class is CustomWidget
        assert "customwidget" in meta.tags
        assert meta.color == (255, 100, 100)

    def test_register_component_with_custom_name(self):
        class AnotherWidget(Node):
            pass

        register_component(
            AnotherWidget,
            name="MyWidget",
            tags=["mywidget"],
        )

        registry = get_registry()

        assert registry.get("MyWidget") is not None
        assert registry.get("AnotherWidget") is None

    def test_register_component_default_tag(self):
        class AutoTagWidget(Node):
            pass

        register_component(AutoTagWidget)

        registry = get_registry()
        meta = registry.get("AutoTagWidget")

        assert meta is not None
        assert "autotagwidget" in meta.tags
