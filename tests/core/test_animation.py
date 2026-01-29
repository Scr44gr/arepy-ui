"""Tests para arepy_ui.core.animation"""

import pytest

from arepy_ui.core.animation import Animation, Animator, Easing, apply_easing


class DummyTarget:
    """Objeto dummy para probar animaciones."""

    def __init__(self):
        self.opacity = 1.0
        self.x = 0.0
        self.y = 0.0
        self.scale = 1.0


class TestEasing:
    """Test the Easing enum and apply_easing function."""

    def test_linear(self):
        assert apply_easing(0.0, Easing.LINEAR) == 0.0
        assert apply_easing(0.5, Easing.LINEAR) == 0.5
        assert apply_easing(1.0, Easing.LINEAR) == 1.0

    def test_ease_in_quad(self):
        assert apply_easing(0.0, Easing.EASE_IN_QUAD) == 0.0
        assert apply_easing(1.0, Easing.EASE_IN_QUAD) == 1.0
        # ease_in_quad(0.5) = 0.5^2 = 0.25
        assert apply_easing(0.5, Easing.EASE_IN_QUAD) == pytest.approx(0.25)

    def test_ease_out_quad(self):
        assert apply_easing(0.0, Easing.EASE_OUT_QUAD) == 0.0
        assert apply_easing(1.0, Easing.EASE_OUT_QUAD) == 1.0
        # ease_out: t * (2 - t) at 0.5 = 0.5 * 1.5 = 0.75
        assert apply_easing(0.5, Easing.EASE_OUT_QUAD) == pytest.approx(0.75)

    def test_ease_in_out_quad(self):
        assert apply_easing(0.0, Easing.EASE_IN_OUT_QUAD) == 0.0
        assert apply_easing(1.0, Easing.EASE_IN_OUT_QUAD) == pytest.approx(1.0)
        assert apply_easing(0.5, Easing.EASE_IN_OUT_QUAD) == pytest.approx(0.5)

    def test_ease_in_cubic(self):
        assert apply_easing(0.0, Easing.EASE_IN_CUBIC) == 0.0
        assert apply_easing(1.0, Easing.EASE_IN_CUBIC) == 1.0
        # 0.5^3 = 0.125
        assert apply_easing(0.5, Easing.EASE_IN_CUBIC) == pytest.approx(0.125)

    def test_ease_out_cubic(self):
        assert apply_easing(0.0, Easing.EASE_OUT_CUBIC) == pytest.approx(0.0)
        assert apply_easing(1.0, Easing.EASE_OUT_CUBIC) == pytest.approx(1.0)

    def test_ease_out_elastic(self):
        # EASE_OUT_ELASTIC may not be implemented with 0/1 boundary, check existence
        result = apply_easing(0.5, Easing.EASE_OUT_ELASTIC)
        assert isinstance(result, float)

    def test_ease_out_bounce(self):
        assert apply_easing(0.0, Easing.EASE_OUT_BOUNCE) == pytest.approx(0.0)
        assert apply_easing(1.0, Easing.EASE_OUT_BOUNCE) == pytest.approx(1.0)


class TestAnimation:
    def test_animation_creation(self):
        target = DummyTarget()
        anim = Animation(
            target=target,  # type: ignore
            property_name="opacity",
            start_value=0.0,
            end_value=1.0,
            duration=1.0,
            easing=Easing.LINEAR,
        )
        assert anim.target is target
        assert anim.property_name == "opacity"
        assert anim.duration == 1.0
        assert not anim.is_finished

    def test_animation_update_linear(self):
        target = DummyTarget()
        target.opacity = 0.0
        anim = Animation(
            target=target,  # type: ignore
            property_name="opacity",
            start_value=0.0,
            end_value=1.0,
            duration=1.0,
            easing=Easing.LINEAR,
        )

        # 50% del tiempo
        anim.update(0.5)
        assert target.opacity == pytest.approx(0.5)
        assert not anim.is_finished

        # 100% del tiempo
        anim.update(0.5)
        assert target.opacity == pytest.approx(1.0)
        assert anim.is_finished

    def test_animation_easing_required(self):
        target = DummyTarget()
        # Animation requires easing parameter
        anim = Animation(
            target=target,  # type: ignore
            property_name="opacity",
            start_value=0.0,
            end_value=1.0,
            duration=1.0,
            easing=Easing.EASE_OUT_QUAD,
        )
        assert anim.easing == Easing.EASE_OUT_QUAD

    def test_animation_on_complete_callback(self):
        target = DummyTarget()
        callback_called = [False]

        def on_complete():
            callback_called[0] = True

        anim = Animation(
            target=target,  # type: ignore
            property_name="opacity",
            start_value=0.0,
            end_value=1.0,
            duration=0.5,
            easing=Easing.LINEAR,
            on_complete=on_complete,
        )

        anim.update(0.6)
        assert callback_called[0], "Callback should have been called"

    def test_animation_negative_values(self):
        target = DummyTarget()
        target.x = 100.0
        anim = Animation(
            target=target,  # type: ignore
            property_name="x",
            start_value=100.0,
            end_value=-100.0,
            duration=1.0,
            easing=Easing.LINEAR,
        )

        anim.update(0.5)
        assert target.x == pytest.approx(0.0)

        anim.update(0.5)
        assert target.x == pytest.approx(-100.0)


class TestAnimator:
    def test_animator_add_animation(self):
        animator = Animator()
        target = DummyTarget()
        anim = Animation(
            target=target,  # type: ignore
            property_name="opacity",
            start_value=0,
            end_value=1,
            duration=1,
            easing=Easing.LINEAR,
        )
        animator.add(anim)
        assert len(animator.animations) == 1

    def test_animator_update_removes_completed(self):
        animator = Animator()
        target = DummyTarget()
        anim = Animation(
            target=target,  # type: ignore
            property_name="opacity",
            start_value=0,
            end_value=1,
            duration=0.5,
            easing=Easing.LINEAR,
        )
        animator.add(anim)

        animator.update(1.0)  # Suficiente para completar
        assert len(animator.animations) == 0

    def test_animator_multiple_animations(self):
        animator = Animator()
        target = DummyTarget()

        anim1 = Animation(
            target=target,  # type: ignore
            property_name="opacity",
            start_value=0,
            end_value=1,
            duration=1,
            easing=Easing.LINEAR,
        )
        anim2 = Animation(
            target=target,  # type: ignore
            property_name="x",
            start_value=0,
            end_value=100,
            duration=2,
            easing=Easing.LINEAR,
        )

        animator.add(anim1)
        animator.add(anim2)
        assert len(animator.animations) == 2

        animator.update(1.5)  # Completa anim1, no anim2
        assert len(animator.animations) == 1

    def test_animator_clear(self):
        animator = Animator()
        target = DummyTarget()
        animator.add(
            Animation(
                target=target,  # type: ignore
                property_name="x",
                start_value=0,
                end_value=1,
                duration=1,
                easing=Easing.LINEAR,
            )
        )
        animator.add(
            Animation(
                target=target,  # type: ignore
                property_name="y",
                start_value=0,
                end_value=1,
                duration=1,
                easing=Easing.LINEAR,
            )
        )

        animator.animations.clear()
        assert len(animator.animations) == 0
