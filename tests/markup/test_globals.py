"""Tests for global styles and theming."""

import pytest

from arepy_ui.markup.globals import (
    GlobalStyleRegistry,
    ThemeVariables,
    clear_globals,
    get_global_styles,
    get_theme,
    load_globals_string,
    set_theme,
)


class TestThemeVariables:
    """Tests for ThemeVariables class."""

    def test_theme_variables_creation(self):
        tv = ThemeVariables()

        assert tv.active is None

    def test_set_base_variables(self):
        tv = ThemeVariables()
        tv.set_base({"primary": "#ff0000", "secondary": "#00ff00"})

        assert tv.get("primary") == "#ff0000"
        assert tv.get("secondary") == "#00ff00"

    def test_add_variant(self):
        tv = ThemeVariables()
        tv.set_base({"bg": "#000000"})
        tv.add_variant("light", {"bg": "#ffffff"})

        assert tv.get("bg") == "#000000"

        tv.activate("light")

        assert tv.get("bg") == "#ffffff"

    def test_activate_variant(self):
        tv = ThemeVariables()
        tv.set_base({"color": "dark"})
        tv.add_variant("light", {"color": "light"})

        tv.activate("light")

        assert tv.active == "light"
        assert tv.get("color") == "light"

    def test_activate_none_returns_to_base(self):
        tv = ThemeVariables()
        tv.set_base({"color": "base"})
        tv.add_variant("alt", {"color": "alt"})

        tv.activate("alt")
        assert tv.get("color") == "alt"

        tv.activate(None)
        assert tv.get("color") == "base"

    def test_get_all_with_active_variant(self):
        tv = ThemeVariables()
        tv.set_base({"a": "1", "b": "2"})
        tv.add_variant("v1", {"a": "10"})

        tv.activate("v1")
        all_vars = tv.get_all()

        assert all_vars["a"] == "10"
        assert all_vars["b"] == "2"

    def test_get_nonexistent_variable(self):
        tv = ThemeVariables()
        tv.set_base({"exists": "yes"})

        assert tv.get("nonexistent") is None

    def test_clear(self):
        tv = ThemeVariables()
        tv.set_base({"var": "value"})
        tv.add_variant("v", {"var": "v"})
        tv.activate("v")

        tv.clear()

        assert tv.active is None
        assert tv.get("var") is None


class TestGlobalStyleRegistry:
    """Tests for GlobalStyleRegistry."""

    def setup_method(self):
        clear_globals()

    def teardown_method(self):
        clear_globals()

    def test_registry_singleton(self):
        r1 = GlobalStyleRegistry()
        r2 = GlobalStyleRegistry()

        assert r1 is r2

    def test_load_globals_string(self):
        load_globals_string(
            """
            :root {
                --bg: #1a1a1a;
            }
            .panel {
                background: var(--bg);
            }
        """
        )

        gs = get_global_styles()
        styles = gs.resolve_for_class("panel")

        assert styles.get("background") == "#1a1a1a"

    def test_theme_switching(self):
        load_globals_string(
            """
            :root {
                --bg: #000000;
            }
            :root.light {
                --bg: #ffffff;
            }
            .box {
                background: var(--bg);
            }
        """
        )

        gs = get_global_styles()

        assert gs.resolve_for_class("box").get("background") == "#000000"

        set_theme("light")

        assert gs.resolve_for_class("box").get("background") == "#ffffff"

    def test_get_theme(self):
        assert get_theme() is None

        set_theme("dark")

        assert get_theme() == "dark"

    def test_set_theme_none_returns_to_base(self):
        load_globals_string(
            """
            :root { --c: base; }
            :root.alt { --c: alt; }
            .t { color: var(--c); }
        """
        )

        set_theme("alt")
        gs = get_global_styles()
        assert gs.resolve_for_class("t").get("color") == "alt"

        set_theme(None)
        assert gs.resolve_for_class("t").get("color") == "base"

    def test_resolve_for_element(self):
        load_globals_string(
            """
            button {
                padding: 10px;
            }
        """
        )

        gs = get_global_styles()
        styles = gs.resolve_for_element("button")

        assert "padding" in styles

    def test_resolve_for_id(self):
        load_globals_string(
            """
            #main {
                width: 100%;
            }
        """
        )

        gs = get_global_styles()
        styles = gs.resolve_for_id("main")

        assert "width" in styles

    def test_resolve_for_classes_multiple(self):
        load_globals_string(
            """
            .a { color: red; }
            .b { background: blue; }
        """
        )

        gs = get_global_styles()
        styles = gs.resolve_for_classes(["a", "b"])

        assert "color" in styles
        assert "background" in styles

    def test_get_variable(self):
        load_globals_string(
            """
            :root {
                --primary: #007bff;
            }
        """
        )

        gs = get_global_styles()

        assert gs.get_variable("primary") == "#007bff"
        assert gs.get_variable("nonexistent") is None

    def test_get_all_variables(self):
        load_globals_string(
            """
            :root {
                --a: 1;
                --b: 2;
            }
        """
        )

        gs = get_global_styles()
        all_vars = gs.get_all_variables()

        assert all_vars.get("a") == "1"
        assert all_vars.get("b") == "2"

    def test_clear_globals(self):
        load_globals_string(
            """
            .test { color: red; }
        """
        )

        gs = get_global_styles()
        assert gs.resolve_for_class("test").get("color") is not None

        clear_globals()

        assert gs.resolve_for_class("test").get("color") is None

    def test_cache_invalidation_on_theme_change(self):
        load_globals_string(
            """
            :root { --c: dark; }
            :root.light { --c: light; }
            .item { color: var(--c); }
        """
        )

        gs = get_global_styles()

        gs.resolve_for_class("item")

        set_theme("light")
        styles = gs.resolve_for_class("item")

        assert styles.get("color") == "light"

    def test_multiple_global_stylesheets_merge_variables(self):
        load_globals_string(
            """
            :root { --base: #111111; }
            .panel { background: var(--base); }
            """
        )
        load_globals_string(
            """
            :root { --accent: #ff0000; }
            .badge { color: var(--accent); }
            """
        )

        gs = get_global_styles()

        assert gs.get_variable("base") == "#111111"
        assert gs.get_variable("accent") == "#ff0000"
        assert gs.resolve_for_class("panel").get("background") == "#111111"
        assert gs.resolve_for_class("badge").get("color") == "#ff0000"
