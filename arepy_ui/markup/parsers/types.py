"""Type definitions for the markup parsers."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Protocol, Tuple, TypeAlias

# Type aliases for better readability
AttributeDict: TypeAlias = Dict[str, Any]
HandlerDict: TypeAlias = Dict[str, Callable[..., Any]]
ParseResult: TypeAlias = Tuple[Optional["AUINodeProtocol"], List[str]]
StyleDict: TypeAlias = Dict[str, Any]


class AUINodeProtocol(Protocol):
    """Protocol for AUI node implementations."""

    tag: str
    attributes: AttributeDict
    children: List["AUINodeProtocol"]
    text_content: str
    parent: Optional["AUINodeProtocol"]
    line_number: int

    def add_child(self, child: "AUINodeProtocol") -> None: ...
    def get_class(self) -> str: ...
    def get_classes(self) -> List[str]: ...
    def get_id(self) -> str: ...
    def to_dict(self) -> Dict[str, Any]: ...


class StyleSheetProtocol(Protocol):
    """Protocol for stylesheet implementations."""

    variables: Dict[str, str]
    rules: List["StyleRuleProtocol"]

    def resolve_class(self, class_name: str) -> StyleDict: ...
    def resolve_classes(self, class_names: List[str]) -> StyleDict: ...
    def resolve_element(self, element_name: str) -> StyleDict: ...


class StyleRuleProtocol(Protocol):
    """Protocol for style rule implementations."""

    selector: str
    properties: StyleDict
    specificity: int
