# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
# pyright: reportMissingModuleSource=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportUnknownReturnType=false, reportGeneralTypeIssues=false
"""Cython-optimized CSS-like parser for ACSS stylesheets."""

from cpython.unicode cimport PyUnicode_READ_CHAR


ctypedef unsigned int Py_UCS4


cdef inline bint _is_ascii_whitespace(Py_UCS4 ch) noexcept:
    return ch == 32 or ch == 9 or ch == 10 or ch == 13


cdef inline bint _is_hex_digit(Py_UCS4 ch) noexcept:
    return (48 <= ch <= 57) or (65 <= ch <= 70) or (97 <= ch <= 102)


cdef inline str _strip_ascii(str value):
    return value.strip(" \t\n\r")


cdef bint _is_hex_color(str value):
    cdef Py_ssize_t length = len(value)
    cdef Py_ssize_t index

    if length < 4 or length > 9:
        return False
    if PyUnicode_READ_CHAR(value, 0) != 35:
        return False

    for index in range(1, length):
        if not _is_hex_digit(PyUnicode_READ_CHAR(value, index)):
            return False

    return True


cdef str _strip_comments(str content):
    cdef list parts = []
    cdef Py_ssize_t start = 0
    cdef Py_ssize_t pos = 0
    cdef Py_ssize_t length = len(content)
    cdef Py_UCS4 ch
    cdef Py_UCS4 next_ch

    while pos < length:
        ch = PyUnicode_READ_CHAR(content, pos)
        if ch == 47 and pos + 1 < length:
            next_ch = PyUnicode_READ_CHAR(content, pos + 1)
            if next_ch == 42:
                if start < pos:
                    parts.append(content[start:pos])
                pos += 2
                while pos + 1 < length:
                    if (
                        PyUnicode_READ_CHAR(content, pos) == 42
                        and PyUnicode_READ_CHAR(content, pos + 1) == 47
                    ):
                        pos += 2
                        break
                    pos += 1
                else:
                    pos = length
                start = pos
                continue
            if next_ch == 47:
                if start < pos:
                    parts.append(content[start:pos])
                pos += 2
                while pos < length and PyUnicode_READ_CHAR(content, pos) != 10:
                    pos += 1
                start = pos
                continue
        pos += 1

    if start < length:
        parts.append(content[start:length])

    if not parts:
        return ""
    return "".join(parts)


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
        cdef int score = 0

        if selector and PyUnicode_READ_CHAR(selector, 0) == 35:
            score = 100
        elif selector and PyUnicode_READ_CHAR(selector, 0) == 46:
            score = 10
        else:
            score = 1

        if selector.find(":") != -1:
            score += 1

        return score

    def __repr__(self):
        return f"StyleRule({self.selector!r}, {len(self.properties)} props)"


