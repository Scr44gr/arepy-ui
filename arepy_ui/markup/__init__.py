"""
AUI Markup System - HTML+CSS-like declarative UI for arepy-ui.

This module provides a markup language for building UIs declaratively:
- AUI files (.aui): HTML-like structure
- ACSS files (.acss): CSS-like styling

Example:
    >>> from arepy_ui.markup import load_aui, load_aui_string
    >>>
    >>> # Load from file
    >>> result = load_aui("ui/menu.aui", handlers={"on_click": handler})
    >>> if result.success:
    ...     ui_manager.set_root(result.root)
    >>>
    >>> # Load from string
    >>> result = load_aui_string("<container><text>Hello</text></container>")
"""

from arepy_ui.markup.errors import ErrorCollector, ErrorLevel, MarkupError, ParseResult
from arepy_ui.markup.globals import (
    clear_globals,
    get_global_styles,
    get_theme,
    load_globals,
    load_globals_string,
    set_theme,
)
from arepy_ui.markup.loader import load_aui, load_aui_string
from arepy_ui.markup.parsers import (
    AUINode,
    AUIParser,
    StyleRule,
    StyleSheet,
    parse_acss,
    parse_acss_file,
    parse_aui,
    parse_aui_file,
)

__all__ = [
    # Main API
    "load_aui",
    "load_aui_string",
    # Error handling
    "ParseResult",
    "MarkupError",
    "ErrorLevel",
    "ErrorCollector",
    # Parser classes
    "AUINode",
    "AUIParser",
    "StyleRule",
    "StyleSheet",
    # Parser functions
    "parse_aui",
    "parse_aui_file",
    "parse_acss",
    "parse_acss_file",
    # Global styles
    "load_globals",
    "load_globals_string",
    "set_theme",
    "get_theme",
    "clear_globals",
    "get_global_styles",
]
