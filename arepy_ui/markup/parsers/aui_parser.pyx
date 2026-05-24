# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
# pyright: reportMissingModuleSource=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportUnknownReturnType=false, reportGeneralTypeIssues=false
"""Cython-optimized AUI markup parser."""

from cpython.unicode cimport PyUnicode_READ_CHAR
from typing import List

from arepy_ui.markup.parsers.constants import SELF_CLOSING_TAGS, VALID_TAGS


ctypedef unsigned int Py_UCS4


cdef inline bint _is_whitespace(Py_UCS4 ch) noexcept:
    return ch == 32 or ch == 9 or ch == 10 or ch == 13


cdef inline bint _is_identifier_char(Py_UCS4 ch) noexcept:
    return (
        (48 <= ch <= 57)
        or (65 <= ch <= 90)
        or (97 <= ch <= 122)
        or ch == 95
        or ch == 45
        or ch == 58
    )


cdef inline bint _is_quote_char(Py_UCS4 ch) noexcept:
    return ch == 34 or ch == 39


cdef inline bint _contains_char(str chars, Py_UCS4 ch) noexcept:
    cdef Py_ssize_t index
    cdef Py_ssize_t length = len(chars)

    for index in range(length):
        if PyUnicode_READ_CHAR(chars, index) == ch:
            return True
    return False


cdef class AUINode:
    """Represents a parsed AUI element node."""

    cdef public str tag
    cdef public dict attributes
    cdef public list children
    cdef public str text_content
    cdef public object parent
    cdef public int line_number

    def __init__(self, str tag, dict attributes=None, int line_number=0):
        self.tag = tag
        self.attributes = attributes if attributes is not None else {}
        self.children = []
        self.text_content = ""
        self.parent = None
        self.line_number = line_number

    cpdef void add_child(self, AUINode child):
        child.parent = self
        self.children.append(child)

    cpdef str get_class(self):
        return str(self.attributes.get("class", ""))

    cpdef list get_classes(self):
        cdef str class_attr = self.get_class()
        if class_attr:
            return class_attr.split()
        return []

    cpdef str get_id(self):
        return str(self.attributes.get("id", ""))

    cpdef dict to_dict(self):
        cdef AUINode child
        return {
            "tag": self.tag,
            "attributes": self.attributes,
            "text": self.text_content,
            "children": [child.to_dict() for child in self.children],
        }

    def __repr__(self):
        return f"AUINode(tag={self.tag!r}, children={len(self.children)})"


