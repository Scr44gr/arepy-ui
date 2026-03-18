"""Type stubs for aui_parser Cython module."""

class AUINode:
    """Represents a parsed AUI element node."""

    tag: str
    attributes: dict[str, str | bool]
    children: list["AUINode"]
    text_content: str
    parent: "AUINode" | None
    line_number: int

    def __init__(
        self,
        tag: str,
        attributes: dict[str, str | bool] | None = None,
        line_number: int = 0,
    ) -> None: ...
    def add_child(self, child: "AUINode") -> None:
        """Add a child node."""
        ...

    def get_class(self) -> str:
        """Get the class attribute value."""
        ...

    def get_classes(self) -> list[str]:
        """Get list of class names."""
        ...

    def get_id(self) -> str:
        """Get the id attribute value."""
        ...

    def to_dict(self) -> dict[str, object]:
        """Convert node tree to dictionary representation."""
        ...

class AUIParser:
    """Parser for AUI markup syntax."""

    @property
    def errors(self) -> list[str]:
        """Get list of parsing errors."""
        ...

    def __init__(self, content: str) -> None: ...
    def parse(self) -> AUINode | None:
        """Parse the content and return the root node."""
        ...

def parse_aui(content: str) -> tuple[AUINode | None, list[str]]:
    """
    Parse AUI markup content.

    Args:
        content: AUI markup string

    Returns:
        Tuple of (root_node, errors)
    """
    ...

def parse_aui_file(path: str) -> tuple[AUINode | None, list[str]]:
    """
    Parse an AUI file.

    Args:
        path: Path to the .aui file

    Returns:
        Tuple of (root_node, errors)
    """
    ...
