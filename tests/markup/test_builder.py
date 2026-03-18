"""Tests for markup builder."""

from unittest.mock import patch

import pytest

from arepy_ui.components.button import Button
from arepy_ui.components.scroll import ScrollView
from arepy_ui.components.text import Text
from arepy_ui.core.node import Node
from arepy_ui.core.types import Unit, UnitType
from arepy_ui.markup.builder import (
    _STYLE_CONVERTERS,
    _clear_builder_caches,
    _convert_style_value,
    build_component,
    resolve_styles,
)
from arepy_ui.markup.errors import ErrorCollector
from arepy_ui.markup.globals import clear_globals, load_globals_string, set_theme
from arepy_ui.markup.parsers import parse_acss, parse_aui

# Components dictionary needed by build_component
COMPONENTS = {
    "Node": Node,
    "Text": Text,
    "Button": Button,
    "ScrollView": ScrollView,
}


class TestStyleConverters:
    """Tests for style value converters."""

    def test_convert_style_value_width(self):
        result = _convert_style_value("width", "100px")
        assert isinstance(result, Unit)
        assert result.value == 100.0

    def test_convert_style_value_background_color(self):
        from arepy_ui.core.types import Color

        result = _convert_style_value("background_color", "#FF0000")
        assert isinstance(result, Color)
        assert result.r == 255

    def test_convert_style_value_gap(self):
        result = _convert_style_value("gap", 10)
        assert result == 10.0

    def test_convert_style_value_z_index(self):
        result = _convert_style_value("z_index", "5")
        assert result == 5

    def test_convert_style_value_unknown_returns_as_is(self):
        result = _convert_style_value("unknown_prop", "some_value")
        assert result == "some_value"

    def test_style_converters_dict_has_all_keys(self):
        expected_keys = [
            "width",
            "height",
            "min_width",
            "max_width",
            "min_height",
            "max_height",
            "top",
            "left",
            "right",
            "bottom",
            "padding",
            "margin",
            "flex_direction",
            "justify_content",
            "align_items",
            "position",
            "background_color",
            "text_color",
            "border_color",
            "gap",
            "border_width",
            "border_radius",
            "font_size",
            "opacity",
            "z_index",
        ]
        for key in expected_keys:
            assert key in _STYLE_CONVERTERS


class TestResolveStyles:
    """Tests for style resolution from stylesheet."""

    def setup_method(self):
        _clear_builder_caches()
        clear_globals()

    def teardown_method(self):
        _clear_builder_caches()
        clear_globals()

    def test_resolve_styles_with_id(self):
        aui_content = '<container id="main"></container>'
        css_content = """
        #main {
            width: 100%;
            height: 50px;
        }
        """
        root, _ = parse_aui(aui_content)
        stylesheet = parse_acss(css_content)
        assert root is not None

        styles = resolve_styles(root, stylesheet)
        # Builder converts to Unit objects
        assert styles is not None
        assert isinstance(styles.get("width"), Unit)
        assert styles.get("width").type == UnitType.PERCENT # type: ignore
        assert styles.get("width").value == 100.0 # type: ignore

    def test_resolve_styles_with_class(self):
        aui_content = '<container class="wrapper"></container>'
        css_content = """
        .wrapper {
            padding: 20px;
            background: #333;
        }
        """
        root, _ = parse_aui(aui_content)
        stylesheet = parse_acss(css_content)
        assert root is not None
        styles = resolve_styles(root, stylesheet)

        # Background is converted to background_color
        assert styles.get("background_color") is not None
        assert styles.get("padding") is not None

    def test_resolve_styles_with_multiple_classes(self):
        aui_content = '<container class="base highlight"></container>'
        css_content = """
        .base {
            padding: 10px;
        }
        .highlight {
            background: yellow;
        }
        """
        root, _ = parse_aui(aui_content)
        stylesheet = parse_acss(css_content)
        assert root is not None
        styles = resolve_styles(root, stylesheet)

        # Merged styles from both classes
        assert styles.get("padding") is not None

    def test_resolve_styles_empty_stylesheet(self):
        aui_content = "<container></container>"

        root, _ = parse_aui(aui_content)
        assert root is not None
        styles = resolve_styles(root, None)

        assert isinstance(styles, dict)

    def test_resolve_styles_reuses_cache_for_same_selector_signature(self):
        aui_content = '<container class="card"></container>'
        css_content = ".card { width: 100px; height: 50px; }"

        first_root, _ = parse_aui(aui_content)
        second_root, _ = parse_aui(aui_content)
        stylesheet = parse_acss(css_content)
        assert first_root is not None
        assert second_root is not None

        with patch(
            "arepy_ui.markup.builder._convert_style_value",
            wraps=_convert_style_value,
        ) as mock_convert:
            resolve_styles(first_root, stylesheet)
            first_call_count = mock_convert.call_count
            resolve_styles(second_root, stylesheet)

        assert first_call_count > 0
        assert mock_convert.call_count == first_call_count

    def test_resolve_styles_cache_invalidates_on_theme_change(self):
        load_globals_string(
            """
            :root { --fg: #111111; }
            :root.light { --fg: #eeeeee; }
            .headline { color: var(--fg); }
            """
        )
        root, _ = parse_aui('<text class="headline">Hello</text>')
        assert root is not None

        dark_styles = resolve_styles(root, None)
        set_theme("light")
        light_styles = resolve_styles(root, None)

        assert dark_styles["text_color"] != light_styles["text_color"]


