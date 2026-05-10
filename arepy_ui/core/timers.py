from __future__ import annotations

from typing import Callable, TypeAlias

TimerCallback: TypeAlias = Callable[[], bool | None]


class Timer:
    """A scheduled callback managed by Timers."""

    def __init__(
        self,
        interval: float,
        callback: TimerCallback,
        repeat: bool = False,
    ) -> None:
        if interval < 0.0:
            raise ValueError("Timer interval must be >= 0.")

        self.interval = interval
        self.callback = callback
        self.repeat = repeat
        self.elapsed = 0.0
        self.active = True
        self.paused = False

    def cancel(self) -> None:
        self.active = False

    def pause(self) -> None:
        self.paused = True

    def resume(self) -> None:
        self.paused = False

    def restart(self) -> None:
        self.elapsed = 0.0
        self.active = True
        self.paused = False

    def update(self, dt: float) -> bool:
        if not self.active or self.paused:
            return self.active

        if self.interval == 0.0:
            keep_running = self.callback() is not False
            if self.repeat and keep_running:
                return True
            self.active = False
            return False

        self.elapsed += dt

        if not self.repeat:
            if self.elapsed < self.interval:
                return True
            self.active = False
            self.callback()
            return False

        while self.elapsed >= self.interval and self.active and not self.paused:
            self.elapsed -= self.interval
            if self.callback() is False:
                self.active = False

        return self.active


class Timers:
    """Scheduler for one-shot and repeating timers."""

    def __init__(self) -> None:
        self._timers: list[Timer] = []
        self._queued_timers: list[Timer] = []
        self._is_updating = False

    @property
    def timers(self) -> tuple[Timer, ...]:
        return tuple(self._timers + self._queued_timers)

    def __len__(self) -> int:
        return len(self._timers)

    def clear(self) -> None:
        for timer in self._timers:
            timer.cancel()
        for timer in self._queued_timers:
            timer.cancel()
        self._timers.clear()
        self._queued_timers.clear()

    def after(self, delay: float, callback: TimerCallback) -> Timer:
        timer = Timer(interval=delay, callback=callback, repeat=False)
        if self._is_updating:
            self._queued_timers.append(timer)
        else:
            self._timers.append(timer)
        return timer

    def every(self, interval: float, callback: TimerCallback) -> Timer:
        timer = Timer(interval=interval, callback=callback, repeat=True)
        if self._is_updating:
            self._queued_timers.append(timer)
        else:
            self._timers.append(timer)
        return timer

    def update(self, dt: float) -> None:
        if dt < 0.0:
            raise ValueError("Timers delta time must be >= 0.")

        active: list[Timer] = []
        self._is_updating = True
        try:
            for timer in self._timers:
                if timer.update(dt):
                    active.append(timer)
        finally:
            self._is_updating = False

        if self._queued_timers:
            active.extend(self._queued_timers)
            self._queued_timers.clear()

        self._timers = active
