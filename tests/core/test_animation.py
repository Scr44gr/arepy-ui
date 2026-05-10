"""Tests para arepy_ui.core.animation"""

import pytest

from arepy_ui.core.animation import Animation, Animator, Easing, apply_easing
from arepy_ui.core.style import Spacing, Style
from arepy_ui.core.types import Color, Unit, Vector2


class DummyTarget:
    """Objeto dummy para probar secuencias de animacion."""

    def __init__(self):
        self.opacity = 1.0
        self.x = 0.0
        self.y = 0.0
        self.color = Color(0, 0, 0, 0)
        self.position = Vector2(0, 0)
        self.style = Style(margin=Spacing.all(0))


class TestEasing:
    def test_linear(self):
        assert apply_easing(0.0, Easing.LINEAR) == 0.0
        assert apply_easing(0.5, Easing.LINEAR) == 0.5
        assert apply_easing(1.0, Easing.LINEAR) == 1.0

    def test_ease_in_quad(self):
        assert apply_easing(0.0, Easing.EASE_IN_QUAD) == 0.0
        assert apply_easing(1.0, Easing.EASE_IN_QUAD) == 1.0
        assert apply_easing(0.5, Easing.EASE_IN_QUAD) == pytest.approx(0.25)

    def test_ease_out_quad(self):
        assert apply_easing(0.0, Easing.EASE_OUT_QUAD) == 0.0
        assert apply_easing(1.0, Easing.EASE_OUT_QUAD) == 1.0
        assert apply_easing(0.5, Easing.EASE_OUT_QUAD) == pytest.approx(0.75)

    def test_ease_in_out_quad(self):
        assert apply_easing(0.0, Easing.EASE_IN_OUT_QUAD) == 0.0
        assert apply_easing(1.0, Easing.EASE_IN_OUT_QUAD) == pytest.approx(1.0)
        assert apply_easing(0.5, Easing.EASE_IN_OUT_QUAD) == pytest.approx(0.5)

    def test_ease_in_cubic(self):
        assert apply_easing(0.0, Easing.EASE_IN_CUBIC) == 0.0
        assert apply_easing(1.0, Easing.EASE_IN_CUBIC) == 1.0
        assert apply_easing(0.5, Easing.EASE_IN_CUBIC) == pytest.approx(0.125)

    def test_ease_out_cubic(self):
        assert apply_easing(0.0, Easing.EASE_OUT_CUBIC) == pytest.approx(0.0)
        assert apply_easing(1.0, Easing.EASE_OUT_CUBIC) == pytest.approx(1.0)

    def test_ease_out_elastic(self):
        result = apply_easing(0.5, Easing.EASE_OUT_ELASTIC)
        assert isinstance(result, float)

    def test_ease_out_bounce(self):
        assert apply_easing(0.0, Easing.EASE_OUT_BOUNCE) == pytest.approx(0.0)
        assert apply_easing(1.0, Easing.EASE_OUT_BOUNCE) == pytest.approx(1.0)


class TestAnimation:
    def test_animation_requires_animator_binding(self):
        animation = Animation()

        with pytest.raises(RuntimeError):
            animation.start()

    def test_animation_sequence_waits_and_calls(self):
        animator = Animator()
        target = DummyTarget()
        target.opacity = 0.0
        callbacks: list[str] = []

        animator.create().wait(0.25).to(
            target,
            "opacity",
            1.0,
            0.5,
            Easing.LINEAR,
        ).call(lambda: callbacks.append("done")).start()

        animator.update(0.2)
        assert target.opacity == pytest.approx(0.0)
        assert callbacks == []

        animator.update(0.3)
        assert target.opacity == pytest.approx(0.5)
        assert callbacks == []

        animator.update(0.25)
        assert target.opacity == pytest.approx(1.0)
        assert callbacks == ["done"]
        assert len(animator.animations) == 0

    def test_animation_supports_custom_easing_callable(self):
        animator = Animator()
        target = DummyTarget()

        animator.create().to(
            target,
            "x",
            10.0,
            1.0,
            lambda progress: progress * progress,
        ).start()

        animator.update(0.5)
        assert target.x == pytest.approx(2.5)

    def test_animation_interpolates_vector_and_color_properties(self):
        animator = Animator()
        target = DummyTarget()

        animator.create().to(
            target,
            "position",
            Vector2(10, 20),
            1.0,
            Easing.LINEAR,
        ).start()
        animator.create().to(
            target,
            "color",
            Color(100, 150, 200, 255),
            1.0,
            Easing.LINEAR,
        ).start()

        animator.update(0.5)

        assert target.position.x == pytest.approx(5.0)
        assert target.position.y == pytest.approx(10.0)
        assert target.color.r == 50
        assert target.color.g == 75
        assert target.color.b == 100
        assert target.color.a in {127, 128}

    def test_animation_interpolates_nested_unit_property(self):
        animator = Animator()
        target = DummyTarget()

        animator.create().to(
            target,
            "style.margin.left",
            100.0,
            1.0,
            Easing.LINEAR,
        ).start()

        animator.update(0.5)

        assert isinstance(target.style.margin.left, Unit)
        assert target.style.margin.left.value == pytest.approx(50.0)
        assert target.style.margin.left.type == Unit.px(0).type

    def test_animation_cannot_be_modified_after_start(self):
        animator = Animator()
        animation = animator.create().to(object(), "__class__", object, 0.0)
        animation.start()

        with pytest.raises(RuntimeError):
            animation.wait(0.1)


class TestAnimator:
    def test_animator_clear_cancels_active_sequences(self):
        animator = Animator()
        target = DummyTarget()

        animator.create().to(target, "x", 100.0, 1.0, Easing.LINEAR).start()
        animator.create().to(target, "y", 50.0, 1.0, Easing.LINEAR).start()

        assert len(animator.animations) == 2

        animator.clear()

        assert len(animator.animations) == 0

    def test_animator_keeps_new_sequences_started_from_callbacks(self):
        animator = Animator()
        target = DummyTarget()

        animator.create().call(
            lambda: animator.create()
            .to(
                target,
                "y",
                20.0,
                1.0,
                Easing.LINEAR,
            )
            .start()
        ).start()

        animator.update(0.0)
        assert len(animator.animations) == 1

        animator.update(0.5)
        assert target.y == pytest.approx(10.0)
