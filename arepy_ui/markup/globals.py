"""
Global stylesheet registry for theme support and shared styles.

Provides a cascading style system where:
1. Global styles (lowest priority)
2. Local stylesheet styles
3. Inline styles (highest priority)

Supports CSS variables with theme variants:
    :root {
        --bg: #1a1a1a;
        --text: #ffffff;
    }

    :root.light {
        --bg: #ffffff;
        --text: #1a1a1a;
    }
"""

from __future__ import annotations

import os
import re
from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    from arepy_ui.markup.parsers.css_parser import StyleSheet


class ThemeVariables:
    """Manages CSS variables with theme variant support."""

    __slots__ = ("_base", "_variants", "_active_variant")

    def __init__(self) -> None:
        self._base: Dict[str, str] = {}
        self._variants: Dict[str, Dict[str, str]] = {}
        self._active_variant: Optional[str] = None

    def set_base(self, variables: Dict[str, str]) -> None:
        """Set base :root variables."""
        self._base = variables.copy()

    def merge_base(self, variables: Dict[str, str]) -> None:
        """Merge base variables from an additional stylesheet."""
        self._base.update(variables)

    def add_variant(self, name: str, variables: Dict[str, str]) -> None:
        """Add a theme variant (e.g., 'light', 'dark')."""
        self._variants[name] = variables.copy()

    def merge_variant(self, name: str, variables: Dict[str, str]) -> None:
        """Merge variables into an existing theme variant."""
        existing = self._variants.setdefault(name, {})
        existing.update(variables)

    def activate(self, variant: Optional[str]) -> None:
        """Activate a theme variant. None returns to base."""
        self._active_variant = variant

    @property
    def active(self) -> Optional[str]:
        """Get currently active variant."""
        return self._active_variant

    def get(self, name: str) -> Optional[str]:
        """Get variable value with variant override."""
        if self._active_variant and self._active_variant in self._variants:
            variant_vars = self._variants[self._active_variant]
            if name in variant_vars:
                return variant_vars[name]
        return self._base.get(name)

    def get_all(self) -> Dict[str, str]:
        """Get all resolved variables for current theme."""
        result = self._base.copy()
        if self._active_variant and self._active_variant in self._variants:
            result.update(self._variants[self._active_variant])
        return result

    def clear(self) -> None:
        """Clear all variables."""
        self._base.clear()
        self._variants.clear()
        self._active_variant = None


