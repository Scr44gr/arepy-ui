# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
"""Cython-optimized AUI markup parser."""

from typing import Any, Dict, List, Optional, Tuple

from arepy_ui.markup.parsers.constants import SELF_CLOSING_TAGS, VALID_TAGS


cdef class AUINode:
    """Represents a parsed AUI element node."""
    
    cdef public str tag
    cdef public dict attributes
    cdef public list children
    cdef public str text_content
    cdef public object parent  # Optional[AUINode]
    cdef public int line_number
    
    def __init__(self, str tag, dict attributes=None, int line_number=0):
        self.tag = tag
        self.attributes = attributes if attributes is not None else {}
        self.children = []
        self.text_content = ""
        self.parent = None
        self.line_number = line_number
    
    cpdef void add_child(self, AUINode child):
        """Add a child node."""
        child.parent = self
        self.children.append(child)
    
    cpdef str get_class(self):
        """Get the class attribute value."""
        return str(self.attributes.get("class", ""))
    
    cpdef list get_classes(self):
        """Get list of class names."""
        cdef str class_attr = self.get_class()
        if class_attr:
            return class_attr.split()
        return []
    
    cpdef str get_id(self):
        """Get the id attribute value."""
        return str(self.attributes.get("id", ""))
    
    cpdef dict to_dict(self):
        """Convert node tree to dictionary representation."""
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
    cdef int _pos
    cdef int _length
    cdef int _line
    cdef list _errors
    
    def __init__(self, str content):
        self._content = content
        self._pos = 0
        self._length = len(content)
        self._line = 1
        self._errors = []
    
    @property
    def errors(self) -> List[str]:
        """Get list of parsing errors."""
        return self._errors
    
    cpdef AUINode parse(self):
        """Parse the content and return the root node."""
        self._skip_whitespace()
        
        cdef AUINode root = None
        cdef AUINode node
        
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
        """Skip whitespace characters, tracking line numbers."""
        cdef str char
        while self._pos < self._length:
            char = self._content[self._pos]
            if char == "\n":
                self._line += 1
                self._pos += 1
            elif char == " " or char == "\t" or char == "\r":
                self._pos += 1
            else:
                break
    
    cdef bint _match(self, str text):
        """Check if text matches at current position."""
        cdef int text_len = len(text)
        return self._content[self._pos:self._pos + text_len] == text
    
    cdef str _read_until(self, str chars):
        """Read characters until one of the specified chars is found."""
        cdef int start = self._pos
        cdef str char
        while self._pos < self._length:
            char = self._content[self._pos]
            if char in chars:
                break
            if char == "\n":
                self._line += 1
            self._pos += 1
        return self._content[start:self._pos]
    
    cdef str _read_quoted_string(self):
        """Read a quoted string value."""
        cdef str quote_char = self._content[self._pos]
        self._pos += 1
        cdef int start = self._pos
        cdef str char
        
        while self._pos < self._length:
            char = self._content[self._pos]
            if char == "\\" and self._pos + 1 < self._length:
                self._pos += 2
            elif char == quote_char:
                break
            else:
                if char == "\n":
                    self._line += 1
                self._pos += 1
        
        cdef str result = self._content[start:self._pos]
        if self._pos < self._length:
            self._pos += 1
        
        return result
    
    cdef str _read_identifier(self):
        """Read an identifier (tag name, attribute name)."""
        cdef int start = self._pos
        cdef str char
        while self._pos < self._length:
            char = self._content[self._pos]
            if char.isalnum() or char == "_" or char == "-" or char == ":":
                self._pos += 1
            else:
                break
        return self._content[start:self._pos]
    
    cdef dict _parse_attributes(self):
        """Parse element attributes."""
        cdef dict attrs = {}
        cdef str name, value, char
        
        while self._pos < self._length:
            self._skip_whitespace()
            
            if self._pos >= self._length:
                break
            
            char = self._content[self._pos]
            if char == ">" or char == "/":
                break
            
            name = self._read_identifier()
            if not name:
                break
            
            self._skip_whitespace()
            
            if self._pos < self._length and self._content[self._pos] == "=":
                self._pos += 1
                self._skip_whitespace()
                
                if self._pos < self._length:
                    char = self._content[self._pos]
                    if char == '"' or char == "'":
                        value = self._read_quoted_string()
                    else:
                        value = self._read_until(" \t\n\r>/")
                    attrs[name] = value
            else:
                attrs[name] = True
        
        return attrs
    
    cdef AUINode _parse_element(self):
        """Parse a single element."""
        cdef int start_line = self._line
        self._pos += 1  # Skip <
        
        # Check for comment
        if self._match("!--"):
            self._pos += 3
            while self._pos < self._length:
                if self._match("-->"):
                    self._pos += 3
                    break
                if self._content[self._pos] == "\n":
                    self._line += 1
                self._pos += 1
            return None
        
        # Read tag name
        cdef str tag = self._read_identifier().lower()
        
        if not tag:
            self._errors.append(f"Line {start_line}: Empty tag name")
            return None
        
        if tag not in VALID_TAGS:
            self._errors.append(f"Line {start_line}: Unknown tag '{tag}'")
        
        # Parse attributes
        cdef dict attrs = self._parse_attributes()
        
        self._skip_whitespace()
        
        # Check for self-closing
        cdef bint is_self_closing = 0
        if self._pos < self._length and self._content[self._pos] == "/":
            self._pos += 1
            is_self_closing = 1
        
        # Skip >
        if self._pos < self._length and self._content[self._pos] == ">":
            self._pos += 1
        
        cdef AUINode node = AUINode(tag, attrs, start_line)
        
        # Self-closing tags don't have children
        if is_self_closing or tag in SELF_CLOSING_TAGS:
            return node
        
        # Parse children
        self._parse_children(node)
        
        return node
    
    cdef void _parse_children(self, AUINode parent):
        """Parse child elements and text content."""
        cdef str text, close_tag
        cdef AUINode child
        
        while self._pos < self._length:
            self._skip_whitespace()
            
            if self._pos >= self._length:
                break
            
            # Check for closing tag
            if self._match("</"):
                self._pos += 2
                close_tag = self._read_identifier().lower()
                self._read_until(">")
                if self._pos < self._length:
                    self._pos += 1
                
                if close_tag != parent.tag:
                    self._errors.append(
                        f"Line {self._line}: Mismatched closing tag. "
                        f"Expected </{parent.tag}>, got </{close_tag}>"
                    )
                break
            
            # Check for new element
            if self._match("<"):
                child = self._parse_element()
                if child is not None:
                    parent.add_child(child)
            else:
                # Text content
                text = self._read_until("<").strip()
                if text:
                    parent.text_content = parent.text_content + text


cpdef tuple parse_aui(str content):
    """
    Parse AUI markup content.
    
    Args:
        content: AUI markup string
        
    Returns:
        Tuple of (root_node, errors)
    """
    cdef AUIParser parser = AUIParser(content)
    cdef AUINode root = parser.parse()
    return (root, parser.errors)


cpdef tuple parse_aui_file(str path):
    """
    Parse an AUI file.
    
    Args:
        path: Path to .aui file
        
    Returns:
        Tuple of (root_node, errors)
    """
    cdef str content
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return parse_aui(content)