cdef class StyleSheet:
    """Parsed stylesheet with variables and rules."""

    cdef public dict variables
    cdef public list rules
    cdef dict _cache
    cdef dict _element_rules
    cdef dict _class_rules
    cdef dict _id_rules
    cdef dict _element_pseudo_rules
    cdef dict _class_pseudo_rules
    cdef dict _id_pseudo_rules

    def __init__(self):
        self.variables = {}
        self.rules = []
        self._cache = {}
        self._element_rules = {}
        self._class_rules = {}
        self._id_rules = {}
        self._element_pseudo_rules = {}
        self._class_pseudo_rules = {}
        self._id_pseudo_rules = {}

    cpdef void add_rule(self, StyleRule rule):
        self.rules.append(rule)
        self._index_rule(rule)

    cdef void _index_rule(self, StyleRule rule):
        cdef str selector = rule.selector
        cdef str base_selector
        cdef str pseudo
        cdef dict target_props
        cdef Py_ssize_t pseudo_sep = selector.find(":")

        if not selector or selector == ":root":
            return

        if pseudo_sep != -1:
            base_selector = selector[:pseudo_sep]
            pseudo = selector[pseudo_sep + 1:]
            if base_selector and PyUnicode_READ_CHAR(base_selector, 0) == 35:
                target_props = self._id_pseudo_rules.setdefault(
                    (base_selector[1:], pseudo), {}
                )
            elif base_selector and PyUnicode_READ_CHAR(base_selector, 0) == 46:
                target_props = self._class_pseudo_rules.setdefault(
                    (base_selector[1:], pseudo), {}
                )
            else:
                target_props = self._element_pseudo_rules.setdefault(
                    (base_selector, pseudo), {}
                )
            target_props.update(rule.properties)
            return

        if PyUnicode_READ_CHAR(selector, 0) == 35:
            target_props = self._id_rules.setdefault(selector[1:], {})
        elif PyUnicode_READ_CHAR(selector, 0) == 46:
            target_props = self._class_rules.setdefault(selector[1:], {})
        else:
            target_props = self._element_rules.setdefault(selector, {})

        target_props.update(rule.properties)

    cpdef dict raw_resolve_class(self, str class_name):
        return dict(self._class_rules.get(class_name, {}))

    cpdef dict raw_resolve_classes(self, list class_names):
        cdef dict result = {}
        cdef str name

        for name in class_names:
            result.update(self._class_rules.get(name, {}))
        return result

    cpdef dict raw_resolve_element(self, str element_name):
        return dict(self._element_rules.get(element_name, {}))

    cpdef dict raw_resolve_id(self, str id_name):
        return dict(self._id_rules.get(id_name, {}))

    cpdef dict raw_resolve_class_pseudo(self, str class_name, str pseudo):
        return dict(self._class_pseudo_rules.get((class_name, pseudo), {}))

    cpdef dict raw_resolve_id_pseudo(self, str id_name, str pseudo):
        return dict(self._id_pseudo_rules.get((id_name, pseudo), {}))

    cpdef dict raw_resolve_element_pseudo(self, str element_name, str pseudo):
        return dict(self._element_pseudo_rules.get((element_name, pseudo), {}))

    cpdef dict resolve_class(self, str class_name):
        cdef dict result

        if class_name in self._cache:
            return self._cache[class_name]

        result = self.raw_resolve_class(class_name)
        result = self._resolve_variables(result)
        self._cache[class_name] = result
        return result

    cpdef dict resolve_classes(self, list class_names):
        return self._resolve_variables(self.raw_resolve_classes(class_names))

    cpdef dict resolve_element(self, str element_name):
        return self._resolve_variables(self.raw_resolve_element(element_name))

    cpdef dict resolve_id(self, str id_name):
        cdef str cache_key = "#" + id_name
        cdef dict result

        if cache_key in self._cache:
            return self._cache[cache_key]

        result = self.raw_resolve_id(id_name)
        result = self._resolve_variables(result)
        self._cache[cache_key] = result
        return result

    cpdef dict resolve_class_pseudo(self, str class_name, str pseudo):
        cdef str cache_key = "." + class_name + ":" + pseudo
        cdef dict result

        if cache_key in self._cache:
            return self._cache[cache_key]

        result = self.raw_resolve_class_pseudo(class_name, pseudo)
        result = self._resolve_variables(result)
        self._cache[cache_key] = result
        return result

    cpdef dict resolve_id_pseudo(self, str id_name, str pseudo):
        cdef str cache_key = "#" + id_name + ":" + pseudo
        cdef dict result

        if cache_key in self._cache:
            return self._cache[cache_key]

        result = self.raw_resolve_id_pseudo(id_name, pseudo)
        result = self._resolve_variables(result)
        self._cache[cache_key] = result
        return result

    cpdef dict resolve_element_pseudo(self, str element_name, str pseudo):
        cdef str cache_key = element_name + ":" + pseudo
        cdef dict result

        if cache_key in self._cache:
            return self._cache[cache_key]

        result = self.raw_resolve_element_pseudo(element_name, pseudo)
        result = self._resolve_variables(result)
        self._cache[cache_key] = result
        return result

    cdef dict _resolve_variables(self, dict props):
        cdef dict result = {}
        cdef str key
        cdef object value
        cdef str string_value
        cdef Py_ssize_t start
        cdef Py_ssize_t end
        cdef str var_name
        cdef object replacement

        for key, value in props.items():
            if isinstance(value, str):
                string_value = value
                start = string_value.find("var(--")
                while start != -1:
                    end = string_value.find(")", start + 6)
                    if end == -1:
                        break
                    var_name = string_value[start + 6:end]
                    replacement = self.variables.get(var_name)
                    if replacement is None:
                        break
                    string_value = (
                        string_value[:start]
                        + <str>replacement
                        + string_value[end + 1:]
                    )
                    start = string_value.find("var(--")
                value = string_value
            result[key] = value

        return result


cdef dict _parse_variables(str content):
    cdef dict variables = {}
    cdef Py_ssize_t pos = 0
    cdef Py_ssize_t length = len(content)
    cdef Py_ssize_t name_start
    cdef Py_ssize_t name_end
    cdef Py_ssize_t value_start
    cdef Py_ssize_t value_end
    cdef str name
    cdef str value

    while pos < length:
        while pos < length and (
            _is_ascii_whitespace(PyUnicode_READ_CHAR(content, pos))
            or PyUnicode_READ_CHAR(content, pos) == 59
        ):
            pos += 1

        if pos + 1 >= length:
            break
        if (
            PyUnicode_READ_CHAR(content, pos) != 45
            or PyUnicode_READ_CHAR(content, pos + 1) != 45
        ):
            while pos < length and PyUnicode_READ_CHAR(content, pos) != 59:
                pos += 1
            continue

        name_start = pos + 2
        pos = name_start
        while pos < length and PyUnicode_READ_CHAR(content, pos) != 58:
            pos += 1
        if pos >= length:
            break

        name_end = pos
        pos += 1
        while pos < length and _is_ascii_whitespace(PyUnicode_READ_CHAR(content, pos)):
            pos += 1
        value_start = pos
        while pos < length and PyUnicode_READ_CHAR(content, pos) != 59:
            pos += 1
        value_end = pos

        name = _strip_ascii(content[name_start:name_end])
        value = _strip_ascii(content[value_start:value_end])
        if name:
            variables[name] = value

        if pos < length and PyUnicode_READ_CHAR(content, pos) == 59:
            pos += 1

    return variables


