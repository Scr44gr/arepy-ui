"""
AUI and ACSS parsers.

This subpackage contains the parsing infrastructure:
- aui_parser: HTML-like markup parser
- css_parser: CSS-like stylesheet parser

Cython implementations only.
Type hints provided via .pyi stub files.
"""

from arepy_ui.markup.parsers.aui_parser import (
    AUINode,
    AUIParser,
    parse_aui,
    parse_aui_file,
)
from arepy_ui.markup.parsers.css_parser import (
    StyleRule,
    StyleSheet,
    parse_acss,
    parse_acss_file,
)

__all__ = [
    # AUI Parser
    "AUINode",
    "AUIParser",
    "parse_aui",
    "parse_aui_file",
    # CSS Parser
    "StyleRule",
    "StyleSheet",
    "parse_acss",
    "parse_acss_file",
]
