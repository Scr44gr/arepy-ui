from __future__ import annotations


HUD_SCALE_FACTOR = 1.0
INVENTORY_SCALE_FACTOR = 1.35


def hud_px(value: float) -> int:
    return int(round(value * HUD_SCALE_FACTOR))

def inventory_px(value: float) -> int:
    return int(round(value * INVENTORY_SCALE_FACTOR))