class GlobalStyleRegistry:
    """
    Singleton registry for global stylesheets.

    Manages:
    - Multiple global stylesheets with priority ordering
    - CSS variables with theme variants
    - Cached merged styles for performance
    """

    _instance: Optional[GlobalStyleRegistry] = None

    _stylesheets: List[StyleSheet]
    _variables: ThemeVariables
    _cache: Dict[str, Dict[str, object]]
    _dirty: bool
    _version: int

    def __new__(cls) -> GlobalStyleRegistry:
        if cls._instance is None:
            instance = super().__new__(cls)
            instance._stylesheets = []
            instance._variables = ThemeVariables()
            instance._cache = {}
            instance._dirty = False
            instance._version = 0
            cls._instance = instance
        return cls._instance

    def load(self, path: str) -> None:
        """
        Load a global stylesheet file.

        Args:
            path: Path to .acss file
        """
        from arepy_ui.markup.parsers import parse_acss_file

        if not os.path.exists(path):
            from arepy_ui.logging import logger

            logger.warning(f"Global stylesheet not found: {path}")
            return

        sheet = parse_acss_file(path)
        self._add_stylesheet(sheet)

    def load_string(self, content: str) -> None:
        """
        Load global styles from a string.

        Args:
            content: ACSS content string
        """
        from arepy_ui.markup.parsers import parse_acss

        sheet = parse_acss(content)
        self._add_stylesheet(sheet)

    def _add_stylesheet(self, sheet: StyleSheet) -> None:
        """Add stylesheet and extract variables."""
        self._stylesheets.append(sheet)
        self._extract_variables(sheet)
        self._invalidate_cache()

    def _extract_variables(self, sheet: StyleSheet) -> None:
        """Extract :root and :root.variant variables."""
        self._variables.merge_base(sheet.variables)

        variant_pattern = re.compile(r":root\.(\w+)")
        for rule in sheet.rules:
            match = variant_pattern.match(rule.selector)
            if match:
                variant_name = match.group(1)
                variant_vars = self._parse_variant_variables(rule.properties)
                self._variables.merge_variant(variant_name, variant_vars)

    def _parse_variant_variables(self, props: Dict[str, object]) -> Dict[str, str]:
        """Extract CSS variables from properties dict."""
        result: Dict[str, str] = {}
        for key, value in props.items():
            if key.startswith("--"):
                var_name = key[2:]
                # Handle parsed color tuples like ('color', '#ffffff')
                if isinstance(value, tuple) and len(value) == 2 and value[0] == "color":
                    result[var_name] = str(value[1])
                else:
                    result[var_name] = str(value)
        return result

    def set_theme(self, variant: Optional[str]) -> None:
        """
        Activate a theme variant.

        Args:
            variant: Theme name (e.g., 'light', 'dark') or None for base
        """
        self._variables.activate(variant)
        self._invalidate_cache()

    @property
    def theme(self) -> Optional[str]:
        """Get currently active theme variant."""
        return self._variables.active

    @property
    def version(self) -> int:
        """Get the current cache version for invalidation-sensitive consumers."""
        return self._version

    def get_variable(self, name: str) -> Optional[str]:
        """Get a CSS variable value for current theme."""
        return self._variables.get(name)

    def get_all_variables(self) -> Dict[str, str]:
        """Get all CSS variables for current theme."""
        return self._variables.get_all()

    def resolve_for_element(self, tag: str) -> Dict[str, object]:
        """Get global styles for an element selector."""
        cache_key = f"e:{tag}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        result: Dict[str, object] = {}
        for sheet in self._stylesheets:
            result.update(sheet.raw_resolve_element(tag))

        result = self._resolve_variables_in_props(result)
        self._cache[cache_key] = result
        return result

    def resolve_for_class(self, class_name: str) -> Dict[str, object]:
        """Get global styles for a class selector."""
        cache_key = f"c:{class_name}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        result: Dict[str, object] = {}
        for sheet in self._stylesheets:
            result.update(sheet.raw_resolve_class(class_name))

        result = self._resolve_variables_in_props(result)
        self._cache[cache_key] = result
        return result

    def resolve_for_classes(self, class_names: List[str]) -> Dict[str, object]:
        """Get merged global styles for multiple classes."""
        result: Dict[str, object] = {}
        for name in class_names:
            result.update(self.resolve_for_class(name))
        return result

    def resolve_for_id(self, id_name: str) -> Dict[str, object]:
        """Get global styles for an ID selector."""
        cache_key = f"i:{id_name}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        result: Dict[str, object] = {}
        for sheet in self._stylesheets:
            result.update(sheet.raw_resolve_id(id_name))

        result = self._resolve_variables_in_props(result)
        self._cache[cache_key] = result
        return result

    def resolve_for_element_pseudo(self, tag: str, pseudo: str) -> Dict[str, object]:
        """Get global styles for an element selector with pseudo-state."""
        cache_key = f"e:{tag}:{pseudo}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        result: Dict[str, object] = {}
        for sheet in self._stylesheets:
            result.update(sheet.raw_resolve_element_pseudo(tag, pseudo))

        result = self._resolve_variables_in_props(result)
        self._cache[cache_key] = result
        return result

    def resolve_for_class_pseudo(
        self, class_name: str, pseudo: str
    ) -> Dict[str, object]:
        """Get global styles for a class selector with pseudo-state."""
        cache_key = f"c:{class_name}:{pseudo}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        result: Dict[str, object] = {}
        for sheet in self._stylesheets:
            result.update(sheet.raw_resolve_class_pseudo(class_name, pseudo))

        result = self._resolve_variables_in_props(result)
        self._cache[cache_key] = result
        return result

    def resolve_for_id_pseudo(self, id_name: str, pseudo: str) -> Dict[str, object]:
        """Get global styles for an ID selector with pseudo-state."""
        cache_key = f"i:{id_name}:{pseudo}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        result: Dict[str, object] = {}
        for sheet in self._stylesheets:
            result.update(sheet.raw_resolve_id_pseudo(id_name, pseudo))

        result = self._resolve_variables_in_props(result)
        self._cache[cache_key] = result
        return result

    def _resolve_variables_in_props(
        self, props: Dict[str, object]
    ) -> Dict[str, object]:
        """Replace var(--name) with current theme values."""
        var_pattern = re.compile(r"var\(--([a-zA-Z0-9_-]+)\)")
        result: Dict[str, object] = {}

        for key, value in props.items():
            if isinstance(value, str) and "var(" in value:
                match = var_pattern.search(value)
                if match:
                    var_name = match.group(1)
                    var_value = self._variables.get(var_name)
                    if var_value is not None:
                        value = var_pattern.sub(var_value, value)
            result[key] = value

        return result

    def _invalidate_cache(self) -> None:
        """Clear cached resolved styles."""
        self._cache.clear()
        self._dirty = True
        self._version += 1

    def clear(self) -> None:
        """Clear all global stylesheets and variables."""
        self._stylesheets.clear()
        self._variables.clear()
        self._cache.clear()
        self._dirty = False
        self._version += 1


_registry: Optional[GlobalStyleRegistry] = None


def get_global_styles() -> GlobalStyleRegistry:
    """Get the global style registry singleton."""
    global _registry
    if _registry is None:
        _registry = GlobalStyleRegistry()
    return _registry


def load_globals(path: str) -> None:
    """
    Load a global stylesheet.

    Args:
        path: Path to .acss file

    Example:
        >>> load_globals("assets/ui/globals.acss")
    """
    get_global_styles().load(path)


def load_globals_string(content: str) -> None:
    """
    Load global styles from a string.

    Args:
        content: ACSS content

    Example:
        >>> load_globals_string('''
        ...     :root {
        ...         --primary: #007bff;
        ...     }
        ...     .panel {
        ...         background: var(--primary);
        ...     }
        ... ''')
    """
    get_global_styles().load_string(content)


def set_theme(variant: Optional[str]) -> None:
    """
    Set the active theme variant.

    Args:
        variant: Theme name or None for base theme

    Example:
        >>> set_theme("light")  # Activate light theme
        >>> set_theme(None)     # Return to base/dark theme
    """
    get_global_styles().set_theme(variant)


def get_theme() -> Optional[str]:
    """Get the currently active theme variant."""
    return get_global_styles().theme


def clear_globals() -> None:
    """Clear all global stylesheets."""
    get_global_styles().clear()
