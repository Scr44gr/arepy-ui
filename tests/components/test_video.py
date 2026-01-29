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
        assert config.auto_hide == False

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
