"""
Pytest configuration and fixtures for arepy-ui tests.
"""

from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_runtime():
    """Mock del runtime de arepy para tests sin ventana gráfica."""
    with patch("arepy_ui.runtime.get_runtime") as mock:
        runtime = MagicMock()

        # Mock display
        runtime.display.get_window_size.return_value = (1280, 720)
        runtime.display.set_mouse_cursor = MagicMock()

        # Mock input
        runtime.input.get_mouse_position.return_value = (0, 0)
        runtime.input.is_mouse_button_pressed.return_value = False
        runtime.input.is_mouse_button_down.return_value = False
        runtime.input.is_mouse_button_released.return_value = False
        runtime.input.get_mouse_wheel_delta.return_value = 0.0

        # Mock renderer
        runtime.renderer.measure_text.return_value = 100
        runtime.renderer.draw_text = MagicMock()
        runtime.renderer.draw_rectangle = MagicMock()
        runtime.renderer.draw_rectangle_rounded = MagicMock()
        runtime.renderer.draw_rectangle_lines_ex = MagicMock()
        runtime.renderer.is_stencil_available.return_value = True

        mock.return_value = runtime
        yield runtime


@pytest.fixture
def mock_runtime_with_click(mock_runtime):
    """Mock del runtime con un click activo."""
    mock_runtime.input.is_mouse_button_pressed.return_value = True
    return mock_runtime


@pytest.fixture
def screen_size():
    """Tamaño de pantalla por defecto para tests."""
    return (1280, 720)
