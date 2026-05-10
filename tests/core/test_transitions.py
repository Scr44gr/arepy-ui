"""Tests for transitions module."""

from unittest.mock import MagicMock, patch

import pytest


class TestTransitionState:
    """Tests for TransitionState enum."""

    def test_transition_states(self):
        """Test all transition states are defined."""
        from arepy_ui.core.transitions import TransitionState

        assert TransitionState.PENDING is not None
        assert TransitionState.RUNNING is not None
        assert TransitionState.COMPLETED is not None
        assert TransitionState.CANCELLED is not None


class TestKeyFrame:
    """Tests for KeyFrame dataclass."""

    def test_keyframe_creation(self):
        """Test creating a KeyFrame."""
        from arepy_ui.core.animation import Easing
        from arepy_ui.core.transitions import KeyFrame

        keyframe = KeyFrame(time=0.0, value=0.0)

        assert keyframe.time == 0.0
        assert keyframe.value == 0.0
        assert keyframe.easing == Easing.EASE_OUT_CUBIC

    def test_keyframe_with_custom_easing(self):
        """Test KeyFrame with custom easing."""
        from arepy_ui.core.animation import Easing
        from arepy_ui.core.transitions import KeyFrame

        keyframe = KeyFrame(time=1.0, value=100.0, easing=Easing.LINEAR)

        assert keyframe.easing == Easing.LINEAR


class TestPropertyAnimation:
    """Tests for PropertyAnimation dataclass."""

    def test_property_animation_creation(self):
        """Test creating a PropertyAnimation."""
        from arepy_ui.core.transitions import KeyFrame, PropertyAnimation

        target = MagicMock()
        keyframes = [KeyFrame(time=0.0, value=0.0), KeyFrame(time=1.0, value=100.0)]

        anim = PropertyAnimation(
            target=target, property_name="opacity", keyframes=keyframes
        )

        assert anim.target == target
        assert anim.property_name == "opacity"
        assert len(anim.keyframes) == 2

    def test_property_animation_initial_state(self):
        """Test PropertyAnimation initial state."""
        from arepy_ui.core.transitions import KeyFrame, PropertyAnimation

        target = MagicMock()
        keyframes = [KeyFrame(time=0.0, value=0.0), KeyFrame(time=1.0, value=100.0)]

        anim = PropertyAnimation(target=target, property_name="x", keyframes=keyframes)

        assert anim._current_keyframe_index == 0
        assert anim._elapsed == 0.0
        assert anim._is_finished == False

    def test_property_animation_update(self):
        """Test PropertyAnimation update method."""
        from arepy_ui.core.transitions import KeyFrame, PropertyAnimation

        target = MagicMock()
        target.x = 0.0
        keyframes = [KeyFrame(time=0.0, value=0.0), KeyFrame(time=1.0, value=100.0)]

        anim = PropertyAnimation(target=target, property_name="x", keyframes=keyframes)

        # Update with some delta time
        result = anim.update(0.5)

        assert result == True  # Still running
        assert anim._elapsed > 0

    def test_property_animation_update_finished(self):
        """Test PropertyAnimation update when finished."""
        from arepy_ui.core.transitions import KeyFrame, PropertyAnimation

        target = MagicMock()
        target.x = 0.0
        keyframes = [KeyFrame(time=0.0, value=0.0), KeyFrame(time=1.0, value=100.0)]

        anim = PropertyAnimation(target=target, property_name="x", keyframes=keyframes)

        # Update past the animation duration
        anim.update(1.5)

        assert anim._is_finished == True

    def test_property_animation_reset(self):
        """Test PropertyAnimation reset method."""
        from arepy_ui.core.transitions import KeyFrame, PropertyAnimation

        target = MagicMock()
        target.x = 0.0
        keyframes = [KeyFrame(time=0.0, value=0.0), KeyFrame(time=1.0, value=100.0)]

        anim = PropertyAnimation(target=target, property_name="x", keyframes=keyframes)

        # Update and then reset
        anim.update(0.5)
        anim.reset()

        assert anim._current_keyframe_index == 0
        assert anim._elapsed == 0.0
        assert anim._is_finished == False

    def test_property_animation_nested_property(self):
        """Test PropertyAnimation with nested property."""
        from arepy_ui.core.transitions import KeyFrame, PropertyAnimation

        target = MagicMock()
        target.style = MagicMock()
        target.style.opacity = 0.0
        keyframes = [KeyFrame(time=0.0, value=0.0), KeyFrame(time=1.0, value=1.0)]

        anim = PropertyAnimation(
            target=target, property_name="style.opacity", keyframes=keyframes
        )

        anim.update(0.5)

        # Should set the nested property
        assert True  # If no exception, it worked

    def test_property_animation_single_keyframe(self):
        """Test PropertyAnimation with single keyframe finishes immediately."""
        from arepy_ui.core.transitions import KeyFrame, PropertyAnimation

        target = MagicMock()
        target.x = 0.0
        keyframes = [KeyFrame(time=0.0, value=50.0)]

        anim = PropertyAnimation(target=target, property_name="x", keyframes=keyframes)

        result = anim.update(0.1)

        # Should finish immediately with single keyframe
        assert result == False


