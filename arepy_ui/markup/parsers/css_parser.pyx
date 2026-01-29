# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
"""
Cython-optimized CSS-like parser for ACSS stylesheets.

This is a performance-optimized version of css_parser.py.
Falls back to pure Python if not compiled.
"""

import re
from typing import Any, Dict, List

# Compiled regex patterns
cdef object _VAR_PATTERN = re.compile(r"var\(--([a-zA-Z0-9_-]+)\)")
cdef object _HEX_COLOR_PATTERN = re.compile(r"^#([0-9a-fA-F]{3,8})$")


cdef class StyleRule:
    """A CSS rule with selector and properties."""
    
    cdef public str selector
    cdef public dict properties
    cdef public int specificity
    
    def __init__(self, str selector, dict properties):
        self.selector = selector
        self.properties = properties
        self.specificity = self._calculate_specificity(selector)
    
    cdef int _calculate_specificity(self, str selector):
        """Calculate CSS specificity score."""
        cdef int score = 0
        if selector.startswith("#"):
            score = 100
        elif selector.startswith("."):
            score = 10
        else:
            score = 1
        if ":" in selector:
            score += 1
        return score
    
    def __repr__(self):
        return f"StyleRule({self.selector!r}, {len(self.properties)} props)"


cdef class StyleSheet:
    """Parsed stylesheet with variables and rules."""
    
    cdef public dict variables
    cdef public list rules
    cdef dict _cache
    
    def __init__(self):
        self.variables = {}
        self.rules = []
        self._cache = {}
    
    cpdef dict resolve_class(self, str class_name):
        """Get resolved properties for a class selector."""
        if class_name in self._cache:
            return self._cache[class_name]
        
        cdef dict result = {}
        cdef StyleRule rule
        
        for rule in self.rules:
            if rule.selector == "." + class_name or rule.selector == class_name:
                result.update(rule.properties)
        
        result = self._resolve_variables(result)
        self._cache[class_name] = result
        return result
    
    cpdef dict resolve_classes(self, list class_names):
        """Get merged properties for multiple class selectors."""
        cdef dict result = {}
        cdef str name
        for name in class_names:
            result.update(self.resolve_class(name))
        return result
    
    cpdef dict resolve_element(self, str element_name):
        """Get properties for an element selector."""
        cdef dict result = {}
        cdef StyleRule rule
        
        for rule in self.rules:
            if rule.selector == element_name:
                result.update(rule.properties)
        
        return self._resolve_variables(result)
    
    cpdef dict resolve_id(self, str id_name):
        """Get properties for an ID selector."""
        cdef str cache_key = "#" + id_name
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        cdef dict result = {}
        cdef StyleRule rule
        
        for rule in self.rules:
            if rule.selector == "#" + id_name or rule.selector == id_name:
                result.update(rule.properties)
        
        result = self._resolve_variables(result)
        self._cache[cache_key] = result
        return result

    cpdef dict resolve_class_pseudo(self, str class_name, str pseudo):
        """Get resolved properties for a class selector with pseudo-state.
        
        Args:
            class_name: The class name (without dot)
            pseudo: The pseudo-selector (e.g., 'hover', 'active')
            
        Returns:
            Properties for .class_name:pseudo
        """
        cdef str cache_key = "." + class_name + ":" + pseudo
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        cdef dict result = {}
        cdef StyleRule rule
        cdef str target = "." + class_name + ":" + pseudo
        
        for rule in self.rules:
            if rule.selector == target:
                result.update(rule.properties)
        
        result = self._resolve_variables(result)
        self._cache[cache_key] = result
        return result

    cpdef dict resolve_id_pseudo(self, str id_name, str pseudo):
        """Get resolved properties for an ID selector with pseudo-state.
        
        Args:
            id_name: The ID name (without hash)
            pseudo: The pseudo-selector (e.g., 'hover', 'active')
            
        Returns:
            Properties for #id_name:pseudo
        """
        cdef str cache_key = "#" + id_name + ":" + pseudo
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        cdef dict result = {}
        cdef StyleRule rule
        cdef str target = "#" + id_name + ":" + pseudo
        
        for rule in self.rules:
            if rule.selector == target:
                result.update(rule.properties)
        
        result = self._resolve_variables(result)
        self._cache[cache_key] = result
        return result

    cpdef dict resolve_element_pseudo(self, str element_name, str pseudo):
        """Get resolved properties for an element selector with pseudo-state.
        
        Args:
            element_name: The element/tag name
            pseudo: The pseudo-selector (e.g., 'hover', 'active')
            
        Returns:
            Properties for element_name:pseudo
        """
        cdef str cache_key = element_name + ":" + pseudo
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        cdef dict result = {}
        cdef StyleRule rule
        cdef str target = element_name + ":" + pseudo
        
        for rule in self.rules:
            if rule.selector == target:
                result.update(rule.properties)
        
        result = self._resolve_variables(result)
        self._cache[cache_key] = result
        return result
    
    cdef dict _resolve_variables(self, dict props):
        """Replace var(--name) references with actual values."""
        cdef dict result = {}
        cdef str key, var_name
        cdef object value, match
        
        for key, value in props.items():
            if isinstance(value, str) and "var(" in value:
                match = _VAR_PATTERN.search(value)
                if match:
                    var_name = match.group(1)
                    if var_name in self.variables:
                        value = _VAR_PATTERN.sub(self.variables[var_name], value)
            result[key] = value
        
        return result


