# Styling Reference

CSS-in-Python styling system for arepy-ui.

<div class="grid cards" markdown>

-   :material-ruler:{ .lg .middle } **Style Properties**

    ---

    All available properties for the Style class.

    [:octicons-arrow-right-24: Properties](properties.md)

-   :material-resize:{ .lg .middle } **Units**

    ---

    Pixels, percentages, and auto sizing.

    [:octicons-arrow-right-24: Units](units.md)

-   :material-arrow-expand:{ .lg .middle } **Spacing**

    ---

    Padding and margin with the Spacing class.

    [:octicons-arrow-right-24: Spacing](spacing.md)

-   :material-view-grid:{ .lg .middle } **Flexbox**

    ---

    Layout with flex direction, alignment, and gap.

    [:octicons-arrow-right-24: Flexbox](flexbox.md)

-   :material-pin:{ .lg .middle } **Positioning**

    ---

    Absolute and relative positioning.

    [:octicons-arrow-right-24: Positioning](positioning.md)

</div>

## Quick Reference

### Creating Styles

```python
from arepy_ui import Style, Color, Unit, Spacing, FlexDirection, JustifyContent, AlignItems

# Full style example
style = Style(
    width=Unit.percent(100),
    height=Unit.px(60),
    flex_direction=FlexDirection.ROW,
    justify_content=JustifyContent.SPACE_BETWEEN,
    align_items=AlignItems.CENTER,
    padding=Spacing.horizontal(20),
    background_color=Color(30, 30, 40),
    border_radius=8.0,
)
```

### Size Units

| Unit | Example | Description |
|------|---------|-------------|
| `Unit.px(n)` | `Unit.px(200)` | Fixed pixels |
| `Unit.percent(n)` | `Unit.percent(50)` | Percentage of parent |
| `Unit.auto()` | `Unit.auto()` | Auto size |

### Flex Direction

| Value | Description |
|-------|-------------|
| `FlexDirection.ROW` | Horizontal (left to right) |
| `FlexDirection.COLUMN` | Vertical (top to bottom) |
| `FlexDirection.ROW_REVERSE` | Right to left |
| `FlexDirection.COLUMN_REVERSE` | Bottom to top |

### Justify Content (Main Axis)

| Value | Description |
|-------|-------------|
| `JustifyContent.FLEX_START` | Start of container |
| `JustifyContent.FLEX_END` | End of container |
| `JustifyContent.CENTER` | Center |
| `JustifyContent.SPACE_BETWEEN` | Even spacing, no edge gap |
| `JustifyContent.SPACE_AROUND` | Even spacing with edge gaps |
| `JustifyContent.SPACE_EVENLY` | Equal space everywhere |

### Align Items (Cross Axis)

| Value | Description |
|-------|-------------|
| `AlignItems.FLEX_START` | Top/Left |
| `AlignItems.FLEX_END` | Bottom/Right |
| `AlignItems.CENTER` | Center |
| `AlignItems.STRETCH` | Fill container |

### Spacing Helpers

```python
Spacing.all(16)           # All sides
Spacing.horizontal(20)    # Left + right
Spacing.vertical(10)      # Top + bottom
Spacing.xy(h=20, v=10)    # Shorthand
Spacing(                  # Individual
    top=Unit.px(10),
    right=Unit.px(20),
    bottom=Unit.px(10),
    left=Unit.px(20),
)
```
