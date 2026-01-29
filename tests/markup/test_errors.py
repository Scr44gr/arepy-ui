"""Tests for markup error handling."""

import pytest

from arepy_ui.markup.errors import ErrorCollector, ErrorLevel, MarkupError, ParseResult


class TestErrorLevel:
    """Tests for ErrorLevel enum."""

    def test_error_levels(self):
        assert ErrorLevel.WARNING.value == "warning"
        assert ErrorLevel.ERROR.value == "error"


class TestMarkupError:
    """Tests for MarkupError dataclass."""

    def test_error_creation_minimal(self):
        error = MarkupError(
            level=ErrorLevel.ERROR,
            message="Something went wrong",
        )

        assert error.level == ErrorLevel.ERROR
        assert error.message == "Something went wrong"
        assert error.line is None
        assert error.column is None
        assert error.tag is None

    def test_error_creation_full(self):
        error = MarkupError(
            level=ErrorLevel.WARNING,
            message="Unknown attribute",
            line=10,
            column=5,
            tag="button",
            attribute="onclick",
        )

        assert error.line == 10
        assert error.column == 5
        assert error.tag == "button"
        assert error.attribute == "onclick"

    def test_error_str_format_minimal(self):
        error = MarkupError(
            level=ErrorLevel.ERROR,
            message="Test error",
        )

        result = str(error)

        assert "[ERROR]" in result
        assert "Test error" in result

    def test_error_str_format_with_line(self):
        error = MarkupError(
            level=ErrorLevel.WARNING,
            message="Test warning",
            line=42,
        )

        result = str(error)

        assert "[WARNING]" in result
        assert "line 42" in result

    def test_error_str_format_with_line_and_column(self):
        error = MarkupError(
            level=ErrorLevel.ERROR,
            message="Error here",
            line=10,
            column=15,
        )

        result = str(error)

        assert "10:15" in result

    def test_error_str_format_with_tag(self):
        error = MarkupError(
            level=ErrorLevel.ERROR,
            message="Invalid tag",
            tag="badtag",
        )

        result = str(error)

        assert "<badtag>" in result


class TestErrorCollector:
    """Tests for ErrorCollector."""

    def test_collector_creation_empty(self):
        collector = ErrorCollector()

        assert len(collector.errors) == 0
        assert collector.has_errors is False
        assert collector.has_warnings is False

    def test_collector_add_warning(self):
        collector = ErrorCollector()

        collector.warning("This is a warning")

        assert len(collector.errors) == 1
        assert collector.errors[0].level == ErrorLevel.WARNING
        assert collector.has_warnings is True
        assert collector.has_errors is False

    def test_collector_add_error(self):
        collector = ErrorCollector()

        collector.error("This is an error")

        assert len(collector.errors) == 1
        assert collector.errors[0].level == ErrorLevel.ERROR
        assert collector.has_errors is True

    def test_collector_warning_with_details(self):
        collector = ErrorCollector()

        collector.warning(
            "Unknown attribute",
            line=5,
            column=10,
            tag="div",
            attribute="unknown",
        )

        error = collector.errors[0]
        assert error.line == 5
        assert error.column == 10
        assert error.tag == "div"
        assert error.attribute == "unknown"

    def test_collector_multiple_errors(self):
        collector = ErrorCollector()

        collector.warning("Warning 1")
        collector.error("Error 1")
        collector.warning("Warning 2")

        assert len(collector.errors) == 3
        assert collector.has_errors is True
        assert collector.has_warnings is True

    def test_collector_clear(self):
        collector = ErrorCollector()
        collector.error("Error")
        collector.warning("Warning")

        collector.clear()

        assert len(collector.errors) == 0
        assert collector.has_errors is False

    def test_collector_merge(self):
        collector1 = ErrorCollector()
        collector1.error("Error 1")

        collector2 = ErrorCollector()
        collector2.warning("Warning 1")

        collector1.merge(collector2)

        assert len(collector1.errors) == 2


class TestParseResult:
    """Tests for ParseResult."""

    def test_parse_result_success(self):
        from arepy_ui.core.node import Node

        node = Node()
        result = ParseResult(root=node, errors=[])

        assert result.success is True
        assert result.root is node
        assert bool(result) is True

    def test_parse_result_with_warnings_still_success(self):
        from arepy_ui.core.node import Node

        node = Node()
        warning = MarkupError(ErrorLevel.WARNING, "Just a warning")
        result = ParseResult(root=node, errors=[warning])

        assert result.success is True
        assert result.has_warnings is True

    def test_parse_result_with_errors_not_success(self):
        from arepy_ui.core.node import Node

        node = Node()
        error = MarkupError(ErrorLevel.ERROR, "An error")
        result = ParseResult(root=node, errors=[error])

        assert result.success is False

    def test_parse_result_no_root_not_success(self):
        result = ParseResult(root=None, errors=[])

        assert result.success is False
        assert bool(result) is False

    def test_parse_result_bool_with_root(self):
        from arepy_ui.core.node import Node

        result = ParseResult(root=Node())

        assert bool(result) is True

    def test_parse_result_bool_without_root(self):
        result = ParseResult(root=None)

        assert bool(result) is False
