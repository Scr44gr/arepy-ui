# ScrollView

Container with vertical scrolling and content clipping.

## Usage

```python
from arepy_ui import ScrollView, Style, Unit

scroll = ScrollView(
    style=Style(width=Unit.px(300), height=Unit.px(400)),
    children=[
        # Content taller than the container
        item1,
        item2,
        item3,
        # ...
    ],
)
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `children` | `list[Node]` | `[]` | Content nodes |
| `style` | `Style` | `None` | Container styling |

## Properties

```python
scroll = ScrollView(...)

# Get current scroll position
y = scroll.scroll_y

# Set scroll position
scroll.scroll_y = 100

# Scroll to top
scroll.scroll_y = 0
```

## Scrolling

Scroll using the mouse wheel when hovering over the ScrollView. The scroll amount is based on wheel delta.

## Examples

### Item List

```python
def create_item_list(items):
    return ScrollView(
        style=Style(
            width=Unit.px(250),
            height=Unit.px(400),
            background_color=Color(40, 40, 40),
        ),
        children=[
            Node(
                style=Style(padding=Spacing.all(10)),
                children=[Text(item.name) for item in items],
            )
        ],
    )
```

### Chat Log

```python
chat_scroll = ScrollView(
    style=Style(
        width=Unit.percent(100),
        height=Unit.px(300),
        background_color=Color(20, 20, 20),
    ),
    children=[
        Node(
            style=Style(flex_direction=FlexDirection.COLUMN, gap=5, padding=Spacing.all(10)),
            children=chat_messages,
        )
    ],
)

# Scroll to bottom when new message arrives
def add_message(msg):
    chat_messages.append(Text(msg))
    chat_scroll.scroll_y = 999999  # Scroll to bottom
```

### Inventory Grid

```python
ScrollView(
    style=Style(width=Unit.px(400), height=Unit.px(300)),
    children=[
        Node(
            style=Style(
                flex_direction=FlexDirection.ROW,
                flex_wrap=True,
                gap=5,
            ),
            children=[create_slot(i) for i in range(50)],
        )
    ],
)
```