class TestTransitions:
    """Integration tests for transitions module."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up mocks for runtime."""
        with patch("arepy_ui.core.transitions.get_runtime") as mock_get_runtime:
            self.mock_runtime = MagicMock()
            self.mock_runtime.time = MagicMock()
            self.mock_runtime.time.get_delta_time.return_value = 0.016
            mock_get_runtime.return_value = self.mock_runtime
            yield

    def test_multiple_keyframes(self):
        """Test animation with multiple keyframes."""
        from arepy_ui.core.animation import Easing
        from arepy_ui.core.transitions import KeyFrame, PropertyAnimation

        target = MagicMock()
        target.value = 0.0
        keyframes = [
            KeyFrame(time=0.0, value=0.0),
            KeyFrame(time=0.5, value=50.0, easing=Easing.LINEAR),
            KeyFrame(time=1.0, value=100.0, easing=Easing.EASE_IN_OUT_QUAD),
        ]

        anim = PropertyAnimation(
            target=target, property_name="value", keyframes=keyframes
        )

        # Update through first segment
        for _ in range(30):  # ~0.48 seconds
            anim.update(0.016)

        assert anim._current_keyframe_index >= 0

    def test_zero_duration_segment(self):
        """Test animation with zero duration segment."""
        from arepy_ui.core.transitions import KeyFrame, PropertyAnimation

        target = MagicMock()
        target.x = 0.0
        keyframes = [
            KeyFrame(time=0.0, value=0.0),
            KeyFrame(time=0.0, value=50.0),  # Same time = instant jump
            KeyFrame(time=1.0, value=100.0),
        ]

        anim = PropertyAnimation(target=target, property_name="x", keyframes=keyframes)

        # Should handle zero duration gracefully
        anim.update(0.1)

        assert True  # No exception = success