class TestBuildComponent:
    """Tests for building components from AUI nodes."""

    def test_build_container(self):
        aui_content = '<container id="root"></container>'
        css_content = "#root { width: 100%; }"

        root, _ = parse_aui(aui_content)
        stylesheet = parse_acss(css_content)
        assert root is not None
        component = build_component(root, stylesheet, {}, COMPONENTS)

        assert isinstance(component, Node)
        assert component.id == "root"

    @pytest.mark.skip(reason="Requires arepy runtime configuration")
    def test_build_text(self):
        aui_content = '<text id="title">Hello World</text>'
        css_content = "#title { font-size: 24; }"

        root, _ = parse_aui(aui_content)
        stylesheet = parse_acss(css_content)

        assert root is not None
        component = build_component(root, stylesheet, {}, COMPONENTS)

        assert isinstance(component, Text)
        assert component.id == "title"
        assert component.text == "Hello World"

    @pytest.mark.skip(reason="Requires arepy runtime configuration")
    def test_build_button(self):
        aui_content = '<button id="submit">Click Me</button>'
        css_content = "#submit { background: #007bff; }"

        root, _ = parse_aui(aui_content)
        stylesheet = parse_acss(css_content)
        assert root is not None
        component = build_component(root, stylesheet, {}, COMPONENTS)

        assert isinstance(component, Button)
        assert component.id == "submit"

    def test_build_scroll(self):
        aui_content = """
        <scroll id="list">
            <text>Item 1</text>
            <text>Item 2</text>
        </scroll>
        """
        css_content = "#list { height: 200px; }"

        root, _ = parse_aui(aui_content)
        stylesheet = parse_acss(css_content)
        assert root is not None
        component = build_component(root, stylesheet, {}, COMPONENTS)

        assert isinstance(component, ScrollView)
        assert component.id == "list"

    def test_build_nested_components(self):
        aui_content = """
        <container id="parent">
            <container id="child1">
                <text>Nested</text>
            </container>
            <container id="child2"></container>
        </container>
        """
        css_content = ""

        root, _ = parse_aui(aui_content)
        stylesheet = parse_acss(css_content)
        assert root is not None
        component = build_component(root, stylesheet, {}, COMPONENTS)
        assert component is not None
        assert component.id == "parent"
        assert len(component.children) == 2
        assert component.children[0].id == "child1"
        assert component.children[1].id == "child2"

    def test_build_with_style_properties(self):
        aui_content = '<container id="styled"></container>'
        css_content = """
        #styled {
            width: 200px;
            height: 100px;
            background: #FF0000;
            padding: 10px;
        }
        """

        root, _ = parse_aui(aui_content)
        stylesheet = parse_acss(css_content)
        assert root is not None
        component = build_component(root, stylesheet, {}, COMPONENTS)
        assert component is not None
        assert component.style.width.value == 200.0
        assert component.style.height.value == 100.0
        assert component.style.background_color is not None
        assert component.style.background_color.r == 255

    @pytest.mark.skip(reason="Requires arepy runtime configuration")
    def test_build_with_handlers(self):
        aui_content = '<button id="btn">Click</button>'
        css_content = ""

        clicked = []
        handlers = {"btn": {"on_click": lambda: clicked.append(True)}}

        root, _ = parse_aui(aui_content)
        stylesheet = parse_acss(css_content)
        assert root is not None
        component = build_component(root, stylesheet, handlers, COMPONENTS) # type: ignore
        assert component is not None

        assert component.on_click is not None
        component.on_click()
        assert len(clicked) == 1


