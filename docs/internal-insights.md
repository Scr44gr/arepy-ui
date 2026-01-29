# Internal Architecture Insights

> This document provides internal insights about arepy-ui's architecture, design decisions, and implementation details. Use this for README inspiration and contributor onboarding.

---

## Core Philosophy

### "Everything is a Node"

arepy-ui follows a unified component model where every UI element inherits from `Node`. This provides:

- **Consistent API**: All components share the same base properties (`style`, `children`, `id`)
- **Composability**: Any component can contain any other component
- **Predictable layout**: Single flexbox engine handles all positioning

```python
# Button is a Node, Text is a Node, containers are Nodes
button = Button("Click", children=[Icon("save")])  # Nest anything
```

### Flexbox-First Layout

Instead of inventing a new layout system, arepy-ui implements **CSS Flexbox** semantics:

- Familiar to web developers
- Well-documented behavior
- Powerful responsive layouts
- Battle-tested algorithm (from `stretch` Rust crate concepts)

---

## Architecture Highlights

### UIManager - The Central Controller

```
┌──────────────────────────────────────────────┐
│                  UIManager                    │
├──────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐            │
│  │   Runtime   │  │   Layout    │            │
│  │  (renderer, │  │   Engine    │            │
│  │   input)    │  │  (flexbox)  │            │
│  └─────────────┘  └─────────────┘            │
│                                              │
│  ┌─────────────────────────────────────────┐ │
│  │              Node Tree                   │ │
│  │  ┌───────┐                              │ │
│  │  │ Root  │                              │ │
│  │  └───┬───┘                              │ │
│  │      ├── Child 1                        │ │
│  │      ├── Child 2                        │ │
│  │      └── ...                            │ │
│  └─────────────────────────────────────────┘ │
└──────────────────────────────────────────────┘
```

**Responsibilities:**
- Owns the node tree
- Coordinates layout computation
- Routes input events to nodes
- Manages render order and z-index

### Computed Layout System

Layout happens in two phases:

1. **Style Phase**: User-defined styles are collected
2. **Compute Phase**: Flexbox algorithm calculates `computed_x`, `computed_y`, `computed_width`, `computed_height`

```python
node.style.width = Unit.percent(50)  # User intent
# After layout:
node.computed_width  # Actual pixels: 400.0
```

### Event Propagation

```
Mouse Event → UIManager → Hit Testing → Node.handle_event()
                              ↓
                    Bubble up to parent (optional)
```

Events propagate **top-down** for hit testing, then **bottom-up** for handling (like DOM events).

---

## Markup System Architecture

### Parser Pipeline

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   .aui file  │────▶│  AUI Parser  │────▶│   AST Tree   │
└──────────────┘     └──────────────┘     └──────────────┘
                                                 │
┌──────────────┐     ┌──────────────┐            ▼
│  .acss file  │────▶│  CSS Parser  │────▶┌──────────────┐
└──────────────┘     └──────────────┘     │   Builder    │
                                          │  (combines)  │
                                          └──────┬───────┘
                                                 ▼
                                          ┌──────────────┐
                                          │  Node Tree   │
                                          └──────────────┘
```

### Cython Acceleration

Critical path functions are implemented in Cython:

```
arepy_ui/markup/
├── parsers/
│   ├── _aui_parser.pyx    # Cython AUI parser
│   ├── _css_parser.pyx    # Cython CSS parser
│   └── *.py               # Pure Python fallbacks
```

**Fallback Strategy:**
```python
try:
    from ._aui_parser import parse_aui  # Try Cython
except ImportError:
    from .aui_parser import parse_aui   # Fallback to Python
