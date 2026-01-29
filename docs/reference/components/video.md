# Video

!!! warning "Experimental"
    This component is not stable and may change in future versions.

Video player component for displaying video files.

## Requirements

Video playback requires the `full` extras:

```bash
pip install arepy-ui[full]
```

Or with uv:

```bash
uv add arepy-ui[full]
```

This installs `av` (PyAV) and `numpy` for video decoding.

## Usage

```python
from arepy_ui.components.video import Video, VideoState, ControlsConfig
from arepy_ui import Unit

# Basic video
video = Video(
    source="assets/intro.mp4",
    width=Unit.px(640),
    height=Unit.px(360),
)

# Autoplay with loop
video = Video(
    source="assets/background.mp4",
    width=Unit.percent(100),
    height=Unit.percent(100),
    autoplay=True,
    loop=True,
)

# With custom controls
video = Video(
    source="assets/cutscene.mp4",
    controls=ControlsConfig(
        show_play_button=True,
        show_progress_bar=True,
        show_time=True,
    ),
)
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `source` | `str` | required | Path to video file |
| `width` | `Unit` | `Unit.px(320)` | Video width |
| `height` | `Unit` | `Unit.px(240)` | Video height |
| `autoplay` | `bool` | `False` | Start playing automatically |
| `loop` | `bool` | `False` | Loop when finished |
| `muted` | `bool` | `False` | Mute audio |
| `controls` | `ControlsConfig` | `None` | Controls configuration |
| `style` | `Style` | `None` | Additional styling |

## ControlsConfig

```python
ControlsConfig(
    show_play_button=True,   # Show play/pause button
    show_progress_bar=True,  # Show seek bar
    show_time=True,          # Show current/total time
    show_volume=True,        # Show volume slider
)
```

## VideoState

```python
from arepy_ui.components.video import VideoState

VideoState.STOPPED   # Not playing
VideoState.PLAYING   # Currently playing
VideoState.PAUSED    # Paused
VideoState.ENDED     # Finished playing
```

## Properties & Methods

```python
video = Video(source="video.mp4")

# Playback control
video.play()
video.pause()
video.stop()
video.seek(10.0)  # Seek to 10 seconds

# State
state = video.state  # VideoState
current_time = video.current_time  # Seconds
duration = video.duration  # Total seconds

# Audio
video.volume = 0.5  # 0.0 to 1.0
video.muted = True
```

## Examples

### Background Video

```python
Node(
    style=Style(width=Unit.percent(100), height=Unit.percent(100)),
    children=[
        Video(
            source="assets/menu_bg.mp4",
            width=Unit.percent(100),
            height=Unit.percent(100),
            autoplay=True,
            loop=True,
            muted=True,
        ),
        # UI on top of video
        Node(
            style=Style(
                position=PositionType.ABSOLUTE,
                top=Unit.px(0),
                left=Unit.px(0),
            ),
            children=[...],
        ),
    ],
)
```

### Cutscene Player

```python
cutscene = Video(
    source="assets/cutscenes/intro.mp4",
    width=Unit.percent(100),
    height=Unit.percent(100),
    on_ended=lambda: transition_to_gameplay(),
)

# Skip button
Button(
    "Skip",
    on_click=lambda: (cutscene.stop(), transition_to_gameplay()),
    style=Style(
        position=PositionType.ABSOLUTE,
        bottom=Unit.px(20),
        right=Unit.px(20),
    ),
)
```

### Video with Controls

```python
Video(
    source="assets/tutorial.mp4",
    width=Unit.px(800),
    height=Unit.px(450),
    controls=ControlsConfig(
        show_play_button=True,
        show_progress_bar=True,
        show_time=True,
        show_volume=True,
    ),
)
```

## Supported Formats

Depends on PyAV/FFmpeg. Common formats:

- MP4 (H.264)
- WebM (VP8/VP9)
- AVI
- MOV

!!! note "Performance"
    Video decoding can be CPU-intensive. For best performance, use hardware-accelerated codecs (H.264) and reasonable resolutions.