class TestBuildComplexLayouts:
    """Tests for building complex UI layouts."""

    def test_build_header_content_footer(self):
        aui_content = """
        <container id="app">
            <container id="header">
                <text>Header</text>
            </container>
            <container id="content">
                <text>Content</text>
            </container>
            <container id="footer">
                <text>Footer</text>
            </container>
        </container>
        """
        css_content = """
        #app {
            width: 100%;
            height: 100%;
            flex-direction: column;
        }
        #header {
            height: 60px;
        }
        #footer {
            height: 40px;
        }
        """

        root, _ = parse_aui(aui_content)
        stylesheet = parse_acss(css_content)
        assert root is not None
        component = build_component(root, stylesheet, {}, COMPONENTS)
        assert component is not None

        assert component.id == "app"
        assert len(component.children) == 3

        header = component.find_by_id("header")
        assert header is not None

        content = component.find_by_id("content")
        assert content is not None

        footer = component.find_by_id("footer")
        assert footer is not None

    def test_build_with_css_variables(self):
        aui_content = '<container id="themed"></container>'
        css_content = """
        :root {
            --primary: #007bff;
        }
        #themed {
            background: var(--primary);
        }
        """

        root, _ = parse_aui(aui_content)
        stylesheet = parse_acss(css_content)
        assert root is not None
        component = build_component(root, stylesheet, {}, COMPONENTS)
        assert component is not None

        # Variable should be resolved
        assert component.style.background_color is not None
        assert component.style.background_color.r == 0
        assert component.style.background_color.g == 123
        assert component.style.background_color.b == 255


class TestResolveStylesInlineAndCascade:
    """Tests for inline styles and cascade resolution."""

    def test_inline_style_overrides_stylesheet(self):
        aui_content = '<container id="box" style="width: 50px"></container>'
        css_content = "#box { width: 100px; }"

        root, _ = parse_aui(aui_content)
        stylesheet = parse_acss(css_content)
        assert root is not None
        styles = resolve_styles(root, stylesheet)

        # Inline should override stylesheet
        assert styles["width"].value == 50.0

    def test_id_selector_overrides_class(self):
        aui_content = '<container id="specific" class="general"></container>'
        css_content = """
        .general { width: 100px; }
        #specific { width: 200px; }
        """

        root, _ = parse_aui(aui_content)
        stylesheet = parse_acss(css_content)
        assert root is not None
        styles = resolve_styles(root, stylesheet)

        # ID should override class
        assert styles["width"].value == 200.0

    def test_row_tag_sets_flex_direction(self):
        from arepy_ui.core.types import FlexDirection

        aui_content = "<row></row>"
        root, _ = parse_aui(aui_content)
        assert root is not None
        styles = resolve_styles(root, None)

        assert styles.get("flex_direction") == FlexDirection.ROW

    def test_column_tag_sets_flex_direction(self):
        from arepy_ui.core.types import FlexDirection

        aui_content = "<column></column>"
        root, _ = parse_aui(aui_content)
        assert root is not None
        styles = resolve_styles(root, None)

        assert styles.get("flex_direction") == FlexDirection.COLUMN

    @patch("arepy_ui.core.fonts.get_font_manager")
    def test_text_color_is_resolved_once_from_styles(self, mock_fm):
        from arepy_ui.core.types import Color
        from arepy_ui.core.fonts import TextMetrics

        mock_fm.return_value.measure_text_ex.return_value = TextMetrics(100, 20, 24)

        aui_content = '<text class="headline">Title</text>'
        css_content = ".headline { color: #112233; }"

        root, _ = parse_aui(aui_content)
        stylesheet = parse_acss(css_content)
        assert root is not None

        component = build_component(root, stylesheet, {}, COMPONENTS)

        assert component is not None
        assert isinstance(component, Text)
        assert isinstance(component.color, Color)
        assert component.color.r == 17
        assert component.color.g == 34
        assert component.color.b == 51


