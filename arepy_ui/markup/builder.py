"""
Component builder for converting AUI nodes to arepy-ui components.
"""

from __future__ import annotations

from collections import OrderedDict
from copy import copy
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Sequence

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

_MAX_RESOLVED_STYLE_CACHE_ENTRIES = 256
_MAX_INTERACTION_COLOR_CACHE_ENTRIES = 256
_MAX_TAG_ATTRIBUTE_PLAN_CACHE_ENTRIES = 256
_MAX_COMPILED_NODE_PLAN_CACHE_ENTRIES = 1024


@dataclass(slots=True)
class _TagAttributePlan:
    static_kwargs: Dict[str, Any]
    handler_bindings: tuple[tuple[tuple[str, ...], str, bool], ...]
    needs_interaction_colors: bool


@dataclass(slots=True)
class _CompiledNodePlan:
    node: AUINode
    component_name: Optional[str]
    child_plans: tuple["_CompiledNodePlan", ...]
    is_known_tag: bool
    is_scroll: bool


_RESOLVED_STYLE_CACHE: OrderedDict[tuple[object, ...], Dict[str, Any]] = OrderedDict()
_INTERACTION_COLOR_CACHE: OrderedDict[tuple[object, ...], Dict[str, Any]] = (
    OrderedDict()
)
_TAG_ATTRIBUTE_PLAN_CACHE: OrderedDict[tuple[object, ...], _TagAttributePlan] = (
    OrderedDict()
)
_COMPILED_NODE_PLAN_CACHE: OrderedDict[int, _CompiledNodePlan] = OrderedDict()

_NOOP_HANDLER = lambda: None


def _cache_get(
    cache: OrderedDict[tuple[object, ...], Dict[str, Any]],
    key: tuple[object, ...],
) -> Optional[Dict[str, Any]]:
    value = cache.get(key)
    if value is None:
        return None
    cache.move_to_end(key)
    return value


def _cache_put(
    cache: OrderedDict[tuple[object, ...], Dict[str, Any]],
    key: tuple[object, ...],
    value: Dict[str, Any],
    max_entries: int,
) -> None:
    cache[key] = value
    cache.move_to_end(key)
    if len(cache) > max_entries:
        cache.popitem(last=False)


def _clear_builder_caches() -> None:
    """Clear memoized style resolution state."""
    _RESOLVED_STYLE_CACHE.clear()
    _INTERACTION_COLOR_CACHE.clear()
    _TAG_ATTRIBUTE_PLAN_CACHE.clear()
    _COMPILED_NODE_PLAN_CACHE.clear()


def _build_style_cache_key(
    node: AUINode,
    stylesheet: Optional[StyleSheet],
    class_names: Sequence[str],
    element_id: Optional[str],
    globals_version: int,
) -> tuple[object, ...]:
    return (
        globals_version,
        id(stylesheet) if stylesheet is not None else None,
        node.tag,
        tuple(class_names),
        element_id,
        node.attributes.get("style", ""),
    )


def _build_interaction_cache_key(
    node: AUINode,
    stylesheet: Optional[StyleSheet],
    class_names: Sequence[str],
    element_id: Optional[str],
    globals_version: int,
) -> tuple[object, ...]:
    return (
        globals_version,
        id(stylesheet) if stylesheet is not None else None,
        node.tag,
        tuple(class_names),
        element_id,
    )


def _option_signature(node: AUINode) -> tuple[tuple[str, str], ...]:
    return tuple(
        (child.attributes.get("value", ""), child.text_content or "")
        for child in node.children
        if child.tag == "option"
    )


def _build_tag_attribute_plan_key(node: AUINode) -> tuple[object, ...]:
    attrs = node.attributes
    tag = node.tag

    if tag == "text":
        return (
            tag,
            node.text_content,
            attrs.get("text"),
            attrs.get("size"),
            attrs.get("color"),
        )
    if tag == "button":
        return (
            tag,
            node.text_content,
            attrs.get("text"),
            attrs.get("width"),
            attrs.get("height"),
        )
    if tag == "input":
        return (
            tag,
            attrs.get("placeholder"),
            attrs.get("value"),
            attrs.get("width"),
            attrs.get("height"),
        )
    if tag == "slider":
        return (tag, attrs.get("min"), attrs.get("max"), attrs.get("value"))
    if tag == "checkbox":
        return (tag, attrs.get("checked"))
    if tag in ("image", "img"):
        return (tag, attrs.get("src"))
    if tag == "progress":
        return (tag, attrs.get("value"), attrs.get("max"))
    if tag == "video":
        return (
            tag,
            attrs.get("src"),
            attrs.get("source"),
            attrs.get("width"),
            attrs.get("height"),
            attrs.get("autoplay"),
            attrs.get("loop"),
            attrs.get("muted"),
        )
    if tag == "select":
        return (tag, _option_signature(node))
    if tag == "scroll":
        return (tag, attrs.get("width"), attrs.get("height"))
    if tag == "colorpicker":
        return (
            tag,
            attrs.get("width"),
            attrs.get("height"),
            attrs.get("color"),
            attrs.get("show-alpha"),
            attrs.get("show-preview"),
        )

    return (tag,)