cdef class AUIParser:
    """Parser for AUI markup syntax."""

    cdef str _content
    cdef Py_ssize_t _pos
    cdef Py_ssize_t _length
    cdef Py_ssize_t _line
    cdef list _errors

    def __init__(self, str content):
        self._content = content
        self._pos = 0
        self._length = len(content)
        self._line = 1
        self._errors = []

    @property
    def errors(self) -> List[str]:
        return self._errors

    cpdef AUINode parse(self):
        cdef AUINode root = None
        cdef AUINode node

        self._skip_whitespace()

        while self._pos < self._length:
            self._skip_whitespace()
            if self._pos >= self._length:
                break

            if self._match("<"):
                node = self._parse_element()
                if node is not None:
                    if root is None:
                        root = node
                    else:
                        self._errors.append(
                            f"Line {node.line_number}: Multiple root elements found"
                        )
            else:
                self._pos += 1

        return root

    cdef void _skip_whitespace(self):
        cdef Py_UCS4 char

        while self._pos < self._length:
            char = PyUnicode_READ_CHAR(self._content, self._pos)
            if char == 10:
                self._line += 1
                self._pos += 1
            elif char == 32 or char == 9 or char == 13:
                self._pos += 1
            else:
                break

    cdef bint _match(self, str text):
        return self._content.startswith(text, self._pos)

    cdef str _read_until(self, str chars):
        cdef Py_ssize_t start = self._pos
        cdef Py_UCS4 char

        while self._pos < self._length:
            char = PyUnicode_READ_CHAR(self._content, self._pos)
            if _contains_char(chars, char):
                break
            if char == 10:
                self._line += 1
            self._pos += 1

        return self._content[start:self._pos]

    cdef str _read_quoted_string(self):
        cdef Py_UCS4 quote_char = PyUnicode_READ_CHAR(self._content, self._pos)
        cdef Py_ssize_t start
        cdef Py_UCS4 char
        cdef str result

        self._pos += 1
        start = self._pos

        while self._pos < self._length:
            char = PyUnicode_READ_CHAR(self._content, self._pos)
            if char == 92 and self._pos + 1 < self._length:
                self._pos += 2
                continue
            if char == quote_char:
                break
            if char == 10:
                self._line += 1
            self._pos += 1

        result = self._content[start:self._pos]
        if self._pos < self._length:
            self._pos += 1
        else:
            self._errors.append(
                f"Line {self._line}: Unterminated quoted attribute value"
            )

        return result

    cdef str _read_identifier(self):
        cdef Py_ssize_t start = self._pos
        cdef Py_UCS4 char

        while self._pos < self._length:
            char = PyUnicode_READ_CHAR(self._content, self._pos)
            if _is_identifier_char(char):
                self._pos += 1
            else:
                break

        return self._content[start:self._pos]

    cdef dict _parse_attributes(self):
        cdef dict attrs = {}
        cdef str name
        cdef str value
        cdef Py_UCS4 char

        while self._pos < self._length:
            self._skip_whitespace()
            if self._pos >= self._length:
                break

            char = PyUnicode_READ_CHAR(self._content, self._pos)
            if char == 62 or char == 47:
                break

            name = self._read_identifier()
            if not name:
                self._errors.append(f"Line {self._line}: Invalid attribute syntax")
                self._pos += 1
                break

            self._skip_whitespace()
            if self._pos < self._length and PyUnicode_READ_CHAR(self._content, self._pos) == 61:
                self._pos += 1
                self._skip_whitespace()

                if self._pos < self._length:
                    char = PyUnicode_READ_CHAR(self._content, self._pos)
                    if _is_quote_char(char):
                        value = self._read_quoted_string()
                    else:
                        value = self._read_until(" \t\n\r>/")
                    attrs[name] = value
                else:
                    self._errors.append(
                        f"Line {self._line}: Missing value for attribute '{name}'"
                    )
            else:
                attrs[name] = True

        return attrs

    cdef AUINode _parse_element(self):
        cdef Py_ssize_t start_line = self._line
        cdef str tag
        cdef dict attrs
        cdef bint is_self_closing = 0
        cdef AUINode node

        self._pos += 1

        if self._match("!--"):
            self._pos += 3
            while self._pos < self._length:
                if self._match("-->"):
                    self._pos += 3
                    return None
                if PyUnicode_READ_CHAR(self._content, self._pos) == 10:
                    self._line += 1
                self._pos += 1
            self._errors.append(f"Line {start_line}: Unterminated comment")
            return None

        tag = self._read_identifier().lower()
        if not tag:
            self._errors.append(f"Line {start_line}: Empty tag name")
            return None

        if tag not in VALID_TAGS:
            self._errors.append(f"Line {start_line}: Unknown tag '{tag}'")

        attrs = self._parse_attributes()
        self._skip_whitespace()

        if self._pos < self._length and PyUnicode_READ_CHAR(self._content, self._pos) == 47:
            self._pos += 1
            is_self_closing = 1

        if self._pos < self._length and PyUnicode_READ_CHAR(self._content, self._pos) == 62:
            self._pos += 1
        else:
            self._errors.append(f"Line {start_line}: Expected '>' after <{tag}>")

        node = AUINode(tag, attrs, start_line)
        if is_self_closing or tag in SELF_CLOSING_TAGS:
            return node

        self._parse_children(node)
        return node

    cdef void _parse_children(self, AUINode parent):
        cdef str text
        cdef str close_tag
        cdef AUINode child
        cdef bint closed = False

        while self._pos < self._length:
            self._skip_whitespace()
            if self._pos >= self._length:
                break

            if self._match("</"):
                self._pos += 2
                close_tag = self._read_identifier().lower()
                self._read_until(">")
                if self._pos < self._length and PyUnicode_READ_CHAR(self._content, self._pos) == 62:
                    self._pos += 1
                else:
                    self._errors.append(
                        f"Line {self._line}: Unterminated closing tag for </{parent.tag}>"
                    )

                if close_tag != parent.tag:
                    self._errors.append(
                        f"Line {self._line}: Mismatched closing tag. "
                        f"Expected </{parent.tag}>, got </{close_tag}>"
                    )
                closed = True
                break

            if self._match("<"):
                child = self._parse_element()
                if child is not None:
                    parent.add_child(child)
            else:
                text = self._read_until("<").strip()
                if text:
                    parent.text_content = parent.text_content + text

        if not closed:
            self._errors.append(f"Line {parent.line_number}: Unclosed tag <{parent.tag}>")


cpdef tuple parse_aui(str content):
    cdef AUIParser parser = AUIParser(content)
    cdef AUINode root = parser.parse()
    return (root, parser.errors)


cpdef tuple parse_aui_file(str path):
    cdef str content
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return parse_aui(content)