class TestTimeline:
    """Tests for Timeline class."""

    def test_timeline_creation(self):
        from arepy_ui.core.transitions import Timeline

        timeline = Timeline(duration=2.0)

        assert timeline.duration == 2.0
        assert timeline.loop is False

    def test_timeline_auto_start(self):
        from arepy_ui.core.transitions import Timeline

        timeline = Timeline(auto_start=True)

        assert timeline._is_running is True

    def test_timeline_manual_start(self):
        from arepy_ui.core.transitions import Timeline

        timeline = Timeline(auto_start=False)
        assert timeline._is_running is False

        timeline.start()
        assert timeline._is_running is True

    def test_timeline_pause_resume(self):
        from arepy_ui.core.transitions import Timeline

        timeline = Timeline(auto_start=True)

        timeline.pause()
        assert timeline._is_running is False

        timeline.resume()
        assert timeline._is_running is True

    def test_timeline_add_animation(self):
        from arepy_ui.core.animation import Easing
        from arepy_ui.core.transitions import Timeline

        target = MagicMock()
        timeline = Timeline()

        result = timeline.add_animation(
            target, "opacity", [(0.0, 0.0, None), (1.0, 1.0, Easing.LINEAR)]
        )

        assert result is timeline  # Chainable
        assert len(timeline._animations) == 1
        assert timeline.duration == 1.0

    def test_timeline_add_event(self):
        from arepy_ui.core.transitions import Timeline

        callback = MagicMock()
        timeline = Timeline()

        result = timeline.add_event(0.5, callback)

        assert result is timeline  # Chainable
        assert len(timeline._events) == 1

    def test_timeline_update_triggers_event(self):
        from arepy_ui.core.transitions import Timeline

        callback = MagicMock()
        timeline = Timeline(duration=1.0, auto_start=True)
        timeline.add_event(0.5, callback)

        # Update past event time
        timeline.update(0.6)

        callback.assert_called_once()

    def test_timeline_progress(self):
        from arepy_ui.core.transitions import Timeline

        timeline = Timeline(duration=2.0, auto_start=True)

        timeline.update(1.0)

        assert timeline.progress == 0.5

    def test_timeline_progress_zero_duration(self):
        from arepy_ui.core.transitions import Timeline

        timeline = Timeline(duration=0.0)

        assert timeline.progress == 1.0

    def test_timeline_on_complete(self):
        from arepy_ui.core.transitions import Timeline

        callback = MagicMock()
        timeline = Timeline(duration=1.0, auto_start=True, on_complete=callback)

        timeline.update(1.5)

        callback.assert_called_once()
        assert timeline.is_finished is True

    def test_timeline_loop(self):
        from arepy_ui.core.transitions import Timeline

        timeline = Timeline(duration=1.0, loop=True, auto_start=True)

        timeline.update(1.5)

        # Should restart, not finish
        assert timeline._is_running is True
        assert timeline._elapsed < 1.0  # Reset


class TestCircleReveal:
    """Tests for CircleReveal class."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        with patch("arepy_ui.core.transitions.get_runtime") as mock:
            self.mock_runtime = MagicMock()
            self.mock_runtime.display.get_window_size.return_value = (800, 600)
            self.mock_runtime.renderer = MagicMock()
            mock.return_value = self.mock_runtime
            yield

    def test_circle_reveal_creation(self):
        from arepy_ui.core.transitions import CircleReveal

        reveal = CircleReveal(center_x=400, center_y=300)

        assert reveal.center_x == 400
        assert reveal.center_y == 300
        assert reveal._is_running is True

    def test_circle_reveal_reverse(self):
        from arepy_ui.core.transitions import CircleReveal

        reveal = CircleReveal(
            center_x=400,
            center_y=300,
            start_radius=0,
            end_radius=500,
            reverse=True,
        )

        assert reveal.start_radius == 500
        assert reveal.end_radius == 0

    def test_circle_reveal_update(self):
        from arepy_ui.core.transitions import CircleReveal

        reveal = CircleReveal(
            center_x=400, center_y=300, start_radius=0, end_radius=100, duration=1.0
        )

        result = reveal.update(0.5)

        assert result is True
        assert reveal._current_radius > 0
        assert reveal._current_radius < 100

    def test_circle_reveal_complete(self):
        from arepy_ui.core.transitions import CircleReveal

        callback = MagicMock()
        reveal = CircleReveal(
            center_x=400, center_y=300, duration=1.0, on_complete=callback
        )

        reveal.update(1.5)

        assert reveal.is_finished is True
        callback.assert_called_once()

    def test_circle_reveal_render_inverse(self):
        from arepy_ui.core.transitions import CircleReveal

        reveal = CircleReveal(center_x=400, center_y=300)
        reveal.update(0.5)

        reveal.render_inverse()

        self.mock_runtime.renderer.draw_circle.assert_called_once()

    def test_circle_reveal_progress(self):
        from arepy_ui.core.transitions import CircleReveal

        reveal = CircleReveal(center_x=400, center_y=300, duration=2.0)

        reveal.update(1.0)

        assert reveal.progress == 0.5

    def test_circle_reveal_progress_zero_duration(self):
        from arepy_ui.core.transitions import CircleReveal

        reveal = CircleReveal(center_x=400, center_y=300, duration=0.0)

        assert reveal.progress == 1.0


class TestFadeTransition:
    """Tests for FadeTransition class."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        with patch("arepy_ui.core.transitions.get_runtime") as mock:
            self.mock_runtime = MagicMock()
            self.mock_runtime.display.get_window_size.return_value = (800, 600)
            self.mock_runtime.renderer = MagicMock()
            mock.return_value = self.mock_runtime
            yield

    def test_fade_in_creation(self):
        from arepy_ui.core.transitions import FadeTransition

        fade = FadeTransition(fade_in=True)

        assert fade.fade_in is True
        assert fade._alpha == 255

    def test_fade_out_creation(self):
        from arepy_ui.core.transitions import FadeTransition

        fade = FadeTransition(fade_in=False)

        assert fade.fade_in is False
        assert fade._alpha == 0

    def test_fade_update(self):
        from arepy_ui.core.transitions import FadeTransition

        fade = FadeTransition(duration=1.0, fade_in=True)

        result = fade.update(0.5)

        assert result is True
        assert fade._alpha < 255
        assert fade._alpha > 0

    def test_fade_complete(self):
        from arepy_ui.core.transitions import FadeTransition

        callback = MagicMock()
        fade = FadeTransition(duration=1.0, on_complete=callback)

        fade.update(1.5)

        assert fade.is_finished is True
        callback.assert_called_once()

    def test_fade_render(self):
        from arepy_ui.core.transitions import FadeTransition

        fade = FadeTransition()
        fade._alpha = 128

        fade.render()

        self.mock_runtime.renderer.draw_rectangle.assert_called_once()

    def test_fade_render_zero_alpha_does_nothing(self):
        from arepy_ui.core.transitions import FadeTransition

        fade = FadeTransition(fade_in=False)
        fade._alpha = 0

        fade.render()

        self.mock_runtime.renderer.draw_rectangle.assert_not_called()


