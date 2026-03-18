"""Benchmark the markup pipeline on a repeated synthetic tree."""

from __future__ import annotations

import importlib.util
import statistics
import sys
import time
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

for candidate in REPO_ROOT.glob("build/lib.*/arepy_ui/markup/parsers/css_parser*.pyd"):
    spec = importlib.util.spec_from_file_location(
        "arepy_ui.markup.parsers.css_parser", candidate
    )
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        sys.modules["arepy_ui.markup.parsers.css_parser"] = module
        spec.loader.exec_module(module)
        break

from arepy_ui.components.button import Button
from arepy_ui.components.scroll import ScrollView
from arepy_ui.components.text import Text
from arepy_ui.core.node import Node
from arepy_ui.core.fonts import TextMetrics
from arepy_ui.markup.builder import _clear_builder_caches
from arepy_ui.markup.globals import clear_globals
from arepy_ui.markup.loader import _clear_load_caches, load_aui, load_aui_string

COMPONENTS = {
    "Node": Node,
    "Text": Text,
    "Button": Button,
    "ScrollView": ScrollView,
}


def _write_fixture_files(tmp_dir: Path, item_count: int) -> tuple[Path, Path]:
    items = []
    for index in range(item_count):
        items.append(
            f'''<container class="card slot-{index % 3}">
    <text class="title">Item {index}</text>
    <button class="btn primary">Go</button>
</container>'''
        )

    aui_path = tmp_dir / "bench.aui"
    acss_path = tmp_dir / "bench.acss"
    aui_path.write_text(
        "<column class=\"layout\">\n" + "\n".join(items) + "\n</column>\n",
        encoding="utf-8",
    )
    acss_path.write_text(
        """
.layout { gap: 12px; padding: 24px; }
.card { width: 220px; height: 120px; padding: 16px; background: #20242a; border-radius: 12px; }
.slot-0 { margin: 4px; }
.slot-1 { margin: 8px; }
.slot-2 { margin: 12px; }
.title { font-size: 18px; color: #f4f4f4; }
.btn { width: 90px; height: 32px; color: #ffffff; background: #3355aa; border-radius: 6px; }
.primary { background: #4477ee; }
button:hover { background: #5f8fff; }
button:active { background: #244caa; }
""".strip()
        + "\n",
        encoding="utf-8",
    )
    return aui_path, acss_path


def _benchmark_load(aui_path: Path, rounds: int) -> tuple[float, float]:
    cold_timings = []
    hot_timings = []

    with patch("arepy_ui.markup.loader._get_components", return_value=COMPONENTS):
        with patch("arepy_ui.core.fonts.get_font_manager") as mock_font_manager:
            mock_font_manager.return_value.measure_text_ex.return_value = TextMetrics(
                100, 20, 24
            )

            for _ in range(rounds):
                clear_globals()
                _clear_builder_caches()
                _clear_load_caches()
                start = time.perf_counter()
                result = load_aui(str(aui_path))
                cold_timings.append(time.perf_counter() - start)
                if result.root is None:
                    raise RuntimeError("cold benchmark build failed")

            for _ in range(rounds):
                start = time.perf_counter()
                result = load_aui(str(aui_path))
                hot_timings.append(time.perf_counter() - start)
                if result.root is None:
                    raise RuntimeError("hot benchmark build failed")

    return statistics.mean(cold_timings), statistics.mean(hot_timings)


def _benchmark_load_string(aui_path: Path, acss_path: Path, rounds: int) -> tuple[float, float]:
    cold_timings = []
    hot_timings = []
    content = aui_path.read_text(encoding="utf-8")
    stylesheet = acss_path.read_text(encoding="utf-8")

    with patch("arepy_ui.markup.loader._get_components", return_value=COMPONENTS):
        with patch("arepy_ui.core.fonts.get_font_manager") as mock_font_manager:
            mock_font_manager.return_value.measure_text_ex.return_value = TextMetrics(
                100, 20, 24
            )

            for _ in range(rounds):
                clear_globals()
                _clear_builder_caches()
                _clear_load_caches()
                start = time.perf_counter()
                result = load_aui_string(content, stylesheet)
                cold_timings.append(time.perf_counter() - start)
                if result.root is None:
                    raise RuntimeError("cold string benchmark build failed")

            for _ in range(rounds):
                start = time.perf_counter()
                result = load_aui_string(content, stylesheet)
                hot_timings.append(time.perf_counter() - start)
                if result.root is None:
                    raise RuntimeError("hot string benchmark build failed")

    return statistics.mean(cold_timings), statistics.mean(hot_timings)


def main() -> None:
    item_count = 300
    rounds = 10
    tmp_dir = Path(__file__).resolve().parent / ".bench_tmp"
    tmp_dir.mkdir(exist_ok=True)
    aui_path, acss_path = _write_fixture_files(tmp_dir, item_count)

    cold_mean, hot_mean = _benchmark_load(aui_path, rounds)
    cold_string_mean, hot_string_mean = _benchmark_load_string(
        aui_path, acss_path, rounds
    )
    node_count = item_count * 3 + 1

    print(f"items: {item_count}")
    print(f"approx_nodes: {node_count}")
    print(f"rounds: {rounds}")
    print(f"file_cold_mean_ms: {cold_mean * 1000:.3f}")
    print(f"file_hot_mean_ms: {hot_mean * 1000:.3f}")
    print(f"file_speedup_x: {cold_mean / hot_mean:.2f}")
    print(f"string_cold_mean_ms: {cold_string_mean * 1000:.3f}")
    print(f"string_hot_mean_ms: {hot_string_mean * 1000:.3f}")
    print(f"string_speedup_x: {cold_string_mean / hot_string_mean:.2f}")


if __name__ == "__main__":
    main()