def _clone_plan_kwargs(static_kwargs: Dict[str, Any]) -> Dict[str, Any]:
    return {
        key: value.copy() if isinstance(value, list) else copy(value)
        for key, value in static_kwargs.items()
    }


def _build_tag_attribute_plan(node: AUINode) -> _TagAttributePlan:
    attrs = node.attributes
    tag = node.tag
    static_kwargs: Dict[str, Any] = {}
    handler_bindings: list[tuple[tuple[str, ...], str, bool]] = []
    needs_interaction_colors = False

    if tag == "text":
        static_kwargs["text"] = node.text_content or attrs.get("text", "")
        if "size" in attrs:
            static_kwargs["size"] = float(attrs["size"])
        if "color" in attrs:
            color = convert_to_color(attrs["color"])
            if color:
                static_kwargs["color"] = color

    elif tag == "button":
        static_kwargs["text"] = node.text_content or attrs.get("text", "Button")
        if "width" in attrs:
            static_kwargs["width"] = convert_to_unit(attrs["width"])
        if "height" in attrs:
            static_kwargs["height"] = convert_to_unit(attrs["height"])
        handler_bindings.append((("on-click", "onclick"), "on_click", True))
        needs_interaction_colors = True

    elif tag == "input":
        static_kwargs["placeholder"] = attrs.get("placeholder", "")
        if "value" in attrs:
            static_kwargs["text"] = attrs["value"]
        if "width" in attrs:
            static_kwargs["width"] = convert_to_unit(attrs["width"])
        if "height" in attrs:
            static_kwargs["height"] = convert_to_unit(attrs["height"])
        handler_bindings.append((("on-change",), "on_change", False))

    elif tag == "slider":
        static_kwargs["min_value"] = float(attrs.get("min", 0))
        static_kwargs["max_value"] = float(attrs.get("max", 100))
        static_kwargs["value"] = float(attrs.get("value", 50))
        handler_bindings.append((("on-change",), "on_change", False))

    elif tag == "checkbox":
        checked = attrs.get("checked", False)
        static_kwargs["checked"] = checked == "true" or checked is True
        handler_bindings.append((("on-change",), "on_change", False))
        needs_interaction_colors = True

    elif tag in ("image", "img"):
        static_kwargs["src"] = attrs.get("src", "")

    elif tag == "progress":
        static_kwargs["value"] = float(attrs.get("value", 0))
        static_kwargs["max_value"] = float(attrs.get("max", 100))

    elif tag == "video":
        static_kwargs["source"] = attrs.get("src", attrs.get("source", ""))
        if "width" in attrs:
            static_kwargs["width"] = convert_to_unit(attrs["width"])
        if "height" in attrs:
            static_kwargs["height"] = convert_to_unit(attrs["height"])
        static_kwargs["autoplay"] = attrs.get("autoplay", "false").lower() == "true"
        static_kwargs["loop"] = attrs.get("loop", "false").lower() == "true"
        static_kwargs["muted"] = attrs.get("muted", "false").lower() == "true"

    elif tag == "select":
        static_kwargs["options"] = [
            child.attributes.get("value", child.text_content or "")
            for child in node.children
            if child.tag == "option"
        ]
        handler_bindings.append((("on-change",), "on_select", False))
        needs_interaction_colors = True

    elif tag == "scroll":
        if "width" in attrs:
            static_kwargs["width"] = convert_to_unit(attrs["width"])
        if "height" in attrs:
            static_kwargs["height"] = convert_to_unit(attrs["height"])

    elif tag == "colorpicker":
        if "width" in attrs:
            static_kwargs["width"] = convert_to_unit(attrs["width"])
        if "height" in attrs:
            static_kwargs["height"] = convert_to_unit(attrs["height"])
        if "color" in attrs:
            static_kwargs["color"] = convert_to_color(attrs["color"])
        if "show-alpha" in attrs:
            static_kwargs["show_alpha"] = attrs["show-alpha"].lower() == "true"
        if "show-preview" in attrs:
            static_kwargs["show_preview"] = attrs["show-preview"].lower() == "true"
        handler_bindings.append((("on-change",), "on_change", False))

    return _TagAttributePlan(
        static_kwargs=static_kwargs,
        handler_bindings=tuple(handler_bindings),
        needs_interaction_colors=needs_interaction_colors,
    )


