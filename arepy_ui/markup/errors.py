"""
Markup error handling and reporting system.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from ..core.node import Node


class ErrorLevel(Enum):
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class MarkupError:
    level: ErrorLevel
    message: str
    line: Optional[int] = None
    column: Optional[int] = None
    tag: Optional[str] = None
    attribute: Optional[str] = None

    def __str__(self) -> str:
        parts = [f"[{self.level.value.upper()}]"]

        if self.line is not None:
            loc = f"line {self.line}"
            if self.column is not None:
                loc += f":{self.column}"
            parts.append(f"({loc})")

        if self.tag:
            parts.append(f"<{self.tag}>:")

        parts.append(self.message)
        return " ".join(parts)


@dataclass
class ErrorCollector:
    errors: List[MarkupError] = field(default_factory=list)

    def warning(
        self,
        message: str,
        *,
        line: Optional[int] = None,
        column: Optional[int] = None,
        tag: Optional[str] = None,
        attribute: Optional[str] = None,
    ) -> None:
        self.errors.append(
            MarkupError(
                level=ErrorLevel.WARNING,
                message=message,
                line=line,
                column=column,
                tag=tag,
                attribute=attribute,
            )
        )

    def error(
        self,
        message: str,
        *,
        line: Optional[int] = None,
        column: Optional[int] = None,
        tag: Optional[str] = None,
        attribute: Optional[str] = None,
    ) -> None:
        self.errors.append(
            MarkupError(
                level=ErrorLevel.ERROR,
                message=message,
                line=line,
                column=column,
                tag=tag,
                attribute=attribute,
            )
        )

    @property
    def has_errors(self) -> bool:
        return any(e.level == ErrorLevel.ERROR for e in self.errors)

    @property
    def has_warnings(self) -> bool:
        return any(e.level == ErrorLevel.WARNING for e in self.errors)

    def clear(self) -> None:
        self.errors.clear()

    def merge(self, other: "ErrorCollector") -> None:
        self.errors.extend(other.errors)


@dataclass
class ParseResult:
    root: Optional["Node"] = None
    errors: List[MarkupError] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return self.root is not None and not any(
            e.level == ErrorLevel.ERROR for e in self.errors
        )

    @property
    def has_warnings(self) -> bool:
        return any(e.level == ErrorLevel.WARNING for e in self.errors)

    def __bool__(self) -> bool:
        return self.root is not None