cdef object _parse_value(str value):
    cdef str v = _strip_ascii(value)
    cdef Py_ssize_t v_length = len(v)

    if (v.startswith('"') and v.endswith('"')) or (
        v.startswith("'") and v.endswith("'")
    ):
        return v[1 : v_length - 1]

    if v.endswith("%"):
        try:
            return ("percent", float(v[: v_length - 1]))
        except ValueError:
            return v

    if v.endswith("px"):
        try:
            return ("px", float(v[: v_length - 2]))
        except ValueError:
            return v

    try:
        if "." in v:
            return float(v)
        return int(v)
    except ValueError:
        pass

    if _is_hex_color(v):
        return ("color", v)

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
    cdef dict props = {}
    cdef Py_ssize_t pos = 0
    cdef Py_ssize_t length = len(content)
    cdef Py_ssize_t key_start
    cdef Py_ssize_t key_end
    cdef Py_ssize_t value_start
    cdef Py_ssize_t value_end
    cdef int nested_depth = 0
    cdef Py_UCS4 ch
    cdef str key
    cdef str value_str

    while pos < length:
        while pos < length and (
            _is_ascii_whitespace(PyUnicode_READ_CHAR(content, pos))
            or PyUnicode_READ_CHAR(content, pos) == 59
        ):
            pos += 1

        if pos >= length:
            break

        key_start = pos
        while pos < length:
            ch = PyUnicode_READ_CHAR(content, pos)
            if ch == 58 or ch == 59:
                break
            pos += 1

        if pos >= length or PyUnicode_READ_CHAR(content, pos) != 58:
            while pos < length and PyUnicode_READ_CHAR(content, pos) != 59:
                pos += 1
            continue

        key_end = pos
        pos += 1
        while pos < length and _is_ascii_whitespace(PyUnicode_READ_CHAR(content, pos)):
            pos += 1
        value_start = pos
        nested_depth = 0

        while pos < length:
            ch = PyUnicode_READ_CHAR(content, pos)
            if ch == 40:
                nested_depth += 1
            elif ch == 41 and nested_depth > 0:
                nested_depth -= 1
            elif ch == 59 and nested_depth == 0:
                break
            pos += 1

        value_end = pos
        key = _strip_ascii(content[key_start:key_end])
        if key:
            value_str = _strip_ascii(content[value_start:value_end])
            props[key] = _parse_value(value_str)

        if pos < length and PyUnicode_READ_CHAR(content, pos) == 59:
            pos += 1

    return props


cpdef StyleSheet parse_acss(str content):
    cdef StyleSheet sheet = StyleSheet()
    cdef str clean
    cdef str selector
    cdef str props_str
    cdef Py_ssize_t pos = 0
    cdef Py_ssize_t length
    cdef Py_ssize_t selector_start
    cdef Py_ssize_t brace_count
    cdef Py_ssize_t props_start
    cdef Py_ssize_t props_end
    cdef dict properties
    cdef Py_UCS4 ch

    clean = _strip_comments(content)
    length = len(clean)

    while pos < length:
        while pos < length and _is_ascii_whitespace(PyUnicode_READ_CHAR(clean, pos)):
            pos += 1
        if pos >= length:
            break

        selector_start = pos
        while pos < length and PyUnicode_READ_CHAR(clean, pos) != 123:
            pos += 1
        if pos >= length:
            break

        selector = _strip_ascii(clean[selector_start:pos])
        if not selector:
            pos += 1
            continue

        pos += 1
        brace_count = 1
        props_start = pos
        while pos < length and brace_count > 0:
            ch = PyUnicode_READ_CHAR(clean, pos)
            if ch == 123:
                brace_count += 1
            elif ch == 125:
                brace_count -= 1
            pos += 1

        if brace_count == 0:
            props_end = pos - 1
            props_str = clean[props_start:props_end]
        else:
            props_str = clean[props_start:length]

        if selector == ":root":
            sheet.variables.update(_parse_variables(props_str))
            continue

        properties = _parse_properties(props_str)
        if properties:
            sheet.add_rule(StyleRule(selector, properties))

    return sheet


cpdef StyleSheet parse_acss_file(str path):
    cdef str content
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return parse_acss(content)