```

### Global Style Registry (Singleton)

```python
GlobalStyleRegistry
├── _stylesheets[]        # List of loaded stylesheets
├── _variables            # ThemeVariables instance
│   ├── _base{}           # :root variables
│   ├── _variants{}       # :root.light, :root.dark
│   └── _active_variant   # Currently active theme
└── _cache{}              # Resolved style cache
```

**Variable Resolution:**
```
var(--accent) → Check active variant → Fallback to base → Return value
```

---

## Component Design Patterns

### Stateful Components

Components like `TextInput`, `Slider`, `ColorPicker` maintain internal state:

```python
class Slider(Node):
    def __init__(self, ...):
        self._value = value
        self._dragging = False
    
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, v):
        self._value = clamp(v, self.min_value, self.max_value)
        self._notify_change()
```

### Streaming Textures (Video, ColorPicker)

For dynamic textures, components use PBO streaming:

```python
# Create streaming texture once
self._texture_id = renderer.create_streaming_texture(width, height, 4)

# Update pixels each frame (double-buffered)
renderer.update_streaming_texture(self._texture_id, pixel_bytes)
```

### Drag State Machine

```
IDLE → (mouse down in handle) → DRAGGING → (mouse up) → IDLE
         │                           │
         └── Update value ◄──────────┘
```

---

## Performance Insights

### Layout Caching

Layout is only recomputed when:
- Node tree structure changes (`add_child`, `remove_child`)
- Style properties change
- Window resize

```python
# Internal dirty flag
if self._layout_dirty:
    self._compute_layout()
    self._layout_dirty = False
```

### Text Rendering Optimization

Text is pre-rendered to texture:

```
Text "Hello" → Render to texture → Cache → Blit each frame
```

Font atlas caching for repeated characters.

### Event Throttling

Input events are batched per frame:
- Mouse position sampled once per `update()`
- Click events debounced
- Scroll events coalesced

---

## Extension Points

### Custom Components

Extend `Node` to create custom components:

```python
class MyWidget(Node):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def update(self, dt: float):
        super().update(dt)
        # Custom logic
    
    def render(self):
        super().render()
        # Custom rendering
```

### Custom Markup Tags

Register new tags in the builder:

```python
TAG_HANDLERS["my-widget"] = lambda attrs, children: MyWidget(**attrs)
```

### Theming

Create design tokens in globals.acss:

```css
:root {
    --brand-primary: #6c5ce7;
    --brand-secondary: #a29bfe;
}

:root.corporate {
    --brand-primary: #0066cc;
    --brand-secondary: #3399ff;
}
```

---

## Testing Architecture

### Mock Runtime

Tests use `MockRuntime` to simulate engine without graphics:

```python
mock_runtime = MockRuntime(width=800, height=600)
ui_manager = UIManager(runtime=mock_runtime)
```

### Property-Based Testing

Critical algorithms use hypothesis:

```python
@given(width=st.integers(1, 1000), children=st.integers(0, 20))
def test_layout_never_overflows(width, children):
    ...
```

### Coverage Targets

| Module | Target | Current |
|--------|--------|---------|
| `core/` | 90% | 95% |
| `components/` | 85% | 88% |
| `markup/` | 80% | 82% |
| Overall | 80% | 81% |

---

## Design Decisions

### Why Flexbox?

- **Familiar**: Most developers know CSS flexbox
- **Powerful**: Handles 95% of UI layouts
- **Responsive**: Works at any resolution
- **Tested**: Algorithm is well-understood

### Why Not Immediate Mode?

Retained mode (node tree) allows:
- Automatic layout
- State management
- Animation system
- Declarative markup

### Why Cython?

- **10-50x** faster parsing than pure Python
- **Zero-copy** integration with C libraries
- **Optional**: Pure Python fallback always works

### Why Streaming Textures?

For Video and ColorPicker:
- PBO uploads don't block CPU
- Double buffering prevents tearing
- GPU-accelerated scaling

---

## Future Directions

- [ ] **Web export**: Compile to WASM for browser
- [ ] **Visual editor**: Drag-and-drop UI builder
- [ ] **Hot reload**: Live preview during development
- [ ] **Accessibility**: Screen reader support
- [ ] **Localization**: Built-in i18n system
