"""Tests for AUI markup parser."""

import pytest

from arepy_ui.markup.parsers import AUINode, AUIParser, parse_aui, parse_aui_file


class TestAUINode:
    """Tests for AUINode class."""

    def test_node_creation(self):
        node = AUINode("container")
        assert node.tag == "container"
        assert node.attributes == {}
        assert node.children == []
        assert node.text_content == ""
        assert node.parent is None

    def test_node_with_attributes(self):
        node = AUINode("button", {"id": "submit", "class": "primary"})
        assert node.tag == "button"
        assert node.attributes["id"] == "submit"
        assert node.attributes["class"] == "primary"

    def test_node_get_id(self):
        node = AUINode("container", {"id": "main"})
        assert node.get_id() == "main"

    def test_node_get_id_empty(self):
        node = AUINode("container")
        assert node.get_id() == ""

    def test_node_get_class(self):
        node = AUINode("button", {"class": "btn primary"})
        assert node.get_class() == "btn primary"

    def test_node_get_classes(self):
        node = AUINode("button", {"class": "btn primary large"})
        classes = node.get_classes()
        assert classes == ["btn", "primary", "large"]

    def test_node_get_classes_empty(self):
        node = AUINode("button")
        assert node.get_classes() == []

    def test_node_add_child(self):
        parent = AUINode("container")
        child = AUINode("text")
        parent.add_child(child)

        assert len(parent.children) == 1
        assert parent.children[0] is child
        assert child.parent is parent

    def test_node_to_dict(self):
        parent = AUINode("container", {"id": "root"})
        child = AUINode("text")
        child.text_content = "Hello"
        parent.add_child(child)

        result = parent.to_dict()
        assert result["tag"] == "container"
        assert result["attributes"]["id"] == "root"
        assert len(result["children"]) == 1
        assert result["children"][0]["text"] == "Hello"


class TestAUIParser:
    """Tests for AUIParser class."""

    def test_parse_simple_tag(self):
        content = "<container></container>"
        root, errors = parse_aui(content)

        assert root is not None
        assert root.tag == "container"
        assert len(errors) == 0

    def test_parse_with_attributes(self):
        content = '<container id="main" class="wrapper"></container>'
        root, errors = parse_aui(content)

        assert root is not None
        assert root.get_id() == "main"
        assert root.get_class() == "wrapper"

    def test_parse_nested_tags(self):
        content = """
        <container>
            <text>Hello World</text>
        </container>
        """
        root, errors = parse_aui(content)

        assert root is not None
        assert root.tag == "container"
        assert len(root.children) == 1
        assert root.children[0].tag == "text"
        assert root.children[0].text_content == "Hello World"

    def test_parse_deeply_nested(self):
        content = """
        <container>
            <container>
                <container>
                    <text>Deep</text>
                </container>
            </container>
        </container>
        """
        root, errors = parse_aui(content)

        assert root is not None
        level1 = root.children[0]
        level2 = level1.children[0]
        level3 = level2.children[0]
        assert level3.tag == "text"
        assert level3.text_content == "Deep"

    def test_parse_multiple_children(self):
        content = """
        <container>
            <text>First</text>
            <text>Second</text>
            <text>Third</text>
        </container>
        """
        root, errors = parse_aui(content)

        assert root is not None
        assert len(root.children) == 3
        assert root.children[0].text_content == "First"
        assert root.children[1].text_content == "Second"
        assert root.children[2].text_content == "Third"

    def test_parse_self_closing_tag(self):
        content = """
        <container>
            <image src="test.png" />
        </container>
        """
        root, errors = parse_aui(content)

        assert root is not None
        assert len(root.children) == 1
        assert root.children[0].tag == "image"
        assert root.children[0].attributes.get("src") == "test.png"

    def test_parse_colorpicker_tag(self):
        content = '<colorpicker color="#ff0000" show-alpha="true" />'
        root, errors = parse_aui(content)

        assert root is not None
        assert root.tag == "colorpicker"
        assert errors == []

    def test_parse_button_tag(self):
        content = '<button id="submit" class="primary">Click Me</button>'
        root, errors = parse_aui(content)

        assert root is not None
        assert root.tag == "button"
        assert root.get_id() == "submit"
        assert root.text_content == "Click Me"

    def test_parse_with_quoted_attributes(self):
        content = '<text color="#FF0000" size="24">Red Text</text>'
        root, errors = parse_aui(content)

        assert root is not None
        assert root.attributes.get("color") == "#FF0000"
        assert root.attributes.get("size") == "24"

    def test_parse_scroll_container(self):
        content = """
        <scroll id="comments" class="scroll-area">
            <text>Comment 1</text>
            <text>Comment 2</text>
        </scroll>
        """
        root, errors = parse_aui(content)

        assert root is not None
        assert root.tag == "scroll"
        assert root.get_id() == "comments"
        assert len(root.children) == 2

    def test_parse_complex_layout(self):
        content = """
        <container id="root" class="main-layout">
            <container id="header" class="header">
                <text class="title">App Title</text>
            </container>
            <container id="content" class="content">
                <scroll class="scroll-area">
                    <text>Item 1</text>
                    <text>Item 2</text>
                </scroll>
            </container>
            <container id="footer" class="footer">
                <button id="action">Submit</button>
            </container>
        </container>
        """
        root, errors = parse_aui(content)

        assert root is not None
        assert root.get_id() == "root"
        assert len(root.children) == 3

        header = root.children[0]
        assert header.get_id() == "header"

        content_node = root.children[1]
        assert content_node.get_id() == "content"
        assert content_node.children[0].tag == "scroll"

        footer = root.children[2]
        assert footer.get_id() == "footer"

    def test_parse_empty_content(self):
        content = ""
        root, errors = parse_aui(content)
        assert root is None

    def test_parse_whitespace_only(self):
        content = "   \n\t   "
        root, errors = parse_aui(content)
        assert root is None

    def test_parser_errors_property(self):
        parser = AUIParser("<container>")
        parser.parse()
        # Parser should handle unclosed tags gracefully
        assert isinstance(parser.errors, list)

    def test_parse_reports_unclosed_tag(self):
        root, errors = parse_aui("<container>")

        assert root is not None
        assert any("Unclosed tag <container>" in error for error in errors)

    def test_parse_reports_unterminated_quoted_attribute(self):
        root, errors = parse_aui('<text value="broken></text>')

        assert root is not None
        assert any("Unterminated quoted attribute value" in error for error in errors)

    def test_parse_reports_missing_gt(self):
        root, errors = parse_aui("<container")

        assert root is not None
        assert any("Expected '>' after <container>" in error for error in errors)


class TestParseAUIFunction:
    """Tests for the parse_aui convenience function."""

    def test_parse_aui_returns_tuple(self):
        result = parse_aui("<container></container>")
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_parse_aui_valid_content(self):
        root, errors = parse_aui("<text>Hello</text>")
        assert root is not None
        assert root.tag == "text"
        assert isinstance(errors, list)

    def test_parse_aui_with_errors(self):
        # Malformed content - parser should return errors
        root, errors = parse_aui("<container>")
        # Even with errors, parser tries to recover
        assert isinstance(errors, list)