cdef dict _parse_variables(str content):
    """Parse CSS variables from :root block."""
    cdef dict variables = {}
    cdef list declarations = content.split(";")
    cdef str decl, name, value
    cdef list parts
    
    for decl in declarations:
        decl = decl.strip()
        if decl.startswith("--"):
            parts = decl.split(":", 1)
            if len(parts) == 2:
                name = parts[0].strip()[2:]
                value = parts[1].strip()
                variables[name] = value
    
    return variables


cdef object _parse_value(str value):
    """Parse a CSS value into appropriate Python type."""
    cdef str v = value.strip()
    
    # Remove quotes
    if (v.startswith('"') and v.endswith('"')) or (
        v.startswith("'") and v.endswith("'")
    ):
        return v[1:-1]
    
    # Percentage
    if v.endswith("%"):
        try:
            return ("percent", float(v[:-1]))
        except ValueError:
            return v
    
    # Pixels
    if v.endswith("px"):
        try:
            return ("px", float(v[:-2]))
        except ValueError:
            return v
    
    # Number
    try:
        if "." in v:
            return float(v)
        return int(v)
    except ValueError:
        pass
    
    # Hex color
    if _HEX_COLOR_PATTERN.match(v):
        return ("color", v)
    
    # Boolean keywords
    if v == "true" or v == "True":
        return True
    if v == "false" or v == "False":
        return False
    if v == "none" or v == "None" or v == "null":
        return None
    if v == "auto":
        return ("auto",)
    
    return v


cdef dict _parse_properties(str content):
    """Parse CSS properties from a rule block."""
    cdef dict props = {}
    cdef list declarations = content.split(";")
    cdef str decl, key, value_str
    cdef list parts
    
    for decl in declarations:
        decl = decl.strip()
        if ":" in decl:
            parts = decl.split(":", 1)
            if len(parts) == 2:
                key = parts[0].strip()
                value_str = parts[1].strip()
                props[key] = _parse_value(value_str)
    
    return props


cpdef StyleSheet parse_acss(str content):
    """
    Parse ACSS content into a StyleSheet.
    
    Args:
        content: ACSS stylesheet string
        
    Returns:
        Parsed StyleSheet object
    """
    cdef StyleSheet sheet = StyleSheet()
    cdef str clean, selector, props_str
    cdef int pos, length, selector_start, brace_count, props_start
    cdef dict properties
    cdef object root_match
    
    # Remove comments
    clean = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
    clean = re.sub(r"//.*$", "", clean, flags=re.MULTILINE)
    
    # Parse :root variables
    root_match = re.search(r":root\s*\{([^}]+)\}", clean)
    if root_match:
        sheet.variables = _parse_variables(root_match.group(1))
        clean = clean.replace(root_match.group(0), "")
    
    # Parse rules
    pos = 0
    length = len(clean)
    
    while pos < length:
        # Skip whitespace
        while pos < length and clean[pos] in " \t\n\r":
            pos += 1
        
        if pos >= length:
            break
        
        # Find selector
        selector_start = pos
        while pos < length and clean[pos] != "{":
            pos += 1
        
        if pos >= length:
            break
        
        selector = clean[selector_start:pos].strip()
        if not selector:
            pos += 1
            continue
        
        # Find matching }
        pos += 1
        brace_count = 1
        props_start = pos
        
        while pos < length and brace_count > 0:
            if clean[pos] == "{":
                brace_count += 1
            elif clean[pos] == "}":
                brace_count -= 1
            pos += 1
        
        props_str = clean[props_start:pos - 1]
        properties = _parse_properties(props_str)
        
        if properties:
            sheet.rules.append(StyleRule(selector, properties))
    
    return sheet


cpdef StyleSheet parse_acss_file(str path):
    """
    Parse an ACSS file.
    
    Args:
        path: Path to .acss file
        
    Returns:
        Parsed StyleSheet object
    """
    cdef str content
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return parse_acss(content)
