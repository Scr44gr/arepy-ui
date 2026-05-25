"""UNSTABLE COMPONENT - API may change in future releases.
Requires optional dependencies: pip install arepy-ui[full]
"""

import os
import struct
import importlib
from dataclasses import dataclass, field
from typing import Any, Callable, Iterator, Optional, Union

from ..core.node import Node
from ..core.style import (
    Spacing,
    Style,
    merge_non_default_style_fields,
    merge_style_fields,
)
from ..core.types import (
    AlignItems,
    Color,
    CursorType,
    FlexDirection,
    JustifyContent,
    PositionType,
    Unit,
)
from ..logging import logger
from ..runtime import MOUSE_BUTTON_LEFT, get_runtime
from .button import Button
from .slider import Slider
from .text import Text

# Check if video dependencies are available
try:
    av: Optional[Any] = importlib.import_module("av")
    HAS_VIDEO_DEPS = True
except ImportError:
    HAS_VIDEO_DEPS = False
    av = None


def _get_av() -> Any:
    if av is None:
        raise RuntimeError("Video dependencies are not available. Install arepy-ui[full].")
    return av


class VideoState:
    """Video playback state."""

    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"


@dataclass
class ControlsConfig:
    """
    Configuration for video player controls.

    Usage:
        # With custom style
        controls = ControlsConfig(
            style=Style(
                background_color=Color(0, 0, 0, 200),
                height=Unit.px(50),
            ),
            accent_color=Color(255, 0, 0, 255),
            show_volume=False,
        )

        # With defaults
        controls = ControlsConfig()
    """

    # Visual style for controls bar
    style: Style = field(
        default_factory=lambda: Style(
            background_color=Color(10, 10, 14, 210),
            height=Unit.px(52),
        )
    )

    # Accent color for progress bar, highlights
    accent_color: Color = field(default_factory=lambda: Color(70, 130, 220, 255))

    # Foreground color for icons/text
    foreground_color: Color = field(default_factory=lambda: Color(255, 255, 255, 255))

    # Which controls to show
    show_play: bool = True
    show_progress: bool = True
    show_time: bool = True
    show_volume: bool = True

    # Auto-hide controls after inactivity
    auto_hide: bool = True
    hide_delay: float = 3.0


