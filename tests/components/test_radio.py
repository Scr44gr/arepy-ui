"""Tests for RadioGroup component."""

from unittest.mock import MagicMock, patch

import pytest


class TestRadioGroup:
    """Tests for RadioGroup component."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up mocks for runtime."""
        with (
            patch("arepy_ui.components.radio.get_runtime") as mock_get_runtime,
            patch(
                "arepy_ui.components.radio.check_collision_point_rec"
            ) as mock_collision,
        ):
            self.mock_runtime = MagicMock()
            self.mock_renderer = MagicMock()
            self.mock_renderer.measure_text.return_value = 100
            self.mock_runtime.renderer = self.mock_renderer
            self.mock_runtime.input = MagicMock()
            self.mock_runtime.input.is_key_pressed.return_value = False
            mock_get_runtime.return_value = self.mock_runtime

            self.mock_collision = mock_collision
            mock_collision.return_value = False

            yield

    def test_radiogroup_creation_empty(self):
        """Test creating an empty RadioGroup."""
        from arepy_ui.components.radio import RadioGroup

        radio_group = RadioGroup()

        assert radio_group is not None
        assert len(radio_group.options) == 0

    def test_radiogroup_creation_with_options(self):
        """Test creating a RadioGroup with options."""
        from arepy_ui.components.radio import RadioGroup, RadioOption

        options = [
            RadioOption(label="Option 1", value="opt1"),
            RadioOption(label="Option 2", value="opt2"),
            RadioOption(label="Option 3", value="opt3"),
        ]
        radio_group = RadioGroup(options=options)

        assert len(radio_group.options) == 3
        assert radio_group.options[0].label == "Option 1"

    def test_radiogroup_initial_selection(self):
        """Test RadioGroup with initial selection."""
        from arepy_ui.components.radio import RadioGroup, RadioOption

        options = [
            RadioOption(label="Option 1", value="opt1"),
            RadioOption(label="Option 2", value="opt2"),
        ]
        radio_group = RadioGroup(options=options, selected_value="opt2")

        assert radio_group._selected_index == 1

    def test_radiogroup_no_initial_selection(self):
        """Test RadioGroup without initial selection."""
        from arepy_ui.components.radio import RadioGroup, RadioOption

        options = [
            RadioOption(label="Option 1", value="opt1"),
            RadioOption(label="Option 2", value="opt2"),
        ]
        radio_group = RadioGroup(options=options)

        assert radio_group._selected_index == -1

    def test_radiogroup_on_change_callback(self):
        """Test RadioGroup on_change callback."""
        from arepy_ui.components.radio import RadioGroup, RadioOption

        on_change_callback = MagicMock()
        options = [
            RadioOption(label="Option 1", value="opt1"),
        ]
        radio_group = RadioGroup(options=options, on_change=on_change_callback)

        assert radio_group.on_change == on_change_callback

    def test_radiogroup_vertical_layout(self):
        """Test RadioGroup with vertical layout."""
        from arepy_ui.components.radio import RadioGroup
        from arepy_ui.core.types import FlexDirection

        radio_group = RadioGroup(direction=FlexDirection.COLUMN)

        assert radio_group.style.flex_direction == FlexDirection.COLUMN

    def test_radiogroup_horizontal_layout(self):
        """Test RadioGroup with horizontal layout."""
        from arepy_ui.components.radio import RadioGroup
        from arepy_ui.core.types import FlexDirection

        radio_group = RadioGroup(direction=FlexDirection.ROW)

        assert radio_group.style.flex_direction == FlexDirection.ROW

    def test_radiogroup_custom_gap(self):
        """Test RadioGroup with custom gap."""
        from arepy_ui.components.radio import RadioGroup

        radio_group = RadioGroup(gap=24)

        assert radio_group.style.gap == 24

    def test_radiogroup_font_size(self):
        """Test RadioGroup with custom font size."""
        from arepy_ui.components.radio import RadioGroup

        radio_group = RadioGroup(font_size=18)

        assert radio_group.font_size == 18

    def test_radiooption_disabled(self):
        """Test RadioOption with disabled state."""
        from arepy_ui.components.radio import RadioOption

        option = RadioOption(label="Disabled", value="dis", disabled=True)

        assert option.disabled == True

    def test_radiogroup_handle_input(self):
        """Test RadioGroup input handling."""
        from arepy_ui.components.radio import RadioGroup, RadioOption

        options = [
            RadioOption(label="Option 1", value="opt1"),
            RadioOption(label="Option 2", value="opt2"),
        ]
        radio_group = RadioGroup(options=options)
        radio_group.computed_x = 0
        radio_group.computed_y = 0
        radio_group.computed_width = 200
        radio_group.computed_height = 100

        mock_mouse = MagicMock()
        mock_mouse.x = 50
        mock_mouse.y = 25

        result = radio_group.handle_input(mock_mouse, False)

        assert isinstance(result, bool)

    def test_radiogroup_render(self):
        """Test RadioGroup rendering."""
        from arepy_ui.components.radio import RadioGroup, RadioOption

        options = [
            RadioOption(label="Option 1", value="opt1"),
            RadioOption(label="Option 2", value="opt2"),
        ]
        radio_group = RadioGroup(options=options)
        radio_group.computed_x = 0
        radio_group.computed_y = 0
        radio_group.computed_width = 200
        radio_group.computed_height = 100

        # Should not raise
        radio_group.render()

    def test_radiogroup_animation_states(self):
        """Test RadioGroup animation states initialization."""
        from arepy_ui.components.radio import RadioGroup, RadioOption

        options = [
            RadioOption(label="Option 1", value="opt1"),
            RadioOption(label="Option 2", value="opt2"),
            RadioOption(label="Option 3", value="opt3"),
        ]
        radio_group = RadioGroup(options=options, selected_value="opt2")

        # Animation state for selected option should be 1.0
        assert radio_group._animation_states[1] == 1.0
        # Others should be 0.0
        assert radio_group._animation_states[0] == 0.0
        assert radio_group._animation_states[2] == 0.0

    def test_radiogroup_visual_config(self):
        """Test RadioGroup visual configuration."""
        from arepy_ui.components.radio import RadioGroup

        radio_group = RadioGroup()

        assert radio_group.radio_size == 18
        assert radio_group.radio_inner_size == 10
        assert radio_group.label_gap == 8