class TestBuildComponentErrors:
    """Tests for error handling in build_component."""

    def test_unknown_tag_warning(self):
        aui_content = "<unknowntag></unknowntag>"
        root, _ = parse_aui(aui_content)
        assert root is not None
        errors = ErrorCollector()
        result = build_component(root, None, {}, COMPONENTS, errors)

        assert result is None
        assert errors.has_warnings  # property, not method

    def test_unavailable_component_warning(self):
        # Use a valid tag but don't include the component
        aui_content = "<canvas></canvas>"  # canvas not in COMPONENTS
        root, _ = parse_aui(aui_content)
        assert root is not None
        errors = ErrorCollector()
        result = build_component(root, None, {}, COMPONENTS, errors)

        assert result is None
        assert errors.has_warnings  # property, not method


class TestApplyTagAttributes:
    """Tests for tag-specific attribute handling."""

    def test_slider_attributes(self):
        from arepy_ui.components.slider import Slider

        components = {**COMPONENTS, "Slider": Slider}
        aui_content = '<slider min="10" max="90" value="50"></slider>'
        root, _ = parse_aui(aui_content)
        assert root is not None
        component = build_component(root, None, {}, components)
        assert component is not None
        assert isinstance(component, Slider)
        assert component.min_value == 10.0
        assert component.max_value == 90.0
        assert component.value == 50.0

    def test_checkbox_attributes(self):
        from arepy_ui.components.checkbox import Checkbox

        components = {**COMPONENTS, "Checkbox": Checkbox}
        # Checkbox is self-closing tag
        aui_content = '<checkbox checked="true" />'
        root, _ = parse_aui(aui_content)
        assert root is not None
        component = build_component(root, None, {}, components)

        assert component is not None
        assert isinstance(component, Checkbox)
        assert component.checked is True

    def test_progress_attributes(self):
        from arepy_ui.components.progressbar import ProgressBar

        components = {**COMPONENTS, "ProgressBar": ProgressBar}
        aui_content = '<progress value="75" max="100"></progress>'
        root, _ = parse_aui(aui_content)
        assert root is not None
        component = build_component(root, None, {}, components)
        assert isinstance(component, ProgressBar)

        assert component.value == 75.0
        assert component.max_value == 100.0

    def test_select_with_options(self):
        from arepy_ui.components.select import Select

        components = {**COMPONENTS, "Select": Select}
        aui_content = """
        <select>
            <option value="a">Option A</option>
            <option value="b">Option B</option>
            <option value="c">Option C</option>
        </select>
        """
        root, _ = parse_aui(aui_content)
        assert root is not None
        component = build_component(root, None, {}, components)
        assert component.options == ["a", "b", "c"] # type: ignore

    def test_input_attributes(self):
        from arepy_ui.components.input import TextInput

        components = {**COMPONENTS, "TextInput": TextInput}
        aui_content = '<input placeholder="Enter name" width="300px"></input>'
        root, _ = parse_aui(aui_content)
        assert root is not None
        component = build_component(root, None, {}, components)

        assert component.placeholder == "Enter name" # type: ignore

    @patch("arepy_ui.core.fonts.get_font_manager")
    def test_button_with_handler(self, mock_fm):
        from arepy_ui.core.fonts import TextMetrics

        mock_fm.return_value.measure_text_ex.return_value = TextMetrics(100, 20, 24)

        clicked = []
        handlers = {"handleClick": lambda: clicked.append(True)}

        aui_content = '<button on-click="handleClick">Click</button>'
        root, _ = parse_aui(aui_content)
        assert root is not None
        component = build_component(root, None, handlers, COMPONENTS)

        assert component is not None
        component.on_click() # type: ignore
        assert len(clicked) == 1

    def test_slider_with_on_change_handler(self):
        from arepy_ui.components.slider import Slider

        values = []
        handlers = {"onSlide": lambda v: values.append(v)}
        components = {**COMPONENTS, "Slider": Slider}

        aui_content = '<slider on-change="onSlide"></slider>'
        root, _ = parse_aui(aui_content)
        assert root is not None

        component = build_component(root, None, handlers, components)
        component.on_change(50) # type: ignore
        assert values == [50]
