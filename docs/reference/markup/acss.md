# ACSS Styling

CSS-like styling for AUI markup files.

## Overview

ACSS (Arepy CSS) is a CSS-like stylesheet format for styling AUI elements.

## Basic Syntax

```css
/* menu.acss */

.screen {
    width: 100%;
    height: 100%;
    background: #1a1a2e;
    justify-content: center;
    align-items: center;
}

.title {
    font-size: 48px;
    color: white;
}

.btn {
    width: 200px;
    height: 50px;
    background: #4a4a6a;
    border-radius: 8px;
}
```

## Selectors

### Class Selector

```css
.button {
    background: #333;
}

.primary {
    background: #0066cc;
}
```

### Multiple Classes

```css
.btn.primary {
    background: #0066cc;
}

.btn.danger {
    background: #cc0000;
}
```

## Properties

### Size

```css
.container {
    width: 100%;
    height: 100%;
    min-width: 200px;
    max-width: 800px;
    min-height: 100px;
    max-height: 600px;
}
```

### Layout (Flexbox)

```css
.row {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
}

.column {
    flex-direction: column;
    justify-content: flex-start;
    align-items: stretch;
    gap: 8px;
}
```

**justify-content values:**
- `flex-start`, `flex-end`, `center`
- `space-between`, `space-around`, `space-evenly`

**align-items values:**
- `flex-start`, `flex-end`, `center`, `stretch`

### Spacing

```css
.card {
    padding: 20px;                    /* All sides */
    padding: 10px 20px;               /* Vertical, Horizontal */
    padding: 10px 20px 15px 20px;     /* Top, Right, Bottom, Left */
    
    margin: 16px;
    margin-top: 10px;
    margin-bottom: 10px;
}
```

### Background

```css
.panel {
    background: #2a2a3e;
    background-color: rgba(30, 30, 40, 0.9);
}
```

### Border

```css
.card {
    border-width: 2px;
    border-color: #4a4a6a;
    border-radius: 12px;
}
```

### Text

```css
.heading {
    font-size: 32px;
    color: #ffffff;
    /* font-family: "Inter"; */
}

.subtitle {
    font-size: 14px;
    color: #888899;
}
```

### Visibility

```css
.hidden {
    visible: false;
}

.transparent {
    opacity: 0.5;
}
```

### Interactive States (Pseudo-selectors)

Style hover and active states using CSS-like pseudo-selectors:

```css
.btn {
    background: #007acc;
    color: #ffffff;
}

.btn:hover {
    background: #3296dc;
    color: #000000;
    border-color: #ffffff;
}

.btn:active {
    background: #005096;
}

.checkbox:hover {
    background: #32e682;
}

.checkbox:active {
    background: #009646;
}

.select:hover {
    background: #3c3e46;
}

.select:active {
    background: #1e2028;
}
```

**Supported pseudo-selectors:**

| Pseudo | Applies when |
|--------|-------------|
| `:hover` | Mouse is over the element |
| `:active` | Element is being pressed/clicked |

### Positioning

```css
.overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 100;
}
```

## Variables

Define and use CSS variables:

```css
:root {
    --primary: #6450c8;
    --bg-dark: #1a1a2e;
    --text: #ffffff;
    --gap: 16px;
}

.btn {
    background: var(--primary);
    color: var(--text);
}

.container {
    background: var(--bg-dark);
    gap: var(--gap);
}
```

## Color Formats

```css
.colors {
    color: white;                 /* Named */
    color: #ff0000;               /* Hex */
    color: #f00;                  /* Short hex */
    color: rgb(255, 0, 0);        /* RGB */
    color: rgba(255, 0, 0, 0.5);  /* RGBA */
}
```

## Units

```css
.units {
    width: 200px;      /* Pixels */
    height: 100%;      /* Percentage */
    gap: 16;           /* Unitless (pixels) */
}
```

## Loading ACSS

ACSS files are auto-loaded with matching AUI files:

```
menu.aui   ← Structure
menu.acss  ← Styles (auto-loaded)
```

Or load explicitly:

```python
from arepy_ui.markup import load_aui

# Auto-loads menu.acss
result = load_aui("menu.aui")

# Or point to an explicit stylesheet file
result = load_aui("menu.aui", stylesheet="custom-styles.acss")
```

## Complete Example

```css
/* game-menu.acss */

:root {
    --bg: #0f0f19;
    --panel: #1a1a2e;
    --primary: #6450c8;
    --primary-hover: #7860d8;
    --text: #ffffff;
    --text-muted: #888899;
}

.screen {
    width: 100%;
    height: 100%;
    background: var(--bg);
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: 32px;
}

.title {
    font-size: 64px;
    color: var(--text);
}

.subtitle {
    font-size: 18px;
    color: var(--text-muted);
    margin-top: -20px;
}

.menu {
    flex-direction: column;
    gap: 12px;
    margin-top: 40px;
}

.btn {
    width: 240px;
    height: 56px;
    background: var(--primary);
    border-radius: 8px;
    justify-content: center;
    align-items: center;
}

.btn:hover {
    background: var(--primary-hover);
}

.btn-danger {
    background: #c83c3c;
}

.version {
    font-size: 12px;
    color: var(--text-muted);
    position: absolute;
    bottom: 20px;
    right: 20px;
}
```

## See Also

- [AUI Syntax](aui.md) - Markup structure
- [Global Styles](globals.md) - Shared variables and themes
- [Style Properties](../styling/properties.md) - Python equivalent
