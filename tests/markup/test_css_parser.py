"""Tests for ACSS (CSS-like) stylesheet parser."""

import pytest

from arepy_ui.markup.parsers import StyleRule, StyleSheet, parse_acss, parse_acss_file


class TestStyleRule:
    """Tests for StyleRule class."""

    def test_rule_creation(self):
        rule = StyleRule(".button", {"background": "#FF0000"})
        assert rule.selector == ".button"
        assert rule.properties["background"] == "#FF0000"

    def test_rule_specificity_class(self):
        rule = StyleRule(".button", {})
        assert rule.specificity == 10

    def test_rule_specificity_id(self):
        rule = StyleRule("#main", {})
        assert rule.specificity == 100

    def test_rule_specificity_element(self):
        rule = StyleRule("container", {})
        assert rule.specificity == 1


class TestStyleSheet:
    """Tests for StyleSheet class."""

    def test_stylesheet_creation(self):
        sheet = StyleSheet()
        assert sheet.variables == {}
        assert sheet.rules == []

    def test_resolve_class_basic(self):
        content = """
        .button {
            background: #007bff;
            padding: 10px;
        }
        """
        sheet = parse_acss(content)
        styles = sheet.resolve_class("button")

        assert styles["background"] == ("color", "#007bff")
        assert styles["padding"] == ("px", 10.0)

    def test_resolve_class_not_found(self):
        sheet = StyleSheet()
        styles = sheet.resolve_class("nonexistent")
        assert styles == {}

    def test_resolve_classes_multiple(self):
        content = """
        .base {
            padding: 10px;
        }
        .highlight {
            background: yellow;
        }
        """
        sheet = parse_acss(content)
        styles = sheet.resolve_classes(["base", "highlight"])

        assert styles["padding"] == ("px", 10.0)
        assert styles["background"] == "yellow"

    def test_resolve_id(self):
        content = """
        #header {
            height: 60px;
            background: #333;
        }
        """
        sheet = parse_acss(content)
        styles = sheet.resolve_id("header")

        assert styles["height"] == ("px", 60.0)
        assert styles["background"] == ("color", "#333")

    def test_resolve_id_not_found(self):
        sheet = StyleSheet()
        styles = sheet.resolve_id("nonexistent")
        assert styles == {}

    def test_resolve_element(self):
        content = """
        container {
            display: flex;
            flex-direction: column;
        }
        """
        sheet = parse_acss(content)
        styles = sheet.resolve_element("container")

        assert styles["display"] == "flex"
        assert styles["flex-direction"] == "column"


class TestACSSParsing:
    """Tests for ACSS parsing functionality."""

    def test_parse_simple_rule(self):
        content = ".box { width: 100px; }"
        sheet = parse_acss(content)

        assert len(sheet.rules) == 1
        assert sheet.rules[0].selector == ".box"

    def test_parse_multiple_rules(self):
        content = """
        .first { width: 100px; }
        .second { height: 200px; }
        .third { margin: 10px; }
        """
        sheet = parse_acss(content)
        assert len(sheet.rules) == 3

    def test_parse_css_variables(self):
        content = """
        :root {
            --primary-color: #007bff;
            --secondary-color: #6c757d;
            --spacing: 16px;
        }
        """
        sheet = parse_acss(content)

        assert sheet.variables["primary-color"] == "#007bff"
        assert sheet.variables["secondary-color"] == "#6c757d"
        assert sheet.variables["spacing"] == "16px"

    def test_parse_variable_reference(self):
        content = """
        :root {
            --primary: #007bff;
        }
        .button {
            background: var(--primary);
        }
        """
        sheet = parse_acss(content)
        styles = sheet.resolve_class("button")

        assert styles["background"] == "#007bff"

    def test_parse_pixel_values(self):
        content = ".box { width: 100px; height: 50px; }"
        sheet = parse_acss(content)
        styles = sheet.resolve_class("box")

        assert styles["width"] == ("px", 100.0)
        assert styles["height"] == ("px", 50.0)

    def test_parse_percent_values(self):
        content = ".box { width: 50%; height: 100%; }"
        sheet = parse_acss(content)
        styles = sheet.resolve_class("box")

        assert styles["width"] == ("percent", 50.0)
        assert styles["height"] == ("percent", 100.0)

    def test_parse_viewport_units(self):
        content = ".box { width: 100vw; height: 50vh; }"
        sheet = parse_acss(content)
        styles = sheet.resolve_class("box")

        # Viewport units are returned as strings
        assert styles["width"] == "100vw"
        assert styles["height"] == "50vh"

    def test_parse_auto_value(self):
        content = ".box { width: auto; }"
        sheet = parse_acss(content)
        styles = sheet.resolve_class("box")

        # auto is returned as tuple
        assert styles["width"] == ("auto",)

    def test_parse_hex_color(self):
        content = ".box { background: #FF5733; color: #333; }"
        sheet = parse_acss(content)
        styles = sheet.resolve_class("box")

        # Colors are returned as tuples
        assert styles["background"] == ("color", "#FF5733")
        assert styles["color"] == ("color", "#333")

    def test_parse_string_values(self):
        content = '.text { font-family: "Arial"; }'
        sheet = parse_acss(content)
        styles = sheet.resolve_class("text")

        assert styles["font-family"] == "Arial"

    def test_parse_numeric_values(self):
        content = ".box { opacity: 0.5; z-index: 10; }"
        sheet = parse_acss(content)
        styles = sheet.resolve_class("box")

        assert styles["opacity"] == 0.5
        assert styles["z-index"] == 10.0

    def test_parse_flex_direction(self):
        content = ".container { flex-direction: row; }"
        sheet = parse_acss(content)
        styles = sheet.resolve_class("container")

        assert styles["flex-direction"] == "row"

    def test_parse_justify_content(self):
        content = ".container { justify-content: center; }"
        sheet = parse_acss(content)
        styles = sheet.resolve_class("container")

        assert styles["justify-content"] == "center"

    def test_parse_align_items(self):
        content = ".container { align-items: flex-start; }"
        sheet = parse_acss(content)
        styles = sheet.resolve_class("container")

        assert styles["align-items"] == "flex-start"

    def test_parse_multi_value_padding(self):
        content = ".box { padding: 10px 20px; }"
        sheet = parse_acss(content)
        styles = sheet.resolve_class("box")

        # Multi-value padding should be parsed
        assert "padding" in styles

    def test_parse_empty_content(self):
        content = ""
        sheet = parse_acss(content)
        assert sheet.variables == {}
        assert sheet.rules == []

    def test_parse_whitespace_content(self):
        content = "   \n\t   "
        sheet = parse_acss(content)
        assert sheet.rules == []

    def test_parse_ignores_block_and_line_comments(self):
        content = """
        /* remove this */
        .first { width: 100px; }
        // and this too
        .second { height: 200px; }
        """
        sheet = parse_acss(content)

        assert len(sheet.rules) == 2
        assert sheet.resolve_class("first")["width"] == ("px", 100.0)
        assert sheet.resolve_class("second")["height"] == ("px", 200.0)


