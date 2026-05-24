"""Tests for Video component.

This module tests the Video component while mocking the external dependency 'av' (PyAV).
The Video component requires pip install arepy-ui[full] for actual video playback.
"""

import sys
from unittest.mock import MagicMock, patch

import pytest


class TestVideoState:
    """Tests for VideoState enum."""

    def test_video_states(self):
        """Test all video states are defined."""
        from arepy_ui.components.video import VideoState

        states = [VideoState.STOPPED, VideoState.PLAYING, VideoState.PAUSED]

        assert len(states) == 3
        assert all(isinstance(s, str) for s in states)


class TestControlsConfig:
    """Tests for ControlsConfig dataclass."""

    def test_controls_config_default(self):
        """Test ControlsConfig with default values."""
        from arepy_ui.components.video import ControlsConfig

        config = ControlsConfig()

        assert config.show_play == True
        assert config.show_progress == True
        assert config.show_time == True
        assert config.show_volume == True
        assert config.auto_hide == True
        assert config.style.height.value == 52

    def test_controls_config_custom(self):
        """Test ControlsConfig with custom values."""
        from arepy_ui.components.video import ControlsConfig
        from arepy_ui.core.types import Color

        config = ControlsConfig(
            show_volume=False,
            auto_hide=True,
            hide_delay=5.0,
            accent_color=Color(255, 0, 0, 255),
        )

        assert config.show_volume == False
        assert config.auto_hide == True
        assert config.hide_delay == 5.0
        assert config.accent_color == Color(255, 0, 0, 255)


class TestVideoStyleMerge:
    def test_video_style_overrides_dimensions(self):
        from arepy_ui.components.video import Video
        from arepy_ui.core.style import Style
        from arepy_ui.core.types import Unit

        video = Video(
            source="demo.mp4",
            style=Style(width=Unit.px(320), height=Unit.px(180)),
            controls=False,
        )

        assert video.style.width.value == 320
        assert video.style.height.value == 180


class TestVideoControlsLayout:
    @staticmethod
    def _build_video():
        from arepy_ui.components import video as video_module
        from arepy_ui.components.video import Video
        from arepy_ui.core.types import Unit

        runtime = MagicMock()
        runtime.has_audio_device = False

        with (
            patch.object(video_module, "HAS_VIDEO_DEPS", True),
            patch("arepy_ui.components.video.get_runtime", return_value=runtime),
            patch("arepy_ui.core.fonts.get_font_manager") as mock_font_manager,
        ):
            mock_font_manager.return_value.measure_text_ex.return_value = MagicMock(
                width=30.0, height=12.0, line_height=14.0
            )
            return Video(
                source="demo.mp4",
                width=Unit.px(400),
                height=Unit.px(400),
            )

    def test_controls_bar_is_anchored_to_bottom(self):
        from arepy_ui.core.types import PositionType

        video = self._build_video()

        assert video._controls_bar is not None
        assert video._controls_bar.style.position == PositionType.ABSOLUTE
        assert video._controls_bar.style.bottom is not None
        assert video._controls_bar.style.bottom.value == 0

    def test_controls_bar_defaults_to_no_vertical_padding(self):

        video = self._build_video()

        assert video._controls_bar is not None
        assert video._controls_bar.style.padding.top.value == 0
        assert video._controls_bar.style.padding.bottom.value == 0

    def test_controls_bar_defaults_to_square_corners_and_more_spacing(self):
        video = self._build_video()

        assert video._controls_bar is not None
        assert video._controls_bar.style.border_radius == 0
        assert video._controls_bar.style.gap == 14
        assert video._controls_bar.style.padding.left.value == 18
        assert video._controls_bar.style.padding.right.value == 18

    def test_controls_use_ascii_safe_default_labels(self):
        video = self._build_video()

        assert video._play_button is not None
        assert video._volume_btn is not None
        assert video._play_button.text_node.text == "PLAY"
        assert video._volume_btn.text_node.text == "VOL"

    def test_controls_update_default_labels_with_state(self):
        from arepy_ui.components.video import VideoState

        video = self._build_video()
        video._state = VideoState.PLAYING
        video.muted = True

        with patch("arepy_ui.core.fonts.get_font_manager") as mock_font_manager:
            mock_font_manager.return_value.measure_text_ex.return_value = MagicMock(
                width=40.0, height=12.0, line_height=14.0
            )
            video._update_controls()

        assert video._play_button is not None
        assert video._volume_btn is not None
        assert video._play_button.text_node.text == "PAUSE"
        assert video._volume_btn.text_node.text == "MUTE"

    def test_controls_bar_tracks_visible_video_frame_bottom(self):
        video = self._build_video()

        video._video_width = 1920
        video._video_height = 1080
        video.calculate_layout(0, 0, 400, 400)

        assert video._controls_bar is not None
        assert video._controls_bar.computed_x == pytest.approx(0.0)
        assert video._controls_bar.computed_width == pytest.approx(400.0)
        assert video._controls_bar.computed_y == pytest.approx(260.5)
        assert (
            video._controls_bar.computed_y + video._controls_bar.computed_height
        ) == pytest.approx(312.5)

    def test_controls_auto_hide_after_mouse_inactivity(self):
        from arepy_ui.components.video import VideoState

        video = self._build_video()
        video._state = VideoState.PLAYING
        video._video_display_bounds = (0.0, 0.0, 400.0, 400.0)
        video.calculate_layout(0, 0, 400, 400)
        initial_video_height = video.computed_height
        initial_controls_height = (
            video._controls_bar.computed_height if video._controls_bar else 0
        )

        runtime = MagicMock()
        runtime.input.get_mouse_position.return_value = (100.0, 100.0)
        runtime.input.is_mouse_button_down.return_value = False
        runtime.renderer.get_delta_time.return_value = 1.6

        with patch("arepy_ui.components.video.get_runtime", return_value=runtime):
            video._update_controls_visibility(runtime)
            assert video._controls_visible == True
            video._update_controls_visibility(runtime)
            video._update_controls_visibility(runtime)

        assert video._controls_visible == False
        assert video._controls_bar is not None
        assert video.computed_height == initial_video_height
        assert video._controls_bar.computed_height == initial_controls_height

    def test_controls_reappear_on_mouse_move_over_video(self):
        from arepy_ui.components.video import VideoState

        video = self._build_video()
        video._state = VideoState.PLAYING
        video._video_display_bounds = (0.0, 0.0, 400.0, 400.0)
        video.calculate_layout(0, 0, 400, 400)
        video._set_controls_visible(False)
        video._last_mouse_position = (10.0, 10.0)

        runtime = MagicMock()
        runtime.input.get_mouse_position.return_value = (40.0, 40.0)
        runtime.input.is_mouse_button_down.return_value = False
        runtime.renderer.get_delta_time.return_value = 0.1

        video._update_controls_visibility(runtime)

        assert video._controls_visible == True
        assert video._controls_bar is not None
        assert video._controls_bar.computed_height == pytest.approx(52.0)