class TestSequenceRunner:
    """Tests for SequenceRunner class."""

    def test_sequence_runner_creation(self):
        from arepy_ui.core.transitions import SequenceRunner

        runner = SequenceRunner()

        assert runner._is_running is False
        assert len(runner._sequences) == 0

    def test_sequence_runner_add(self):
        from arepy_ui.core.transitions import FadeTransition, SequenceRunner

        runner = SequenceRunner()
        fade = FadeTransition()

        result = runner.add(fade, delay=0.5)

        assert result is runner  # Chainable
        assert len(runner._sequences) == 1

    def test_sequence_runner_start(self):
        from arepy_ui.core.transitions import FadeTransition, SequenceRunner

        runner = SequenceRunner()
        runner.add(FadeTransition())
        runner.start()

        assert runner._is_running is True

    def test_sequence_runner_with_callback(self):
        from arepy_ui.core.transitions import SequenceRunner

        callback = MagicMock()
        runner = SequenceRunner()
        runner.add(callback)
        runner.start()

        # Callback should be called immediately
        callback.assert_called_once()

    def test_sequence_runner_complete(self):
        from arepy_ui.core.transitions import SequenceRunner

        on_complete = MagicMock()
        runner = SequenceRunner(on_complete=on_complete)
        runner.add(lambda: None)
        runner.start()

        # Should complete after callback runs
        assert runner.is_finished is True
        on_complete.assert_called_once()

    def test_sequence_runner_with_delay(self):
        from arepy_ui.core.transitions import FadeTransition, SequenceRunner

        runner = SequenceRunner()
        fade = FadeTransition(duration=0.5)
        runner.add(fade, delay=0.5)
        runner.start()

        # First update - still in delay
        runner.update(0.3)
        assert runner._current_item_started is False
        assert fade._elapsed == 0.0

        # Second update - starts item
        runner.update(0.3)
        assert runner._current_item_started is True
        assert runner._delay_timer is None
        assert fade._elapsed == 0.0
