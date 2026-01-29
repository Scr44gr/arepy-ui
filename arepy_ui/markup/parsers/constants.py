"""Constants and configuration for the markup parsers."""

from __future__ import annotations

from typing import FrozenSet

# Self-closing tags (do not require closing tag)
SELF_CLOSING_TAGS: FrozenSet[str] = frozenset(
    [
        "image",
        "img",
        "progress",
        "slider",
        "checkbox",
        "video",
        "input",
        "br",
        "hr",
    ]
)

# Valid AUI element tags
VALID_TAGS: FrozenSet[str] = frozenset(
    [
        # Layout
        "container",
        "row",
        "column",
        "spacer",
        # Content
        "text",
        "button",
        "input",
        "select",
        "option",
        "slider",
        "checkbox",
        "image",
        "img",
        "scroll",
        "tabs",
        "tab",
        "progress",
        "canvas",
        "video",
        # Interactive
        "draggable",
        "dropzone",
        "modal",
        # Separators
        "br",
        "hr",
    ]
)

# Map of AUI tags to arepy-ui component names
TAG_TO_COMPONENT: dict[str, str | None] = {
    "container": "Node",
    "row": "Node",
    "column": "Node",
    "spacer": "Node",
    "text": "Text",
    "button": "Button",
    "input": "TextInput",
    "slider": "Slider",
    "checkbox": "Checkbox",
    "select": "Select",
    "option": None,  # Handled by parent Select
    "image": "Image",
    "img": "Image",
    "scroll": "ScrollView",
    "tabs": "Tabs",
    "tab": None,  # Handled by parent Tabs
    "progress": "ProgressBar",
    "canvas": "Canvas",
    "video": "Video",
    "draggable": "Draggable",
    "dropzone": "DropZone",
    "modal": "Modal",
    "colorpicker": "ColorPicker",
}

# Map of CSS property names to arepy-ui Style attribute names
CSS_TO_STYLE: dict[str, str] = {
    # Dimensions
    "width": "width",
    "height": "height",
    "min-width": "min_width",
    "max-width": "max_width",
    "min-height": "min_height",
    "max-height": "max_height",
    # Spacing
    "padding": "padding",
    "margin": "margin",
    "gap": "gap",
    # Flexbox
    "flex-direction": "flex_direction",
    "justify-content": "justify_content",
    "align-items": "align_items",
    # Positioning
    "position": "position",
    "top": "top",
    "left": "left",
    "right": "right",
    "bottom": "bottom",
    # Appearance
    "background": "background_color",
    "background-color": "background_color",
    "border-radius": "border_radius",
    "border-width": "border_width",
    "border-color": "border_color",
    "opacity": "opacity",
    # Text
    "color": "text_color",
    "font-size": "font_size",
    # Other
    "z-index": "z_index",
    "cursor": "cursor",
}
