"""Tests para arepy_ui.core.timers"""

from arepy_ui.core.timers import Timers


class TestTimers:
    def test_after_runs_once(self):
        events: list[str] = []
        timers = Timers()

        timers.after(0.2, lambda: events.append("done"))

        timers.update(0.1)
        assert events == []
        assert len(timers.timers) == 1

        timers.update(0.1)
        assert events == ["done"]
        assert len(timers.timers) == 0

    def test_every_repeats_until_callback_returns_false(self):
        events: list[int] = []
        timers = Timers()

        def on_tick() -> bool:
            events.append(len(events) + 1)
            return len(events) < 3

        timers.every(0.1, on_tick)
        timers.update(0.35)

        assert events == [1, 2, 3]
        assert len(timers.timers) == 0

    def test_timer_can_be_cancelled(self):
        events: list[str] = []
        timers = Timers()

        timer = timers.after(0.1, lambda: events.append("cancelled"))
        timer.cancel()
        timers.update(0.2)

        assert events == []
        assert len(timers.timers) == 0

    def test_timer_created_from_callback_is_kept(self):
        events: list[str] = []
        timers = Timers()

        def schedule_next() -> None:
            timers.after(0.1, lambda: events.append("nested"))

        timers.after(0.0, schedule_next)
        timers.update(0.0)

        assert len(timers.timers) == 1
        timers.update(0.1)
        assert events == ["nested"]
