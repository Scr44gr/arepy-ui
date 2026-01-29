"""Tests para arepy_ui.config"""

import pytest

from arepy_ui.config import (
    ResizeMode,
    ScaleAnchor,
    ScaleTransform,
    UIConfig,
    calculate_scale_transform,
)


class TestUIConfig:
    def test_config_defaults(self):
        config = UIConfig()

        assert config.resize_mode == ResizeMode.RESPONSIVE
        assert config.scale_anchor == ScaleAnchor.CENTER
        assert config.min_scale == 0.5
        assert config.max_scale == 2.0
        assert config.layout_debounce_ms == 0.0

    def test_config_with_reference_size(self):
        config = UIConfig(
            reference_width=1920,
            reference_height=1080,
        )

        assert config.reference_width == 1920
        assert config.reference_height == 1080

    def test_config_scale_fit(self):
        config = UIConfig(resize_mode=ResizeMode.SCALE_FIT)

        assert config.resize_mode == ResizeMode.SCALE_FIT

    def test_config_with_callbacks(self):
        called = [False]

        def on_resize(w, h):
            called[0] = True

        config = UIConfig(on_resize=on_resize)

        assert config.on_resize is not None


class TestScaleTransform:
    def test_scale_transform_defaults(self):
        transform = ScaleTransform()

        assert transform.scale_x == 1.0
        assert transform.scale_y == 1.0
        assert transform.offset_x == 0.0
        assert transform.offset_y == 0.0

    def test_uniform_scale(self):
        transform = ScaleTransform(scale_x=2.0, scale_y=1.5)

        assert transform.uniform_scale == 1.5  # min of the two

    def test_apply_to_point(self):
        transform = ScaleTransform(
            scale_x=2.0,
            scale_y=2.0,
            offset_x=100,
            offset_y=50,
        )

        x, y = transform.apply_to_point(10, 20)

        assert x == 10 * 2.0 + 100  # 120
        assert y == 20 * 2.0 + 50  # 90

    def test_inverse_point(self):
        transform = ScaleTransform(
            scale_x=2.0,
            scale_y=2.0,
            offset_x=100,
            offset_y=50,
        )

        # Punto en pantalla
        screen_x, screen_y = 120, 90

        # Convertir a coordenadas UI
        ui_x, ui_y = transform.inverse_point(screen_x, screen_y)

        assert ui_x == pytest.approx(10)
        assert ui_y == pytest.approx(20)

    def test_inverse_then_apply_is_identity(self):
        transform = ScaleTransform(
            scale_x=1.5,
            scale_y=0.8,
            offset_x=200,
            offset_y=100,
        )

        original_x, original_y = 50, 75

        # Apply then inverse
        screen_x, screen_y = transform.apply_to_point(original_x, original_y)
        back_x, back_y = transform.inverse_point(screen_x, screen_y)

        assert back_x == pytest.approx(original_x)
        assert back_y == pytest.approx(original_y)


class TestCalculateScaleTransform:
    def test_responsive_no_scale(self):
        config = UIConfig(resize_mode=ResizeMode.RESPONSIVE)

        transform = calculate_scale_transform(
            config,
            reference_width=1280,
            reference_height=720,
            current_width=1920,
            current_height=1080,
        )

        # Responsive no aplica escala
        assert transform.scale_x == 1.0
        assert transform.scale_y == 1.0

    def test_scale_fit_smaller_window(self):
        config = UIConfig(resize_mode=ResizeMode.SCALE_FIT)

        transform = calculate_scale_transform(
            config,
            reference_width=1280,
            reference_height=720,
            current_width=640,
            current_height=360,
        )

        # Debería escalar a 0.5
        assert transform.scale_x == pytest.approx(0.5)
        assert transform.scale_y == pytest.approx(0.5)

    def test_scale_fit_larger_window(self):
        config = UIConfig(resize_mode=ResizeMode.SCALE_FIT)

        transform = calculate_scale_transform(
            config,
            reference_width=1280,
            reference_height=720,
            current_width=2560,
            current_height=1440,
        )

        # Debería escalar a 2.0
        assert transform.scale_x == pytest.approx(2.0)
        assert transform.scale_y == pytest.approx(2.0)
