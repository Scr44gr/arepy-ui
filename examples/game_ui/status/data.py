from __future__ import annotations

from dataclasses import dataclass


DAY_START_MINUTES = 6 * 60
NIGHT_START_MINUTES = 19 * 60
TOTAL_DAY_MINUTES = 24 * 60


@dataclass
class StatusState:
    total_minutes: float = float(6 * 60 + 40)
    gold: int = 2480
    minutes_per_second: float = 6.0

    def update(self, delta_seconds: float) -> None:
        self.total_minutes = (
            self.total_minutes + max(0.0, delta_seconds) * self.minutes_per_second
        ) % TOTAL_DAY_MINUTES

    @property
    def clock_minutes(self) -> int:
        return int(self.total_minutes) % TOTAL_DAY_MINUTES

    @property
    def hour(self) -> int:
        return self.clock_minutes // 60

    @property
    def minute(self) -> int:
        return self.clock_minutes % 60

    @property
    def hour_12(self) -> int:
        hour = self.hour % 12
        return 12 if hour == 0 else hour

    @property
    def period(self) -> str:
        return "AM" if self.hour < 12 else "PM"

    @property
    def is_day(self) -> bool:
        return DAY_START_MINUTES <= self.clock_minutes < NIGHT_START_MINUTES

    def formatted_time(self) -> str:
        return f"{self.hour_12:02d}:{self.minute:02d}"

    def formatted_gold(self) -> str:
        return f"{self.gold:,}".replace(",", ".")
