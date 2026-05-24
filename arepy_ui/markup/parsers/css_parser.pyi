"""Type stubs for css_parser Cython module."""

from typing import Any, Dict, List

class StyleRule:
    """A CSS rule with selector and properties."""

    selector: str
    properties: Dict[str, Any]
    specificity: int

    def __init__(self, selector: str, properties: Dict[str, Any]) -> None: ...

class StyleSheet:
    """Parsed stylesheet with variables and rules."""

    variables: Dict[str, str]
    rules: List[StyleRule]

    def __init__(self) -> None: ...
    def resolve_class(self, class_name: str) -> Dict[str, Any]:
        """Get resolved properties for a class selector."""
        ...

    def resolve_classes(self, class_names: List[str]) -> Dict[str, Any]:
        """Get merged properties for multiple class selectors."""
        ...

    def resolve_id(self, id_name: str) -> Dict[str, Any]:
        """Get properties for an ID selector."""
        ...

    def resolve_element(self, element_name: str) -> Dict[str, Any]:
        """Get properties for an element selector."""
        ...

    def resolve_class_pseudo(self, class_name: str, pseudo: str) -> Dict[str, Any]:
        """Get resolved properties for a class selector with pseudo-state.

        Args:
            class_name: The class name (without dot)
            pseudo: The pseudo-selector (e.g., 'hover', 'active')

        Returns:
            Properties for .class_name:pseudo
        """
        ...

    def resolve_id_pseudo(self, id_name: str, pseudo: str) -> Dict[str, Any]:
        """Get resolved properties for an ID selector with pseudo-state.

        Args:
            id_name: The ID name (without hash)
            pseudo: The pseudo-selector (e.g., 'hover', 'active')

        Returns:
            Properties for #id_name:pseudo
        """
        ...

    def resolve_element_pseudo(self, element_name: str, pseudo: str) -> Dict[str, Any]:
        """Get resolved properties for an element selector with pseudo-state.

        Args:
            element_name: The element/tag name
            pseudo: The pseudo-selector (e.g., 'hover', 'active')

        Returns:
            Properties for element_name:pseudo
        """
        ...

def parse_acss(content: str) -> StyleSheet:
    """
    Parse ACSS content into a StyleSheet.

    Args:
        content: ACSS stylesheet string

    Returns:
        Parsed StyleSheet object
    """
    ...

def parse_acss_file(path: str) -> StyleSheet:
    """
    Parse an ACSS file.

    Args:
        path: Path to the .acss file

    Returns:
        Parsed StyleSheet object
    """
    ...
