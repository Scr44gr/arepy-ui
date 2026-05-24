"""
Component builder for converting AUI nodes to arepy-ui components.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Dict, Mapping, Optional

from arepy_ui.core.style import Style
from arepy_ui.markup.converters import (
    convert_to_align_items,
    convert_to_color,
    convert_to_flex_direction,
    convert_to_float,
    convert_to_int,
    convert_to_justify_content,
    convert_to_position_type,
    convert_to_spacing,
    convert_to_unit,
)
from arepy_ui.markup.errors import ErrorCollector
from arepy_ui.markup.parsers.constants import CSS_TO_STYLE, TAG_TO_COMPONENT

if TYPE_CHECKING:
    from arepy_ui.core.node import Node
    from arepy_ui.markup.parsers import AUINode, StyleSheet


# Converters for each style property type
_STYLE_CONVERTERS: Dict[str, Callable[[Any], Any]] = {
    # Units
    "width": convert_to_unit,
    "height": convert_to_unit,
    "min_width": convert_to_unit,
    "max_width": convert_to_unit,
    "min_height": convert_to_unit,
    "max_height": convert_to_unit,
    "top": convert_to_unit,
    "left": convert_to_unit,
    "right": convert_to_unit,
    "bottom": convert_to_unit,
    # Spacing
    "padding": convert_to_spacing,
    "margin": convert_to_spacing,
    # Enums
    "flex_direction": convert_to_flex_direction,
    "justify_content": convert_to_justify_content,
    "align_items": convert_to_align_items,
    "position": convert_to_position_type,
    # Colors
    "background_color": convert_to_color,
    "text_color": convert_to_color,
    "border_color": convert_to_color,
    # Floats
    "gap": convert_to_float,
    "border_width": convert_to_float,
    "border_radius": convert_to_float,
    "font_size": convert_to_float,
    "opacity": convert_to_float,
    # Integers
    "z_index": convert_to_int,
}


def _resolve_pseudo_styles(
    node: AUINode,
    stylesheet: Optional[StyleSheet],
    pseudo: str,
) -> Dict[str, Any]:
    """
    Resolve styles for a pseudo-state (hover, active) from stylesheet.

    Args:
        node: The AUI node
        stylesheet: Optional stylesheet
        pseudo: The pseudo-selector (e.g., 'hover', 'active')

    Returns:
        Dictionary of style properties for the pseudo-state
    """
    from arepy_ui.markup.globals import get_global_styles

    result: Dict[str, Any] = {}
    attrs = node.attributes
    globals_registry = get_global_styles()

    # 1. Global element pseudo-styles
    global_element = globals_registry.resolve_for_element_pseudo(node.tag, pseudo)
    result.update(global_element)

    # 2. Global class pseudo-styles
    for class_name in node.get_classes():
        global_class = globals_registry.resolve_for_class_pseudo(class_name, pseudo)
        result.update(global_class)

    # 3. Global ID pseudo-styles
    element_id = attrs.get("id")
    if element_id:
        global_id = globals_registry.resolve_for_id_pseudo(element_id, pseudo)
        result.update(global_id)

    # 4. Local stylesheet pseudo-styles
    if stylesheet:
        # Check if stylesheet has pseudo methods
        if hasattr(stylesheet, "resolve_element_pseudo"):
            element_styles = stylesheet.resolve_element_pseudo(node.tag, pseudo)
            result.update(element_styles)

        if hasattr(stylesheet, "resolve_class_pseudo"):
            for class_name in node.get_classes():
                class_styles = stylesheet.resolve_class_pseudo(class_name, pseudo)
                result.update(class_styles)

        if hasattr(stylesheet, "resolve_id_pseudo") and element_id:
            id_styles = stylesheet.resolve_id_pseudo(element_id, pseudo)
            result.update(id_styles)

    return result


def resolve_styles(
    node: AUINode,
    stylesheet: Optional[StyleSheet],
) -> Dict[str, Any]:
    """
    Resolve and convert styles for an AUI node.

    Style cascade (lowest to highest priority):
    1. Global element styles
    2. Global class styles
    3. Global ID styles
    4. Local element styles
    5. Local class styles
    6. Local ID styles
    7. Inline styles

    Args:
        node: The AUI node to get styles for
        stylesheet: Optional stylesheet for class/element styles

    Returns:
        Dictionary of style properties with converted values
    """
    from arepy_ui.core.types import FlexDirection
    from arepy_ui.markup.globals import get_global_styles

    style_dict: Dict[str, Any] = {}
    globals_registry = get_global_styles()

    # 1. Global element styles (lowest priority)
    global_element = globals_registry.resolve_for_element(node.tag)
    for css_key, value in global_element.items():
        if css_key in CSS_TO_STYLE:
            style_key = CSS_TO_STYLE[css_key]
            style_dict[style_key] = _convert_style_value(style_key, value)

    # 2. Global class styles
    for class_name in node.get_classes():
        global_class = globals_registry.resolve_for_class(class_name)
        for css_key, value in global_class.items():
            if css_key in CSS_TO_STYLE:
                style_key = CSS_TO_STYLE[css_key]
                style_dict[style_key] = _convert_style_value(style_key, value)

    # 3. Global ID styles
    element_id = node.attributes.get("id")
    if element_id:
        global_id = globals_registry.resolve_for_id(element_id)
        for css_key, value in global_id.items():
            if css_key in CSS_TO_STYLE:
                style_key = CSS_TO_STYLE[css_key]
                style_dict[style_key] = _convert_style_value(style_key, value)

    if stylesheet:
        # 4. Local element styles
        element_styles = stylesheet.resolve_element(node.tag)
        for css_key, value in element_styles.items():
            if css_key in CSS_TO_STYLE:
                style_key = CSS_TO_STYLE[css_key]
                style_dict[style_key] = _convert_style_value(style_key, value)

        # 5. Local class styles
        for class_name in node.get_classes():
            class_styles = stylesheet.resolve_class(class_name)
            for css_key, value in class_styles.items():
                if css_key in CSS_TO_STYLE:
                    style_key = CSS_TO_STYLE[css_key]
                    style_dict[style_key] = _convert_style_value(style_key, value)

        # 6. Local ID styles
        if element_id:
            id_styles = stylesheet.resolve_id(element_id)
            for css_key, value in id_styles.items():
                if css_key in CSS_TO_STYLE:
                    style_key = CSS_TO_STYLE[css_key]
                    style_dict[style_key] = _convert_style_value(style_key, value)

    # 7. Inline styles (highest priority)
    inline_style = node.attributes.get("style", "")
    if inline_style:
        for declaration in inline_style.split(";"):
            if ":" in declaration:
                css_key, value = declaration.split(":", 1)
                css_key = css_key.strip()
                value = value.strip()
                if css_key in CSS_TO_STYLE:
                    style_key = CSS_TO_STYLE[css_key]
                    style_dict[style_key] = _convert_style_value(style_key, value)

    # Handle layout shortcuts for row/column tags
    if node.tag == "row":
        style_dict.setdefault("flex_direction", FlexDirection.ROW)
    elif node.tag == "column":
        style_dict.setdefault("flex_direction", FlexDirection.COLUMN)

    return style_dict


def _convert_style_value(style_key: str, value: Any) -> Any:
    """Convert a value using the appropriate converter."""
    converter = _STYLE_CONVERTERS.get(style_key)
    if converter:
        return converter(value)
    return value


def build_component(
    node: AUINode,
    stylesheet: Optional[StyleSheet],
    handlers: Mapping[str, Callable[..., Any]],
    components: Mapping[str, type[Any]],
    errors: Optional[ErrorCollector] = None,
) -> Optional[Node]:
    """
    Build an arepy-ui component from an AUI node.

    Args:
        node: The AUI node to build
        stylesheet: Optional stylesheet for styling
        handlers: Dictionary of event handler functions
        components: Dictionary of available component classes
        errors: Optional error collector for reporting issues

    Returns:
        Built component or None if tag is not supported
    """
    if errors is None:
        errors = ErrorCollector()

    tag = node.tag

    if tag not in TAG_TO_COMPONENT:
        errors.warning(
            f"Unknown tag '{tag}' will be ignored",
            tag=tag,
            line=getattr(node, "line_number", None),
        )
        return None

    component_name = TAG_TO_COMPONENT[tag]
    if component_name is None:
        return None

    ComponentClass = components.get(component_name)
    if ComponentClass is None:
        errors.warning(
            f"Component '{component_name}' not available",
            tag=tag,
            line=getattr(node, "line_number", None),
        )
        return None

    # Resolve styles
    style_props = resolve_styles(node, stylesheet)
    style = Style(**style_props) if style_props else None

    # Build component kwargs
    kwargs: Dict[str, Any] = {}

    if style:
        kwargs["style"] = style

    # Handle common attributes
    if "id" in node.attributes:
        kwargs["id"] = node.attributes["id"]

    # Tag-specific attribute handling (pass stylesheet for text color resolution)
    _apply_tag_attributes(tag, node, handlers, kwargs, stylesheet)

    # Special handling for ScrollView - needs content parameter
    if tag == "scroll":
        from arepy_ui.core.node import Node as CoreNode
        from arepy_ui.core.types import Unit

        # Build content container from children
        content = CoreNode(
            style=Style(
                width=Unit.percent(100),
                height=Unit.auto(),
            )
        )

        for child_node in node.children:
            child = build_component(
                child_node, stylesheet, handlers, components, errors
            )
            if child is not None:
                content.add_child(child)

        # Get dimensions from kwargs or use defaults
        width = kwargs.pop("width", Unit.percent(100))
        height = kwargs.pop("height", Unit.percent(100))
        scroll_style = kwargs.pop("style", None)
        element_id = kwargs.pop("id", None)

        try:
            component = ComponentClass(
                width=width,
                height=height,
                content=content,
                style=scroll_style,
                id=element_id,
            )
        except Exception as e:
            errors.error(
                f"Failed to create ScrollView: {e}",
                tag=tag,
                line=getattr(node, "line_number", None),
            )
            return None

        return component

    # Create the component
    try:
        component = ComponentClass(**kwargs)
    except Exception as e:
        errors.error(
            f"Failed to create {component_name}: {e}",
            tag=tag,
            line=getattr(node, "line_number", None),
        )
        return None

    # Build children (except for special cases)
    if tag not in ("select", "option", "scroll"):
        for child_node in node.children:
            if child_node.tag == "option":
                continue

            child = build_component(
                child_node, stylesheet, handlers, components, errors
            )
            if child is not None:
                component.add_child(child)

    return component


def _apply_tag_attributes(
    tag: str,
    node: AUINode,
    handlers: Mapping[str, Callable[..., Any]],
    kwargs: Dict[str, Any],
    stylesheet: Optional[StyleSheet] = None,
) -> None:
    """Apply tag-specific attributes to kwargs."""
    attrs = node.attributes

    if tag == "text":
        kwargs["text"] = node.text_content or attrs.get("text", "")
        if "size" in attrs:
            kwargs["size"] = float(attrs["size"])

        # Get color from: 1) attribute, 2) stylesheet, 3) default
        text_color = None
        if "color" in attrs:
            text_color = convert_to_color(attrs["color"])
        elif stylesheet:
            # Check ID styles first
            element_id = attrs.get("id")
            if element_id:
                id_styles = stylesheet.resolve_id(element_id)
                if "color" in id_styles:
                    text_color = convert_to_color(id_styles["color"])

            # Then check class styles
            if text_color is None:
                class_attr = attrs.get("class", "")
                for class_name in class_attr.split():
                    class_styles = stylesheet.resolve_class(class_name)
                    if "color" in class_styles:
                        text_color = convert_to_color(class_styles["color"])
                        break

        if text_color:
            kwargs["color"] = text_color

    elif tag == "button":
        kwargs["text"] = node.text_content or attrs.get("text", "Button")
        if "width" in attrs:
            kwargs["width"] = convert_to_unit(attrs["width"])
        if "height" in attrs:
            kwargs["height"] = convert_to_unit(attrs["height"])
        handler_name = attrs.get("on-click") or attrs.get("onclick")
        if handler_name and handler_name in handlers:
            kwargs["on_click"] = handlers[handler_name]
        else:
            # Default empty handler if no on_click provided
            kwargs["on_click"] = lambda: None

        # Resolve :hover pseudo-styles
        hover_styles = _resolve_pseudo_styles(node, stylesheet, "hover")
        if "background" in hover_styles or "background-color" in hover_styles:
            bg = hover_styles.get("background") or hover_styles.get("background-color")
            hover_color = convert_to_color(bg)
            if hover_color:
                kwargs["hover_color"] = hover_color

        # Resolve :active pseudo-styles
        active_styles = _resolve_pseudo_styles(node, stylesheet, "active")
        if "background" in active_styles or "background-color" in active_styles:
            bg = active_styles.get("background") or active_styles.get(
                "background-color"
            )
            pressed_color = convert_to_color(bg)
            if pressed_color:
                kwargs["pressed_color"] = pressed_color

    elif tag == "input":
        kwargs["placeholder"] = attrs.get("placeholder", "")
        if "value" in attrs:
            kwargs["text"] = attrs["value"]
        if "width" in attrs:
            kwargs["width"] = convert_to_unit(attrs["width"])
        if "height" in attrs:
            kwargs["height"] = convert_to_unit(attrs["height"])
        handler_name = attrs.get("on-change")
        if handler_name and handler_name in handlers:
            kwargs["on_change"] = handlers[handler_name]

    elif tag == "slider":
        kwargs["min_value"] = float(attrs.get("min", 0))
        kwargs["max_value"] = float(attrs.get("max", 100))
        kwargs["value"] = float(attrs.get("value", 50))
        handler_name = attrs.get("on-change")
        if handler_name and handler_name in handlers:
            kwargs["on_change"] = handlers[handler_name]

    elif tag == "checkbox":
        checked = attrs.get("checked", False)
        kwargs["checked"] = checked == "true" or checked is True
        handler_name = attrs.get("on-change")
        if handler_name and handler_name in handlers:
            kwargs["on_change"] = handlers[handler_name]

        # Resolve :hover pseudo-styles
        hover_styles = _resolve_pseudo_styles(node, stylesheet, "hover")
        if "background" in hover_styles or "background-color" in hover_styles:
            bg = hover_styles.get("background") or hover_styles.get("background-color")
            hover_color = convert_to_color(bg)
            if hover_color:
                kwargs["hover_color"] = hover_color

        # Resolve :active pseudo-styles
        active_styles = _resolve_pseudo_styles(node, stylesheet, "active")
        if "background" in active_styles or "background-color" in active_styles:
            bg = active_styles.get("background") or active_styles.get(
                "background-color"
            )
            pressed_color = convert_to_color(bg)
            if pressed_color:
                kwargs["pressed_color"] = pressed_color

    elif tag in ("image", "img"):
        kwargs["src"] = attrs.get("src", "")

    elif tag == "progress":
        kwargs["value"] = float(attrs.get("value", 0))
        kwargs["max_value"] = float(attrs.get("max", 100))

    elif tag == "video":
        kwargs["source"] = attrs.get("src", attrs.get("source", ""))
        if "width" in attrs:
            kwargs["width"] = convert_to_unit(attrs["width"])
        if "height" in attrs:
            kwargs["height"] = convert_to_unit(attrs["height"])
        kwargs["autoplay"] = attrs.get("autoplay", "false").lower() == "true"
        kwargs["loop"] = attrs.get("loop", "false").lower() == "true"
        kwargs["muted"] = attrs.get("muted", "false").lower() == "true"

    elif tag == "select":
        # Resolve :hover pseudo-styles
        hover_styles = _resolve_pseudo_styles(node, stylesheet, "hover")
        if "background" in hover_styles or "background-color" in hover_styles:
            bg = hover_styles.get("background") or hover_styles.get("background-color")
            hover_color = convert_to_color(bg)
            if hover_color:
                kwargs["hover_color"] = hover_color

        # Resolve :active pseudo-styles
        active_styles = _resolve_pseudo_styles(node, stylesheet, "active")
        if "background" in active_styles or "background-color" in active_styles:
            bg = active_styles.get("background") or active_styles.get(
                "background-color"
            )
            pressed_color = convert_to_color(bg)
            if pressed_color:
                kwargs["pressed_color"] = pressed_color

        # Extract options from child nodes
        options = []
        for child in node.children:
            if child.tag == "option":
                value = child.attributes.get("value", child.text_content or "")
                options.append(value)
        kwargs["options"] = options
        handler_name = attrs.get("on-change")
        if handler_name and handler_name in handlers:
            kwargs["on_select"] = handlers[handler_name]

    elif tag == "scroll":
        # Handle width/height from attributes
        if "width" in attrs:
            kwargs["width"] = convert_to_unit(attrs["width"])
        if "height" in attrs:
            kwargs["height"] = convert_to_unit(attrs["height"])

    elif tag == "colorpicker":
        # ColorPicker attributes
        if "width" in attrs:
            kwargs["width"] = convert_to_unit(attrs["width"])
        if "height" in attrs:
            kwargs["height"] = convert_to_unit(attrs["height"])
        if "color" in attrs:
            kwargs["color"] = convert_to_color(attrs["color"])
        if "show-alpha" in attrs:
            kwargs["show_alpha"] = attrs["show-alpha"].lower() == "true"
        if "show-preview" in attrs:
            kwargs["show_preview"] = attrs["show-preview"].lower() == "true"
        handler_name = attrs.get("on-change")
        if handler_name and handler_name in handlers:
            kwargs["on_change"] = handlers[handler_name]
