"""
Centralized component registry for arepy-ui.

This module provides a single source of truth for all UI components,
making it easy to:
- Register custom components
- Get component metadata (colors, tags, etc.)
- Use components in markup, debugger, and error reporting
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Type

from arepy_ui.core.types import Color


@dataclass(frozen=True, slots=True)
class ComponentMeta:
    """Metadata for a registered component."""

    component_class: Type
    name: str
    tags: tuple[str, ...]
    color: tuple[int, int, int]
    category: str = "custom"

    def get_debug_color(self, alpha: int = 180) -> Color:
        return Color(self.color[0], self.color[1], self.color[2], alpha)


class ComponentRegistry:
    """Central registry for all UI components."""

    _instance: Optional[ComponentRegistry] = None

    _components: Dict[str, ComponentMeta]
    _tag_map: Dict[str, str]
    _initialized: bool

    def __new__(cls) -> ComponentRegistry:
        if cls._instance is None:
            instance = super().__new__(cls)
            instance._components = {}
            instance._tag_map = {}
            instance._initialized = False
            cls._instance = instance
        return cls._instance

    def register(
        self,
        component_class: Type,
        name: Optional[str] = None,
        tags: Optional[List[str]] = None,
        color: tuple[int, int, int] = (150, 150, 150),
        category: str = "custom",
    ) -> None:
        """
        Register a component in the registry.

        Args:
            component_class: The component class to register
            name: Display name (defaults to class name)
            tags: AUI markup tags that map to this component
            color: RGB color for debugger visualization
            category: Component category (core, input, layout, media, custom)
        """
        comp_name = name or component_class.__name__
        tag_tuple = tuple(tags) if tags else (comp_name.lower(),)

        meta = ComponentMeta(
            component_class=component_class,
            name=comp_name,
            tags=tag_tuple,
            color=color,
            category=category,
        )

        self._components[comp_name] = meta

        for tag in tag_tuple:
            self._tag_map[tag] = comp_name

    def get(self, name: str) -> Optional[ComponentMeta]:
        """Get component metadata by name."""
        return self._components.get(name)

    def get_by_tag(self, tag: str) -> Optional[ComponentMeta]:
        """Get component metadata by markup tag."""
        comp_name = self._tag_map.get(tag.lower())
        if comp_name:
            return self._components.get(comp_name)
        return None

    def get_class(self, name: str) -> Optional[Type]:
        """Get component class by name."""
        meta = self._components.get(name)
        return meta.component_class if meta else None

    def get_class_by_tag(self, tag: str) -> Optional[Type]:
        """Get component class by markup tag."""
        meta = self.get_by_tag(tag)
        return meta.component_class if meta else None

    def get_all(self) -> Dict[str, ComponentMeta]:
        """Get all registered components."""
        return self._components.copy()

    def get_components_dict(self) -> Dict[str, Type]:
        """Get a dictionary of component names to classes (for markup loader)."""
        return {name: meta.component_class for name, meta in self._components.items()}

    def get_tag_map(self) -> Dict[str, str]:
        """Get mapping of tags to component names."""
        return self._tag_map.copy()

    def get_valid_tags(self) -> set[str]:
        """Get all valid markup tags."""
        return set(self._tag_map.keys())

    def is_valid_tag(self, tag: str) -> bool:
        """Check if a tag is valid."""
        return tag.lower() in self._tag_map

    def get_debug_color(self, class_name: str) -> Optional[tuple[int, int, int]]:
        """Get debug color for a component class name."""
        meta = self._components.get(class_name)
        return meta.color if meta else None

    def clear(self) -> None:
        """Clear all registered components (useful for testing)."""
        self._components.clear()
        self._tag_map.clear()
        self._initialized = False

    def _ensure_initialized(self) -> None:
        """Ensure built-in components are registered."""
        if self._initialized:
            return
        self._initialized = True
        _register_builtin_components(self)


def get_registry() -> ComponentRegistry:
    """Get the global component registry."""
    registry = ComponentRegistry()
    registry._ensure_initialized()
    return registry


def register_component(
    component_class: Type,
    name: Optional[str] = None,
    tags: Optional[List[str]] = None,
    color: tuple[int, int, int] = (150, 150, 150),
    category: str = "custom",
) -> None:
    """
    Register a custom component.

    Example:
        >>> from arepy_ui import register_component, Node
        >>>
        >>> class MyWidget(Node):
        ...     pass
        >>>
        >>> register_component(
        ...     MyWidget,
        ...     tags=["mywidget", "my-widget"],
        ...     color=(255, 100, 100),
        ... )
    """
    get_registry().register(
        component_class=component_class,
        name=name,
        tags=tags,
        color=color,
        category=category,
    )


def _register_builtin_components(registry: ComponentRegistry) -> None:
    """Register all built-in arepy-ui components."""
    from arepy_ui.components.button import Button
    from arepy_ui.components.canvas import Canvas
    from arepy_ui.components.checkbox import Checkbox
    from arepy_ui.components.colorpicker import ColorPicker
    from arepy_ui.components.divider import Divider
    from arepy_ui.components.drag import Draggable, DropZone
    from arepy_ui.components.image import Image
    from arepy_ui.components.input import TextInput
    from arepy_ui.components.listview import ListView
    from arepy_ui.components.progressbar import ProgressBar
    from arepy_ui.components.radio import RadioGroup
    from arepy_ui.components.scroll import ScrollView
    from arepy_ui.components.select import Select
    from arepy_ui.components.slider import Slider
    from arepy_ui.components.tabs import Tabs
    from arepy_ui.components.text import Text
    from arepy_ui.components.textarea import TextArea
    from arepy_ui.components.toggle import Toggle
    from arepy_ui.components.video import Video
    from arepy_ui.core.node import Node

    registry.register(
        Node,
        tags=["container", "row", "column", "spacer", "div", "node"],
        color=(120, 120, 130),
        category="core",
    )

    registry.register(
        Text,
        tags=["text", "label", "span", "p"],
        color=(100, 180, 255),
        category="core",
    )

    registry.register(
        Button,
        tags=["button", "btn"],
        color=(255, 130, 100),
        category="input",
    )

    registry.register(
        TextInput,
        tags=["input", "textinput", "text-input"],
        color=(130, 255, 180),
        category="input",
    )

    registry.register(
        TextArea,
        tags=["textarea", "text-area"],
        color=(130, 230, 160),
        category="input",
    )

    registry.register(
        Checkbox,
        tags=["checkbox", "check"],
        color=(255, 200, 100),
        category="input",
    )

    registry.register(
        Toggle,
        tags=["toggle", "switch"],
        color=(100, 220, 200),
        category="input",
    )

    registry.register(
        RadioGroup,
        tags=["radio", "radiogroup", "radio-group"],
        color=(200, 150, 255),
        category="input",
    )

    registry.register(
        Slider,
        tags=["slider", "range"],
        color=(200, 130, 255),
        category="input",
    )

    registry.register(
        Select,
        tags=["select", "dropdown"],
        color=(255, 180, 200),
        category="input",
    )

    registry.register(
        ScrollView,
        tags=["scroll", "scrollview", "scroll-view"],
        color=(180, 200, 255),
        category="layout",
    )

    registry.register(
        Tabs,
        tags=["tabs", "tabview"],
        color=(255, 150, 180),
        category="layout",
    )

    registry.register(
        ListView,
        tags=["listview", "list-view", "list"],
        color=(150, 200, 180),
        category="layout",
    )

    registry.register(
        Image,
        tags=["image", "img", "picture"],
        color=(100, 255, 200),
        category="media",
    )

    registry.register(
        Video,
        tags=["video"],
        color=(255, 100, 150),
        category="media",
    )

    registry.register(
        Canvas,
        tags=["canvas"],
        color=(150, 255, 200),
        category="media",
    )

    registry.register(
        ColorPicker,
        tags=["colorpicker", "color-picker"],
        color=(255, 200, 150),
        category="input",
    )

    registry.register(
        ProgressBar,
        tags=["progress", "progressbar", "progress-bar"],
        color=(100, 200, 255),
        category="display",
    )

    registry.register(
        Divider,
        tags=["divider", "hr", "separator"],
        color=(100, 100, 110),
        category="layout",
    )

    registry.register(
        Draggable,
        tags=["draggable"],
        color=(255, 180, 100),
        category="interaction",
    )

    registry.register(
        DropZone,
        tags=["dropzone", "drop-zone"],
        color=(180, 255, 100),
        category="interaction",
    )