class Video(Node):
    """
    Video player component with customizable controls.

    Requires: pip install arepy-ui[full]

    Usage:
        # Basic usage
        video = Video(
            source="path/to/video.mp4",
            width=Unit.px(640),
            height=Unit.px(360),
            autoplay=True,
        )

        # With custom controls
        video = Video(
            source="video.mp4",
            controls=ControlsConfig(
                style=Style(
                    background_color=Color(0, 0, 0, 200),
                    height=Unit.px(50),
                ),
                accent_color=Color(255, 0, 0, 255),
                show_volume=False,
            ),
        )

        # Without controls
        video = Video(source="video.mp4", controls=None)

        # Manual control
        video.play()
        video.pause()
        video.seek(10.5)  # seconds
        video.volume = 0.8
    """

    def __init__(
        self,
        source: str,
        width: Unit = Unit.vw(100),
        height: Unit = Unit.px(360),
        autoplay: bool = False,
        loop: bool = True,
        muted: bool = False,
        volume: float = 1.0,
        controls: Optional[Union[ControlsConfig, bool]] = True,
        on_play: Optional[Callable[[], None]] = None,
        on_pause: Optional[Callable[[], None]] = None,
        on_ended: Optional[Callable[[], None]] = None,
        on_time_update: Optional[Callable[[float], None]] = None,
        style: Optional[Style] = None,
        **kwargs,
    ):
        # Initialize ALL attributes first (before any potential exceptions)
        self._video_container: Any = None
        self._video_stream: Any = None
        self._streaming_texture: Any = None
        self._frame_generator: Optional[Iterator[Any]] = None
        self._initialized = False
        self._video_width = 0
        self._video_height = 0
        self._video_fps = 30.0
        self._frame_time_acc = 0.0
        self._current_time = 0.0
        self._duration = 0.0
        self._state = VideoState.STOPPED
        self._audio_device = None
        self._audio_music = None
        self._has_audio = False
        self._audio_memory_data = None
        self._deps_available = HAS_VIDEO_DEPS
        self._post_seek_sync_remaining = 0.0
        self._post_seek_sync_duration = 0.25

        # Setup style
        default_style = Style(
            width=width,
            height=height,
            background_color=Color(0, 0, 0, 255),
            cursor=CursorType.POINTING_HAND,
        )

        merge_style_fields(default_style, style, ("width", "height"))
        if style and style.cursor:
            default_style.cursor = style.cursor
        if style and style.background_color:
            default_style.background_color = style.background_color

        super().__init__(style=default_style, **kwargs)

        self.source = source
        self.autoplay = autoplay
        self.loop = loop
        self.muted = muted
        self._volume = volume

        # Controls config - normalize to ControlsConfig or None
        if controls is True:
            self._controls_config = ControlsConfig()
        elif controls is False or controls is None:
            self._controls_config = None
        else:
            self._controls_config = controls

        # Callbacks
        self.on_play_callback = on_play
        self.on_pause_callback = on_pause
        self.on_ended = on_ended
        self.on_time_update = on_time_update

        # Controls state
        self._controls_visible = True
        self._controls_hide_timer = 0.0
        self._last_mouse_position: tuple[float, float] | None = None

        # Control nodes (created in _build_controls)
        self._controls_bar: Optional[Node] = None
        self._play_button: Optional[Button] = None
        self._progress_slider: Optional[Slider] = None
        self._time_label: Optional[Text] = None
        self._volume_btn: Optional[Button] = None
        self._volume_slider: Optional[Slider] = None
        self._is_seeking = False
        self._video_display_bounds: tuple[float, float, float, float] | None = None

        # If dependencies not available, show placeholder instead
        if not self._deps_available:
            logger.warning(
                "Video playback requires 'av'. Install with: pip install arepy-ui[full]"
            )
            self._build_placeholder()
            return

        # Audio - get from runtime
        runtime = get_runtime()
        if runtime.has_audio_device:
            self._audio_device = runtime.audio_device

        # Build controls UI
        if self._controls_config:
            self._build_controls()

        # Set click handler for video area (play/pause toggle)
        self.on_click = self._on_video_click

    def _build_placeholder(self):
        """Build a placeholder UI when video dependencies are not available."""
        # Container for centered text
        placeholder = Node(
            style=Style(
                width=Unit.percent(100),
                height=Unit.percent(100),
                flex_direction=FlexDirection.COLUMN,
                justify_content=JustifyContent.CENTER,
                align_items=AlignItems.CENTER,
                background_color=Color(20, 20, 20, 255),
            )
        )

        # Text measurement depends on a configured runtime. Keep construction safe
        # even when Video is instantiated outside a live arepy environment.
        if not get_runtime().is_configured:
            self.add_child(placeholder)
            return

        # Main message
        title = Text(
            text="Video Not Supported :(",
            color=Color(255, 255, 255, 255),
            size=18,
            style=Style(
                margin=Spacing.symmetric(0, 8),
            ),
        )
        placeholder.add_child(title)

        # Instructions
        instructions = Text(
            text="Install with: pip install arepy-ui[full]",
            color=Color(180, 180, 180, 255),
            size=14,
        )
        placeholder.add_child(instructions)

        self.add_child(placeholder)

    def _build_controls(self):
        """Build the controls bar using UI components."""
        cfg = self._controls_config
        if not cfg:
            return

        controls_height = self._get_controls_height()
        bar_style = self._build_controls_bar_style(cfg, controls_height)

        # Controls bar container - positioned at bottom
        self._controls_bar = Node(style=bar_style)

        # Play/Pause button
        if cfg.show_play:
            self._play_button = self._build_controls_button(
                text=self._get_play_button_text(),
                on_click=self._on_play_click,
                width=Unit.px(80),
                height=Unit.px(34),
                font_size=13,
            )
            self._controls_bar.add_child(self._play_button)

        # Progress slider
        if cfg.show_progress:
            self._progress_slider = Slider(
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                width=Unit.px(180),
                height=Unit.px(24),
                track_color=Color(255, 255, 255, 55),
                fill_color=cfg.accent_color,
                thumb_color=cfg.foreground_color,
                thumb_size=10,
                track_height=4,
                on_change=self._on_progress_change,
            )
            self._controls_bar.add_child(self._progress_slider)

        # Time label
        if cfg.show_time:
            self._time_label = Text(
                "00:00 / 00:00",
                size=13,
                color=cfg.foreground_color,
            )
            self._controls_bar.add_child(self._time_label)

        # Volume slider
        if cfg.show_volume:
            self._volume_btn = self._build_controls_button(
                text=self._get_volume_button_text(),
                on_click=self._on_mute_click,
                width=Unit.px(64),
                height=Unit.px(34),
                font_size=12,
            )
            self._controls_bar.add_child(self._volume_btn)

            self._volume_slider = Slider(
                min_value=0.0,
                max_value=100.0,
                value=self._volume * 100,
                width=Unit.px(76),
                height=Unit.px(24),
                track_color=Color(255, 255, 255, 55),
                fill_color=cfg.accent_color,
                thumb_color=cfg.foreground_color,
                thumb_size=10,
                track_height=3,
                on_change=self._on_volume_change,
            )
            self._controls_bar.add_child(self._volume_slider)

        self.add_child(self._controls_bar)
        self._set_controls_visible(True)

    def _get_controls_height(self) -> int:
        cfg = self._controls_config
        controls_height = 52
        if cfg and cfg.style.height and hasattr(cfg.style.height, "value"):
            controls_height = int(cfg.style.height.value)
        return controls_height

    def _get_controls_button_colors(self) -> tuple[Color, Color, Color]:
        base = Color(255, 255, 255, 26)
        hover = Color(255, 255, 255, 40)
        pressed = Color(255, 255, 255, 58)
        return base, hover, pressed

    def _build_controls_button(
        self,
        text: str,
        on_click: Callable[[], None],
        width: Unit,
        height: Unit,
        font_size: float,
    ) -> Button:
        cfg = self._controls_config
        assert cfg is not None

        base_color, hover_color, pressed_color = self._get_controls_button_colors()
        return Button(
            text=text,
            on_click=on_click,
            width=width,
            height=height,
            bg_color=base_color,
            text_color=cfg.foreground_color,
            border_radius=17.0,
            font_size=font_size,
            hover_color=hover_color,
            pressed_color=pressed_color,
        )

    def _get_play_button_text(self) -> str:
        return "PAUSE" if self.is_playing else "PLAY"

    def _get_volume_button_text(self) -> str:
        return "MUTE" if self.muted or self._volume <= 0 else "VOL"

    def _build_controls_bar_style(
        self, cfg: ControlsConfig, controls_height: int
    ) -> Style:
        base_style = Style(
            position=PositionType.ABSOLUTE,
            bottom=Unit.px(0),
            left=Unit.px(0),
            right=Unit.px(0),
            height=Unit.px(controls_height),
            width=Unit.percent(100),
            background_color=cfg.style.background_color or Color(10, 10, 14, 210),
            flex_direction=FlexDirection.ROW,
            align_items=AlignItems.CENTER,
            padding=Spacing.symmetric(0, 18),
            gap=14,
            border_radius=0.0,
        )
        merge_non_default_style_fields(
            base_style,
            cfg.style,
            (
                "background_color",
                "border_color",
                "border_width",
                "border_radius",
                "opacity",
                "padding",
                "gap",
            ),
        )
        base_style.position = PositionType.ABSOLUTE
        base_style.bottom = Unit.px(0)
        base_style.left = Unit.px(0)
        base_style.right = Unit.px(0)
        base_style.height = Unit.px(controls_height)
        base_style.width = Unit.percent(100)
        base_style.flex_direction = FlexDirection.ROW
        base_style.align_items = AlignItems.CENTER
        return base_style

    def _set_controls_visible(self, visible: bool):
        self._controls_visible = visible

    def _reveal_controls(self):
        self._controls_hide_timer = 0.0
        self._set_controls_visible(True)

    def _normalize_mouse_position(self, mouse_pos: Any) -> tuple[float, float]:
        if isinstance(mouse_pos, tuple):
            return float(mouse_pos[0]), float(mouse_pos[1])
        return float(mouse_pos.x), float(mouse_pos.y)

    def _is_mouse_over_video(self, mouse_x: float, mouse_y: float) -> bool:
        rect = self._video_display_bounds or (
            self.computed_x,
            self.computed_y,
            self.computed_width,
            self.computed_height,
        )
        rect_x, rect_y, rect_width, rect_height = rect
        return (
            rect_x <= mouse_x < rect_x + rect_width
            and rect_y <= mouse_y < rect_y + rect_height
        )

    def _update_controls_visibility(self, runtime):
        if not self._controls_config or not self._controls_bar:
            return

        if not self._controls_config.auto_hide or not self.is_playing:
            self._controls_hide_timer = 0.0
            self._set_controls_visible(True)
            mouse_pos = runtime.input.get_mouse_position()
            self._last_mouse_position = self._normalize_mouse_position(mouse_pos)
            return

        delta_time = runtime.renderer.get_delta_time()
        mouse_x, mouse_y = self._normalize_mouse_position(
            runtime.input.get_mouse_position()
        )
        mouse_down = runtime.input.is_mouse_button_down(MOUSE_BUTTON_LEFT)
        mouse_moved = (
            self._last_mouse_position is None
            or self._last_mouse_position
            != (
                mouse_x,
                mouse_y,
            )
        )

        if self._is_mouse_over_video(mouse_x, mouse_y) and (mouse_moved or mouse_down):
            self._reveal_controls()
        else:
            self._controls_hide_timer += delta_time
            if self._controls_hide_timer >= self._controls_config.hide_delay:
                self._set_controls_visible(False)

        self._last_mouse_position = (mouse_x, mouse_y)

    def _get_reserved_controls_width(self) -> float:
        used_width = 24.0
        if self._play_button:
            used_width += self._play_button.style.width.value + 10
        if self._time_label:
            used_width += max(self._time_label.computed_width, 104) + 10
        if self._volume_btn:
            used_width += self._volume_btn.style.width.value + 10
        if self._volume_slider:
            used_width += self._volume_slider.style.width.value + 10
        return used_width

    def _get_video_display_rect(self) -> tuple[float, float, float, float]:
        if self.computed_width <= 0 or self.computed_height <= 0:
            return (self.computed_x, self.computed_y, 0.0, 0.0)

        if self._video_width <= 0 or self._video_height <= 0:
            return (
                self.computed_x,
                self.computed_y,
                self.computed_width,
                self.computed_height,
            )

        video_aspect = self._video_width / self._video_height
        container_aspect = self.computed_width / self.computed_height

        if video_aspect > container_aspect:
            dst_width = self.computed_width
            dst_height = self.computed_width / video_aspect
        else:
            dst_height = self.computed_height
            dst_width = self.computed_height * video_aspect

        dst_x = self.computed_x + (self.computed_width - dst_width) / 2
        dst_y = self.computed_y + (self.computed_height - dst_height) / 2
        return (dst_x, dst_y, dst_width, dst_height)

    def _layout_controls_overlay(self):
        if not self._controls_bar:
            return

        display_x, display_y, display_width, display_height = (
            self._get_video_display_rect()
        )
        self._video_display_bounds = (
            display_x,
            display_y,
            display_width,
            display_height,
        )

        if display_width <= 0 or display_height <= 0:
            return

        self._controls_bar.calculate_layout(
            display_x,
            display_y,
            display_width,
            display_height,
        )

    def _on_video_click(self):
        """Handle click on video area - toggle play/pause."""
        # Don't toggle if clicking on controls
        runtime = get_runtime()
        mouse_x, mouse_y = runtime.input.get_mouse_position()

        # Check if click is in controls area
        if self._controls_bar and self._controls_config:
            if not self._controls_visible:
                self._reveal_controls()

            controls_right = (
                self._controls_bar.computed_x + self._controls_bar.computed_width
            )
            controls_bottom = (
                self._controls_bar.computed_y + self._controls_bar.computed_height
            )
            in_controls = (
                self._controls_bar.computed_x <= mouse_x < controls_right
                and self._controls_bar.computed_y <= mouse_y < controls_bottom
            )
            if in_controls:
                return  # Click is on controls, don't toggle

        self.toggle_play()

    def _on_play_click(self):
        """Handle play button click."""
        self._reveal_controls()
        self.toggle_play()

    def _on_progress_change(self, value: float):
        """Handle progress slider change."""
        self._reveal_controls()
        if self._duration > 0:
            seek_time = (value / 100.0) * self._duration
            self.seek(seek_time)

    def _on_volume_change(self, value: float):
        """Handle volume slider change."""
        self._reveal_controls()
        self.volume = value / 100.0

    def _on_mute_click(self):
        """Toggle mute."""
        self._reveal_controls()
        self.muted = not self.muted
        if self.muted:
            self.volume = 0.0
        else:
            self.volume = 1.0

    def _update_controls(self):
        """Update controls to reflect current state."""
        if not self._controls_config:
            return

        # Update play button icon
        if self._play_button:
            self._play_button.text_node.text = self._get_play_button_text()

        # Update progress slider width dynamically
        if self._progress_slider and self._controls_bar:
            controls_width = self._controls_bar.computed_width or self.computed_width
            available_width = max(
                100, controls_width - self._get_reserved_controls_width()
            )
            self._progress_slider.style.width = Unit.px(available_width)

        # Update progress slider value
        if self._progress_slider and self._duration > 0:
            progress = (self._current_time / self._duration) * 100
            self._progress_slider._value = progress  # Direct update to avoid callback

        # Update time label
        if self._time_label:
            current = self._format_time(self._current_time)
            total = self._format_time(self._duration)
            self._time_label.text = f"{current} / {total}"

        if self._volume_btn:
            self._volume_btn.text_node.text = self._get_volume_button_text()

        # Update volume slider
        if self._volume_slider:
            self._volume_slider._value = self._volume * 100

        self._layout_controls_overlay()

    def calculate_layout(self, parent_x, parent_y, parent_width, parent_height):
        super().calculate_layout(parent_x, parent_y, parent_width, parent_height)
        self._layout_controls_overlay()

    @property
    def controls(self) -> Optional[ControlsConfig]:
        """Get controls configuration."""
        return self._controls_config

    @controls.setter
    def controls(self, value: Optional[Union[ControlsConfig, bool]]):
        """Set controls configuration."""
        # Remove existing controls
        if self._controls_bar and self._controls_bar in self.children:
            self.children.remove(self._controls_bar)
            self._controls_bar = None
            self._play_button = None
            self._progress_slider = None
            self._time_label = None
            self._volume_btn = None
            self._volume_slider = None

        if value is True:
            self._controls_config = ControlsConfig()
        elif value is False or value is None:
            self._controls_config = None
        else:
            self._controls_config = value

        # Rebuild controls
        if self._controls_config:
            self._build_controls()

    @property
    def volume(self) -> float:
        return self._volume

    @volume.setter
    def volume(self, value: float):
        self._volume = max(0.0, min(1.0, value))
        if self._has_audio and self._audio_music and self._audio_device:
            self._audio_device.set_music_volume(self._audio_music, self._volume)

    @property
    def current_time(self) -> float:
        return self._current_time

    @property
    def duration(self) -> float:
        return self._duration

    @property
    def is_playing(self) -> bool:
        return self._state == VideoState.PLAYING

    @property
    def is_paused(self) -> bool:
        return self._state == VideoState.PAUSED

    def play(self):
        """Start or resume playback."""
        if not self._deps_available:
            return

        if not self._initialized:
            self._initialize()

        if self._state != VideoState.PLAYING:
            self._state = VideoState.PLAYING
            self._reveal_controls()
            if self._has_audio and self._audio_music and self._audio_device:
                self._audio_device.resume_music(self._audio_music)
            if self.on_play_callback:
                self.on_play_callback()

    def pause(self):
        """Pause playback."""
        if not self._deps_available:
            return

        if self._state == VideoState.PLAYING:
            self._state = VideoState.PAUSED
            self._reveal_controls()
            if self._has_audio and self._audio_music and self._audio_device:
                self._audio_device.pause_music(self._audio_music)
            if self.on_pause_callback:
                self.on_pause_callback()

    def toggle_play(self):
        """Toggle between play and pause."""
        if not self._deps_available:
            return

        if self.is_playing:
            self.pause()
        else:
            self.play()

    def seek(self, time: float):
        """Seek to a specific time in seconds."""
        if not self._deps_available:
            return

        if not self._initialized or not self._video_container or not self._video_stream:
            return

        time = max(0.0, min(time, self._duration))

        try:
            runtime = get_runtime()
            was_playing = self.is_playing

            if self._has_audio and self._audio_music and self._audio_device:
                try:
                    self._audio_device.pause_music(self._audio_music)
                except Exception:
                    pass

            primed = self._prime_video_at_time(time, runtime)
            if not primed:
                self._current_time = time

            if self._has_audio and self._audio_music and self._audio_device:
                self._audio_device.seek_music_stream(
                    self._audio_music, self._current_time
                )
                self._audio_device.update_music_stream(self._audio_music)
                if was_playing:
                    self._audio_device.resume_music(self._audio_music)

            self._post_seek_sync_remaining = self._post_seek_sync_duration
        except Exception as e:
            logger.error(f"Seek error: {e}")

    def stop(self):
        """Stop playback and reset to beginning."""
        if not self._deps_available:
            return

        self._state = VideoState.STOPPED
        self.seek(0)

    def _find_audio_file(self) -> Optional[str]:
        """Try to find a matching audio file."""
        base_path = os.path.splitext(self.source)[0]
        audio_extensions = [".mp3", ".ogg", ".wav", ".flac"]

        for ext in audio_extensions:
            audio_path = base_path + ext
            if os.path.exists(audio_path):
                return audio_path
        return None

    def _extract_audio_from_video(self) -> Optional[bytes]:
        """Extract audio from video file as WAV bytes."""
        try:
            av_module = _get_av()
            container = av_module.open(self.source)

            if len(container.streams.audio) == 0:
                container.close()
                return None

            audio_stream = container.streams.audio[0]
            audio_data = []
            sample_rate = audio_stream.rate
            channels = audio_stream.channels

            resampler = av_module.AudioResampler(
                format="s16",
                layout="stereo" if channels >= 2 else "mono",
                rate=sample_rate,
            )

            for frame in container.decode(audio=0):
                resampled = resampler.resample(frame)
                for r in resampled:
                    audio_data.append(r.to_ndarray().tobytes())

            container.close()

            if not audio_data:
                return None

            raw_audio = b"".join(audio_data)
            num_channels = 2 if channels >= 2 else 1
            sample_width = 2

            wav_buffer = bytearray()
            wav_buffer.extend(b"RIFF")
            wav_buffer.extend(struct.pack("<I", 36 + len(raw_audio)))
            wav_buffer.extend(b"WAVE")
            wav_buffer.extend(b"fmt ")
            wav_buffer.extend(struct.pack("<I", 16))
            wav_buffer.extend(struct.pack("<H", 1))
            wav_buffer.extend(struct.pack("<H", num_channels))
            wav_buffer.extend(struct.pack("<I", sample_rate))
            wav_buffer.extend(
                struct.pack("<I", sample_rate * num_channels * sample_width)
            )
            wav_buffer.extend(struct.pack("<H", num_channels * sample_width))
            wav_buffer.extend(struct.pack("<H", sample_width * 8))
            wav_buffer.extend(b"data")
            wav_buffer.extend(struct.pack("<I", len(raw_audio)))
            wav_buffer.extend(raw_audio)

            return bytes(wav_buffer)

        except Exception as e:
            logger.error(f"Failed to extract audio: {e}")
            return None

    def _init_audio(self):
        """Initialize audio from video or separate file."""
        if not self._audio_device or self.muted:
            return

        from pathlib import Path

        audio_path = self._find_audio_file()

        if audio_path:
            try:
                self._audio_music = self._audio_device.load_music(Path(audio_path))
                self._audio_device.play_music(self._audio_music)
                self._audio_device.set_music_volume(self._audio_music, self._volume)
                self._has_audio = True
                return
            except Exception as e:
                logger.error(f"Failed to load audio file: {e}")

        self._audio_memory_data = self._extract_audio_from_video()

        if self._audio_memory_data:
            try:
                self._audio_music = self._audio_device.load_music_from_memory(
                    ".wav", self._audio_memory_data
                )
                if self._audio_music:
                    self._audio_device.play_music(self._audio_music)
                    self._audio_device.set_music_volume(self._audio_music, self._volume)
                    self._has_audio = True
            except Exception as e:
                logger.error(f"Failed to load audio from memory: {e}")
                self._has_audio = False

    def _initialize(self):
        """Initialize video resources."""
        if self._initialized:
            return

        runtime = get_runtime()

        try:
            av_module = _get_av()
            self._video_container = av_module.open(self.source)
            self._video_stream = self._video_container.streams.video[0]

            self._video_width = self._video_stream.width
            self._video_height = self._video_stream.height
            self._video_fps = (
                float(self._video_stream.average_rate)
                if self._video_stream.average_rate
                else 30.0
            )

            if self._video_stream.duration and self._video_stream.time_base:
                self._duration = float(
                    self._video_stream.duration * self._video_stream.time_base
                )
            elif self._video_container.duration:
                self._duration = self._video_container.duration / 1000000.0

            if not runtime.renderer.is_streaming_available():
                runtime.renderer.init_streaming()

            if not runtime.renderer.is_streaming_available():
                logger.error("Failed to initialize PBO streaming")
                return

            self._streaming_texture = runtime.renderer.create_streaming_texture(
                self._video_width, self._video_height, 4
            )

            if self._streaming_texture is None:
                logger.error("Failed to create streaming texture")
                return

            self._frame_generator = self._video_container.decode(video=0)

            self._init_audio()

            self._initialized = True

            if self.autoplay:
                self._state = VideoState.PLAYING

        except Exception as e:
            logger.error(f"Failed to initialize video: {e}")

    def _get_next_frame(self) -> Optional[bytes]:
        """Get the next video frame as RGBA bytes."""
        try:
            if self._frame_generator is None:
                return None
            frame = next(self._frame_generator)
            return self._frame_to_pixels(frame)

        except StopIteration:
            if self.loop:
                self._video_container.seek(0)
                self._frame_generator = self._video_container.decode(video=0)
                self._current_time = 0.0

                if self._has_audio and self._audio_music and self._audio_device:
                    self._audio_device.seek_music_stream(self._audio_music, 0.0)

                try:
                    if self._frame_generator is None:
                        return None
                    frame = next(self._frame_generator)
                    return self._frame_to_pixels(frame)
                except Exception:
                    return None
            else:
                self._state = VideoState.STOPPED
                if self.on_ended:
                    self.on_ended()
                return None

        except Exception as e:
            logger.error(f"Error getting frame: {e}")
            return None

    def _format_time(self, seconds: float) -> str:
        """Format seconds as MM:SS."""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

    def _update_current_time_from_frame(self, frame: Any) -> Optional[float]:
        if (
            frame.pts is not None
            and self._video_stream
            and self._video_stream.time_base
        ):
            self._current_time = float(frame.pts * self._video_stream.time_base)
            if self.on_time_update:
                self.on_time_update(self._current_time)
            return self._current_time
        return None

    def _frame_to_pixels(self, frame: Any) -> bytes:
        self._update_current_time_from_frame(frame)
        rgba_frame = frame.to_ndarray(format="rgba")
        return rgba_frame.tobytes()

    def _update_streaming_texture(self, runtime, pixels: Optional[bytes]) -> None:
        if pixels and self._streaming_texture:
            runtime.renderer.update_streaming_texture(self._streaming_texture, pixels)

    def _prime_video_at_time(self, target_time: float, runtime) -> bool:
        if not self._video_container or not self._video_stream:
            return False

        stream = self._video_stream
        time_base = getattr(stream, "time_base", None)
        if not time_base:
            return False

        pts = int(target_time / float(time_base))
        self._video_container.seek(pts, stream=stream, backward=True)
        self._frame_generator = self._video_container.decode(video=0)

        max_scan_frames = max(int(self._video_fps * 2), 1)
        frame_duration = 1.0 / self._video_fps if self._video_fps > 0 else 0.0
        selected_frame = None
        last_frame = None

        for _ in range(max_scan_frames):
            if self._frame_generator is None:
                break

            try:
                frame = next(self._frame_generator)
            except StopIteration:
                break

            last_frame = frame
            frame_time = self._update_current_time_from_frame(frame)
            if frame_time is None:
                selected_frame = frame
                break

            if frame_time + (frame_duration * 0.5) >= target_time:
                selected_frame = frame
                break

        if selected_frame is None:
            selected_frame = last_frame

        if selected_frame is None:
            return False

        pixels = self._frame_to_pixels(selected_frame)
        self._update_streaming_texture(runtime, pixels)
        self._frame_time_acc = 0.0
        return True

    def _sync_video_to_audio(self, runtime, audio_time: float) -> None:
        time_diff = audio_time - self._current_time

        if self._post_seek_sync_remaining > 0.0:
            self._post_seek_sync_remaining = max(
                0.0,
                self._post_seek_sync_remaining - runtime.renderer.get_delta_time(),
            )

            if abs(time_diff) > 0.2:
                self._prime_video_at_time(audio_time, runtime)
                return

            if time_diff > 0:
                self._update_streaming_texture(runtime, self._get_next_frame())
            return

        if time_diff > 0.1:
            max_skip_frames = 30
            skipped = 0
            latest_pixels = None
            while self._current_time < audio_time - 0.05 and skipped < max_skip_frames:
                latest_pixels = self._get_next_frame()
                skipped += 1
                if not latest_pixels:
                    break
            self._update_streaming_texture(runtime, latest_pixels)
        elif time_diff > 0:
            self._update_streaming_texture(runtime, self._get_next_frame())

    def _advance_video_without_audio(self, runtime) -> None:
        delta_time = runtime.renderer.get_delta_time()
        self._frame_time_acc += delta_time

        frame_duration = 1.0 / self._video_fps
        if self._frame_time_acc >= frame_duration:
            self._frame_time_acc -= frame_duration
            self._update_streaming_texture(runtime, self._get_next_frame())

    def render(self):
        """Render the video player."""
        if not self.style.visible:
            return

        # If dependencies not available, just render children (placeholder)
        if not self._deps_available:
            for child in self.children:
                child.render()
            return

        from arepy import Color as ArepyColor
        from arepy.engine.renderer import Rect

        runtime = get_runtime()

        # Culling check
        screen_w, screen_h = runtime.display.get_window_size()
        if (
            self.computed_x > screen_w
            or self.computed_x + self.computed_width < 0
            or self.computed_y > screen_h
            or self.computed_y + self.computed_height < 0
        ):
            return

        # Draw background first
        if self.style.background_color:
            bg_rect = Rect(
                int(self.computed_x),
                int(self.computed_y),
                int(self.computed_width),
                int(self.computed_height),
            )
            bg = self.style.background_color
            runtime.renderer.draw_rectangle(bg_rect, ArepyColor(bg.r, bg.g, bg.b, bg.a))

        # Initialize on first render if autoplay
        if not self._initialized and self.autoplay:
            self._initialize()

        # Update audio stream
        if self._has_audio and self._audio_music and self._audio_device:
            self._audio_device.update_music_stream(self._audio_music)

        # Update and draw video if initialized
        if self._initialized and self._streaming_texture:
            if self._state == VideoState.PLAYING:
                # Sync video to audio time (audio is master clock)
                if self._has_audio and self._audio_music and self._audio_device:
                    # Get current audio playback position
                    audio_time = self._audio_device.get_music_time_played(
                        self._audio_music
                    )

                    # Detect if audio has looped (audio time reset to near 0 while video is still far ahead)
                    if audio_time < 1.0 and self._current_time > self._duration - 1.0:
                        # Audio has looped, reset video to sync
                        self._prime_video_at_time(0.0, runtime)
                        self._current_time = 0.0

                    self._sync_video_to_audio(runtime, audio_time)
                else:
                    self._advance_video_without_audio(runtime)

            texture = runtime.renderer.get_streaming_texture(self._streaming_texture)

            if texture:
                dst_x, dst_y, dst_width, dst_height = self._get_video_display_rect()
                self._video_display_bounds = (dst_x, dst_y, dst_width, dst_height)

                src_rect = Rect(0, 0, self._video_width, self._video_height)
                dst_rect = Rect(int(dst_x), int(dst_y), int(dst_width), int(dst_height))

                runtime.renderer.draw_texture_ex(
                    texture,
                    src_rect,
                    dst_rect,
                    (0, 0),
                    0.0,
                    ArepyColor(255, 255, 255, 255),
                )

        # Update controls state
        self._update_controls()
        self._update_controls_visibility(runtime)

        # Draw big play button if not playing and no controls
        if not self._initialized or (
            self._state != VideoState.PLAYING and not self._controls_config
        ):
            self._render_big_play_button(runtime)

        # Render children (controls) ON TOP of video
        for child in self.children:
            if child is self._controls_bar and not self._controls_visible:
                continue
            child.render()

    def handle_input(self, mouse_pos, is_click, wheel_scroll: float = 0.0) -> bool:
        from arepy.engine.renderer import Rect
        from arepy.math import check_collision_point_rec

        if not self.style.visible:
            return False

        for child in reversed(self.children):
            if child is self._controls_bar and not self._controls_visible:
                continue
            if child.handle_input(mouse_pos, is_click, wheel_scroll):
                return True

        if not self.pickable:
            return False

        rect = Rect(
            self.computed_x,
            self.computed_y,
            int(self.computed_width),
            int(self.computed_height),
        )
        is_over = check_collision_point_rec((mouse_pos.x, mouse_pos.y), rect)

        if is_over:
            if not self.is_hovered:
                self.is_hovered = True
                if self.on_hover_enter:
                    self.on_hover_enter()

            if is_click and self.on_click:
                self.on_click()
                return True
        else:
            if self.is_hovered:
                self.is_hovered = False
                if self.on_hover_exit:
                    self.on_hover_exit()

        return False

    def _render_big_play_button(self, runtime):
        """Render large centered play button."""
        from arepy import Color as ArepyColor

        cx = int(self.computed_x + self.computed_width / 2)
        cy = int(self.computed_y + self.computed_height / 2)

        runtime.renderer.draw_circle((cx, cy), 40, ArepyColor(0, 0, 0, 150))
        runtime.renderer.draw_text(
            ">", (cx - 8, cy - 12), 30, ArepyColor(255, 255, 255, 255)
        )

    def cleanup(self):
        """Clean up video resources."""
        if not self._deps_available:
            return

        if self._has_audio and self._audio_music and self._audio_device:
            try:
                self._audio_device.stop_music(self._audio_music)
                self._audio_device.unload_music(self._audio_music)
            except Exception:
                pass

        if self._video_container:
            try:
                self._video_container.close()
            except Exception:
                pass
            self._video_container = None

        self._audio_memory_data = None
        self._initialized = False

    def __del__(self):
        """Destructor to clean up resources."""
        self.cleanup()
