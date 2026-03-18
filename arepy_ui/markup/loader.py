"""
AUI Loader - Main API for loading AUI markup files.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
import re
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Union

from arepy_ui.markup.builder import build_component
from arepy_ui.markup.errors import ErrorCollector, ErrorLevel, MarkupError, ParseResult
from arepy_ui.markup.parsers import (
    parse_acss,
    parse_acss_file,
    parse_aui,
    parse_aui_file,
)
from arepy_ui.registry import get_registry

if TYPE_CHECKING:
    from arepy_ui.core.node import Node
    from arepy_ui.markup.parsers import AUINode, StyleSheet


@dataclass(slots=True)
class _AUIFileCacheEntry:
    mtime_ns: int
    size: int
    root_node: AUINode | None
    parser_errors: tuple[str, ...]


@dataclass(slots=True)
class _ACSSFileCacheEntry:
    mtime_ns: int
    size: int
    stylesheet: StyleSheet


_AUI_FILE_CACHE: Dict[str, _AUIFileCacheEntry] = {}
_ACSS_FILE_CACHE: Dict[str, _ACSSFileCacheEntry] = {}
_INLINE_STYLESHEET_CACHE: Dict[str, StyleSheet] = {}


def _normalize_path(path: str) -> str:
    return os.path.abspath(path)


def _clear_load_caches() -> None:
    """Clear cached parsed markup and stylesheet artifacts."""
    _AUI_FILE_CACHE.clear()
    _ACSS_FILE_CACHE.clear()
    _INLINE_STYLESHEET_CACHE.clear()


def _load_cached_aui_file(path: str) -> tuple[AUINode | None, list[str]]:
    normalized_path = _normalize_path(path)
    stat = os.stat(normalized_path)
    cached = _AUI_FILE_CACHE.get(normalized_path)
    if (
        cached is not None
        and cached.mtime_ns == stat.st_mtime_ns
        and cached.size == stat.st_size
    ):
        return cached.root_node, list(cached.parser_errors)

    root_node, parser_errors = parse_aui_file(normalized_path)
    _AUI_FILE_CACHE[normalized_path] = _AUIFileCacheEntry(
        mtime_ns=stat.st_mtime_ns,
        size=stat.st_size,
        root_node=root_node,
        parser_errors=tuple(parser_errors),
    )
    return root_node, list(parser_errors)


def _load_cached_acss_file(path: str) -> StyleSheet:
    normalized_path = _normalize_path(path)
    stat = os.stat(normalized_path)
    cached = _ACSS_FILE_CACHE.get(normalized_path)
    if (
        cached is not None
        and cached.mtime_ns == stat.st_mtime_ns
        and cached.size == stat.st_size
    ):
        return cached.stylesheet

    stylesheet = parse_acss_file(normalized_path)
    _ACSS_FILE_CACHE[normalized_path] = _ACSSFileCacheEntry(
        mtime_ns=stat.st_mtime_ns,
        size=stat.st_size,
        stylesheet=stylesheet,
    )
    return stylesheet


def _load_cached_inline_stylesheet(content: str) -> StyleSheet:
    cached = _INLINE_STYLESHEET_CACHE.get(content)
    if cached is not None:
        return cached

    stylesheet = parse_acss(content)
    _INLINE_STYLESHEET_CACHE[content] = stylesheet
    return stylesheet


def _get_components() -> Dict[str, type]:
    """Get all registered components from the registry."""
    return get_registry().get_components_dict()


def _convert_parser_errors(parser_errors: list) -> list[MarkupError]:
    result = []
    line_pattern = re.compile(r"Line (\d+):")

    for error_str in parser_errors:
        line = None
        match = line_pattern.search(error_str)
        if match:
            line = int(match.group(1))

        level = ErrorLevel.ERROR if "error" in error_str.lower() else ErrorLevel.WARNING
        result.append(
            MarkupError(
                level=level,
                message=error_str,
                line=line,
            )
        )

    return result


def load_aui(
    path: str,
    stylesheet: Optional[str] = None,
    handlers: Optional[Dict[str, Callable[..., Any]]] = None,
) -> ParseResult:
    """
    Load an AUI file and return a ParseResult with the root component and any errors.

    Args:
        path: Path to the .aui file
        stylesheet: Optional path to .acss file. If None, looks for same name as .aui
        handlers: Dictionary mapping handler names to functions

    Returns:
        ParseResult containing root Node and list of errors/warnings

    Example:
        >>> result = load_aui("ui/menu.aui", handlers={"start": on_start})
        >>> if result.success:
        ...     ui_manager.set_root(result.root)
        >>> for error in result.errors:
        ...     print(error)
    """
    handlers = handlers or {}
    components = _get_components()
    errors = ErrorCollector()

    root_node, parser_errors = _load_cached_aui_file(path)

    if parser_errors:
        for err in _convert_parser_errors(parser_errors):
            errors.errors.append(err)

    if root_node is None:
        errors.error(f"Failed to parse AUI file: {path}")
        return ParseResult(root=None, errors=errors.errors)

    css = None
    if stylesheet:
        css = _load_cached_acss_file(stylesheet)
    else:
        acss_path = os.path.splitext(path)[0] + ".acss"
        if os.path.exists(acss_path):
            css = _load_cached_acss_file(acss_path)

    component = build_component(root_node, css, handlers, components, errors)

    return ParseResult(root=component, errors=errors.errors)


def load_aui_string(
    content: str,
    stylesheet: Optional[Any] = None,
    handlers: Optional[Dict[str, Callable[..., Any]]] = None,
) -> ParseResult:
    """
    Load AUI from a string and return a ParseResult.

    Args:
        content: AUI markup string
        stylesheet: Optional ACSS stylesheet string or StyleSheet object
        handlers: Dictionary mapping handler names to functions

    Returns:
        ParseResult containing root Node and list of errors/warnings

    Example:
        >>> result = load_aui_string('''
        ...     <container class="panel">
        ...         <text>Hello World</text>
        ...     </container>
        ... ''')
        >>> if result:
        ...     ui_manager.set_root(result.root)
    """
    from arepy_ui.markup.parsers.css_parser import StyleSheet

    handlers = handlers or {}
    components = _get_components()
    errors = ErrorCollector()

    root_node, parser_errors = parse_aui(content)

    if parser_errors:
        for err in _convert_parser_errors(parser_errors):
            errors.errors.append(err)

    if root_node is None:
        errors.error("Failed to parse AUI content")
        return ParseResult(root=None, errors=errors.errors)

    css = None
    if stylesheet:
        if isinstance(stylesheet, StyleSheet):
            css = stylesheet
        else:
            css = _load_cached_inline_stylesheet(stylesheet)

    component = build_component(root_node, css, handlers, components, errors)

    return ParseResult(root=component, errors=errors.errors)