class TestVideoSeekSync:
    @staticmethod
    def _build_video_with_audio():
        from arepy_ui.components import video as video_module
        from arepy_ui.components.video import Video
        from arepy_ui.core.types import Unit

        runtime = MagicMock()
        runtime.has_audio_device = True
        runtime.audio_device = MagicMock()
        runtime.renderer = MagicMock()

        with (
            patch.object(video_module, "HAS_VIDEO_DEPS", True),
            patch("arepy_ui.components.video.get_runtime", return_value=runtime),
            patch("arepy_ui.core.fonts.get_font_manager") as mock_font_manager,
        ):
            mock_font_manager.return_value.measure_text_ex.return_value = MagicMock(
                width=30.0, height=12.0, line_height=14.0
            )
            video = Video(
                source="demo.mp4",
                width=Unit.px(400),
                height=Unit.px(240),
            )

        return video, runtime

    def test_seek_primes_video_frame_before_audio_resumes(self):
        video, runtime = self._build_video_with_audio()

        frame_a = MagicMock()
        frame_a.pts = 25
        frame_a.to_ndarray.return_value.tobytes.return_value = b"frame-a"

        frame_b = MagicMock()
        frame_b.pts = 27
        frame_b.to_ndarray.return_value.tobytes.return_value = b"frame-b"

        stream = MagicMock()
        stream.time_base = 0.1

        container = MagicMock()
        container.decode.return_value = iter([frame_a, frame_b])

        video._initialized = True
        video._streaming_texture = "texture"
        video._video_container = container
        video._video_stream = stream
        video._video_fps = 10.0
        video._duration = 10.0
        video._has_audio = True
        video._audio_music = object()
        video._state = "playing"

        with patch("arepy_ui.components.video.get_runtime", return_value=runtime):
            video.seek(2.6)

        container.seek.assert_called_once_with(26, stream=stream, backward=True)
        runtime.renderer.update_streaming_texture.assert_called_once_with(
            "texture", b"frame-b"
        )
        assert video.current_time == pytest.approx(2.7)
        assert video._post_seek_sync_remaining == pytest.approx(
            video._post_seek_sync_duration
        )

        audio_calls = [
            call
            for call in runtime.audio_device.mock_calls
            if call[0]
            in {
                "pause_music",
                "seek_music_stream",
                "update_music_stream",
                "resume_music",
            }
        ]
        assert audio_calls[0][0] == "pause_music"
        assert audio_calls[1][0] == "seek_music_stream"
        assert audio_calls[1][1][1] == pytest.approx(2.7)
        assert audio_calls[2][0] == "update_music_stream"
        assert audio_calls[3][0] == "resume_music"

    def test_post_seek_sync_window_retargets_instead_of_skipping_frames(self):
        video, runtime = self._build_video_with_audio()
        video._current_time = 1.0
        video._post_seek_sync_remaining = 0.2
        runtime.renderer.get_delta_time.return_value = 0.05

        with patch.object(video, "_prime_video_at_time", return_value=True) as prime:
            with patch.object(video, "_get_next_frame") as get_next_frame:
                video._sync_video_to_audio(runtime, 1.5)

        prime.assert_called_once_with(1.5, runtime)
        get_next_frame.assert_not_called()