def _get_tag_attribute_plan(node: AUINode) -> _TagAttributePlan:
    cache_key = _build_tag_attribute_plan_key(node)
    cached = _TAG_ATTRIBUTE_PLAN_CACHE.get(cache_key)
    if cached is not None:
        _TAG_ATTRIBUTE_PLAN_CACHE.move_to_end(cache_key)
        return cached

    plan = _build_tag_attribute_plan(node)
    _TAG_ATTRIBUTE_PLAN_CACHE[cache_key] = plan
    _TAG_ATTRIBUTE_PLAN_CACHE.move_to_end(cache_key)
    if len(_TAG_ATTRIBUTE_PLAN_CACHE) > _MAX_TAG_ATTRIBUTE_PLAN_CACHE_ENTRIES:
        _TAG_ATTRIBUTE_PLAN_CACHE.popitem(last=False)
    return plan


def _compile_node_plan_uncached(node: AUINode) -> _CompiledNodePlan:
    tag = node.tag
    component_name = TAG_TO_COMPONENT.get(tag)
    is_known_tag = tag in TAG_TO_COMPONENT

    if tag == "scroll":
        child_plans = tuple(_compile_node_plan(child) for child in node.children)
    elif tag in ("select", "option"):
        child_plans = ()
    else:
        child_plans = tuple(
            _compile_node_plan(child)
            for child in node.children
            if child.tag != "option"
        )

    return _CompiledNodePlan(
        node=node,
        component_name=component_name,
        child_plans=child_plans,
        is_known_tag=is_known_tag,
        is_scroll=tag == "scroll",
    )


def _compile_node_plan(node: AUINode) -> _CompiledNodePlan:
    cache_key = id(node)
    cached = _COMPILED_NODE_PLAN_CACHE.get(cache_key)
    if cached is not None:
        _COMPILED_NODE_PLAN_CACHE.move_to_end(cache_key)
        return cached

    plan = _compile_node_plan_uncached(node)
    _COMPILED_NODE_PLAN_CACHE[cache_key] = plan
    _COMPILED_NODE_PLAN_CACHE.move_to_end(cache_key)
    if len(_COMPILED_NODE_PLAN_CACHE) > _MAX_COMPILED_NODE_PLAN_CACHE_ENTRIES:
        _COMPILED_NODE_PLAN_CACHE.popitem(last=False)
    return plan