class TestACSSComplexStyles:
    """Tests for complex ACSS styling scenarios."""

    def test_youtube_style_layout(self):
        content = """
        :root {
            --bg-dark: #181818;
            --text-light: #FFFFFF;
            --accent: #FF0000;
        }

        #root {
            width: 100%;
            height: 100%;
            background: var(--bg-dark);
        }

        #header {
            height: 56px;
            background: var(--bg-dark);
            padding: 0 16px;
        }

        .video-title {
            font-size: 18;
            color: var(--text-light);
        }

        .like-button {
            background: transparent;
            color: var(--text-light);
            padding: 8px 16px;
        }

        .like-button:hover {
            background: rgba(255, 255, 255, 0.1);
        }
        """
        sheet = parse_acss(content)

        # Variables
        assert sheet.variables["bg-dark"] == "#181818"
        assert sheet.variables["text-light"] == "#FFFFFF"
        assert sheet.variables["accent"] == "#FF0000"

        # ID selector
        root_styles = sheet.resolve_id("root")
        assert root_styles["width"] == ("percent", 100.0)
        assert root_styles["background"] == "#181818"

        # Class selector with variable
        title_styles = sheet.resolve_class("video-title")
        assert title_styles["font-size"] == 18.0
        assert title_styles["color"] == "#FFFFFF"

    def test_style_cascade(self):
        content = """
        .base {
            color: black;
            font-size: 14;
        }
        .override {
            color: red;
        }
        """
        sheet = parse_acss(content)

        # When resolving multiple classes, later ones override
        styles = sheet.resolve_classes(["base", "override"])
        assert styles["color"] == "red"
        assert styles["font-size"] == 14.0

    def test_specificity_caching(self):
        content = """
        .button { background: blue; }
        #special { background: gold; }
        """
        sheet = parse_acss(content)

        # First call
        styles1 = sheet.resolve_class("button")
        # Second call (should use cache)
        styles2 = sheet.resolve_class("button")

        assert styles1 == styles2
        assert styles1["background"] == "blue"

    def test_complex_selector_parsing(self):
        content = """
        container {
            display: flex;
        }
        .wrapper {
            padding: 20px;
        }
        #main {
            width: 100%;
        }
        """
        sheet = parse_acss(content)

        # Element selector
        assert sheet.resolve_element("container")["display"] == "flex"

        # Class selector
        assert sheet.resolve_class("wrapper")["padding"] == ("px", 20.0)

        # ID selector
        assert sheet.resolve_id("main")["width"] == ("percent", 100.0)

    def test_pseudo_selectors_use_indexed_resolution(self):
        content = """
        .button:hover { background: #123456; }
        #hero:active { background: #654321; }
        text:hover { color: #abcdef; }
        """
        sheet = parse_acss(content)

        assert sheet.resolve_class_pseudo("button", "hover")["background"] == (
            "color",
            "#123456",
        )
        assert sheet.resolve_id_pseudo("hero", "active")["background"] == (
            "color",
            "#654321",
        )
        assert sheet.resolve_element_pseudo("text", "hover")["color"] == (
            "color",
            "#abcdef",
        )
