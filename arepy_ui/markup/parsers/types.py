"""Type definitions for the markup parsers."""

from __future__ import annotations

from typing import Callable, Protocol, TypeAlias

# Type aliases for better readability
AttributeValue: TypeAlias = str | bool
AttributeDict: TypeAlias = dict[str, AttributeValue]
HandlerDict: TypeAlias = dict[str, Callable[..., object]]
ParseResult: TypeAlias = tuple["AUINodeProtocol" | None, list[str]]
StyleDict: TypeAlias = dict[str, object]


class AUINodeProtocol(Protocol):
    """Protocol for AUI node implementations."""

    tag: str
    attributes: AttributeDict
    children: list["AUINodeProtocol"]
    text_content: str
    parent: "AUINodeProtocol" | None
    line_number: int

    def add_child(self, child: "AUINodeProtocol") -> None: ...
    def get_class(self) -> str: ...
    def get_classes(self) -> list[str]: ...
    def get_id(self) -> str: ...
    def to_dict(self) -> dict[str, object]: ...


class StyleSheetProtocol(Protocol):
    """Protocol for stylesheet implementations."""

    variables: dict[str, str]
    rules: list["StyleRuleProtocol"]

    def resolve_class(self, class_name: str) -> StyleDict: ...
    def resolve_classes(self, class_names: list[str]) -> StyleDict: ...
    def resolve_element(self, element_name: str) -> StyleDict: ...


class StyleRuleProtocol(Protocol):
    """Protocol for style rule implementations."""

    selector: str
    properties: StyleDict
    specificity: int