def _resolve_pseudo_styles(
    node: AUINode,
    stylesheet: Optional[StyleSheet],
    pseudo: str,
    *,
    class_names: Sequence[str],
    element_id: Optional[str],
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
    globals_registry = get_global_styles()

    # 1. Global element pseudo-styles
    global_element = globals_registry.resolve_for_element_pseudo(node.tag, pseudo)
    result.update(global_element)

    # 2. Global class pseudo-styles
    for class_name in class_names:
        global_class = globals_registry.resolve_for_class_pseudo(class_name, pseudo)
        result.update(global_class)

    # 3. Global ID pseudo-styles
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
            for class_name in class_names:
                class_styles = stylesheet.resolve_class_pseudo(class_name, pseudo)
                result.update(class_styles)

        if hasattr(stylesheet, "resolve_id_pseudo") and element_id:
            id_styles = stylesheet.resolve_id_pseudo(element_id, pseudo)
            result.update(id_styles)

    return result


def _resolve_interaction_colors(
    node: AUINode,
    stylesheet: Optional[StyleSheet],
    *,
    class_names: Sequence[str],
    element_id: Optional[str],
) -> Dict[str, Any]:
    """Resolve hover and pressed colors for interactive components."""
    from arepy_ui.markup.globals import get_global_styles

    globals_version = get_global_styles().version
    cache_key = _build_interaction_cache_key(
        node, stylesheet, class_names, element_id, globals_version
    )
    cached = _cache_get(_INTERACTION_COLOR_CACHE, cache_key)
    if cached is not None:
        return cached.copy()

    kwargs: Dict[str, Any] = {}

    hover_styles = _resolve_pseudo_styles(
        node,
        stylesheet,
        "hover",
        class_names=class_names,
        element_id=element_id,
    )
    if "background" in hover_styles or "background-color" in hover_styles:
        bg = hover_styles.get("background") or hover_styles.get("background-color")
        hover_color = convert_to_color(bg)
        if hover_color:
            kwargs["hover_color"] = hover_color

    active_styles = _resolve_pseudo_styles(
        node,
        stylesheet,
        "active",
        class_names=class_names,
        element_id=element_id,
    )
    if "background" in active_styles or "background-color" in active_styles:
        bg = active_styles.get("background") or active_styles.get("background-color")
        pressed_color = convert_to_color(bg)
        if pressed_color:
            kwargs["pressed_color"] = pressed_color

    _cache_put(
        _INTERACTION_COLOR_CACHE,
        cache_key,
        kwargs.copy(),
        _MAX_INTERACTION_COLOR_CACHE_ENTRIES,
    )
    return kwargs


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
    class_names = tuple(node.get_classes())
    element_id = node.attributes.get("id")
    cache_key = _build_style_cache_key(
        node,
        stylesheet,
        class_names,
        element_id,
        globals_registry.version,
    )
    cached = _cache_get(_RESOLVED_STYLE_CACHE, cache_key)
    if cached is not None:
        return cached.copy()

    # 1. Global element styles (lowest priority)
    global_element = globals_registry.resolve_for_element(node.tag)
    for css_key, value in global_element.items():
        if css_key in CSS_TO_STYLE:
            style_key = CSS_TO_STYLE[css_key]
            style_dict[style_key] = _convert_style_value(style_key, value)

    # 2. Global class styles
    for class_name in class_names:
        global_class = globals_registry.resolve_for_class(class_name)
        for css_key, value in global_class.items():
            if css_key in CSS_TO_STYLE:
                style_key = CSS_TO_STYLE[css_key]
                style_dict[style_key] = _convert_style_value(style_key, value)

    # 3. Global ID styles
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
        for class_name in class_names:
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

    _cache_put(
        _RESOLVED_STYLE_CACHE,
        cache_key,
        style_dict.copy(),
        _MAX_RESOLVED_STYLE_CACHE_ENTRIES,
    )
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
    handlers: Dict[str, Callable[..., Any]],
    components: Dict[str, type],
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

    return _build_component_from_plan(
        _compile_node_plan(node),
        stylesheet,
        handlers,
        components,
        errors,
    )


def _build_component_from_plan(
    plan: _CompiledNodePlan,
    stylesheet: Optional[StyleSheet],
    handlers: Dict[str, Callable[..., Any]],
    components: Dict[str, type],
    errors: ErrorCollector,
) -> Optional[Node]:
    node = plan.node
    tag = node.tag
    line_number = getattr(node, "line_number", None)

    if not plan.is_known_tag:
        errors.warning(
            f"Unknown tag '{tag}' will be ignored",
            tag=tag,
            line=line_number,
        )
        return None

    component_name = plan.component_name
    if component_name is None:
        return None

    ComponentClass = components.get(component_name)
    if ComponentClass is None:
        errors.warning(
            f"Component '{component_name}' not available",
            tag=tag,
            line=line_number,
        )
        return None

    style_props = resolve_styles(node, stylesheet)
    style = Style(**style_props) if style_props else None

    kwargs: Dict[str, Any] = {}

    if style:
        kwargs["style"] = style

    if "id" in node.attributes:
        kwargs["id"] = node.attributes["id"]

    _apply_tag_attributes(
        tag,
        node,
        handlers,
        kwargs,
        style_props,
        stylesheet,
    )

    if plan.is_scroll:
        from arepy_ui.core.node import Node as CoreNode
        from arepy_ui.core.types import Unit

        # Build content container from children
        content = CoreNode(
            style=Style(
                width=Unit.percent(100),
                height=Unit.auto(),
            )
        )

        for child_plan in plan.child_plans:
            child = _build_component_from_plan(
                child_plan, stylesheet, handlers, components, errors
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
                line=line_number,
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
            line=line_number,
        )
        return None

    for child_plan in plan.child_plans:
        child = _build_component_from_plan(
            child_plan, stylesheet, handlers, components, errors
        )
        if child is not None:
            component.add_child(child)

    return component


def _apply_tag_attributes(
    tag: str,
    node: AUINode,
    handlers: Dict[str, Callable[..., Any]],
    kwargs: Dict[str, Any],
    style_props: Dict[str, Any],
    stylesheet: Optional[StyleSheet] = None,
) -> None:
    """Apply tag-specific attributes to kwargs."""
    attrs = node.attributes
    class_names = tuple(node.get_classes())
    element_id = attrs.get("id")
    plan = _get_tag_attribute_plan(node)
    kwargs.update(_clone_plan_kwargs(plan.static_kwargs))

    for attr_names, target_kwarg, use_default in plan.handler_bindings:
        handler_name = next(
            (attrs.get(name) for name in attr_names if attrs.get(name)), None
        )
        if handler_name and handler_name in handlers:
            kwargs[target_kwarg] = handlers[handler_name]
        elif use_default:
            kwargs[target_kwarg] = _NOOP_HANDLER

    if (
        tag == "text"
        and "color" not in kwargs
        and style_props.get("text_color") is not None
    ):
        kwargs["color"] = style_props["text_color"]

    if plan.needs_interaction_colors:
        kwargs.update(
            _resolve_interaction_colors(
                node,
                stylesheet,
                class_names=class_names,
                element_id=element_id,
            )
        )
