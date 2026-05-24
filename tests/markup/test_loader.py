"""Tests for markup loader caching behavior."""

from pathlib import Path
from unittest.mock import patch

from arepy_ui.markup.loader import (
    _AUI_FILE_CACHE,
    _AUI_STRING_CACHE,
    _INLINE_STYLESHEET_CACHE,
    _clear_load_caches,
    load_aui,
    load_aui_string,
)


class TestLoaderCaching:
    def setup_method(self):
        _clear_load_caches()

    def teardown_method(self):
        _clear_load_caches()

    @patch("arepy_ui.markup.loader._get_components", return_value={})
    @patch("arepy_ui.markup.loader.build_component", return_value=object())
    def test_load_aui_reuses_parsed_file_cache(
        self, _mock_build, _mock_components, tmp_path
    ):
        aui_path = tmp_path / "ui.aui"
        acss_path = tmp_path / "ui.acss"
        aui_path.write_text("<text>Hello</text>", encoding="utf-8")
        acss_path.write_text("text { color: #fff; }", encoding="utf-8")

        fake_root = object()
        fake_sheet = object()

        with (
            patch(
                "arepy_ui.markup.loader.parse_aui_file",
                return_value=(fake_root, []),
            ) as mock_parse_aui_file,
            patch(
                "arepy_ui.markup.loader.parse_acss_file",
                return_value=fake_sheet,
            ) as mock_parse_acss_file,
        ):
            first = load_aui(str(aui_path))
            second = load_aui(str(aui_path))

        assert first.root is not None
        assert second.root is not None
        assert mock_parse_aui_file.call_count == 1
        assert mock_parse_acss_file.call_count == 1

    @patch("arepy_ui.markup.loader._get_components", return_value={})
    @patch("arepy_ui.markup.loader.build_component", return_value=object())
    def test_load_aui_invalidates_cache_when_source_changes(
        self, _mock_build, _mock_components, tmp_path
    ):
        aui_path = tmp_path / "panel.aui"
        aui_path.write_text("<text>Hello</text>", encoding="utf-8")

        fake_root = object()

        with patch(
            "arepy_ui.markup.loader.parse_aui_file",
            return_value=(fake_root, []),
        ) as mock_parse_aui_file:
            load_aui(str(aui_path))
            aui_path.write_text("<text>Hello again</text>", encoding="utf-8")
            load_aui(str(aui_path))

        assert mock_parse_aui_file.call_count == 2

    def test_load_aui_string_reuses_inline_stylesheet_cache(self):
        with patch("arepy_ui.markup.loader.parse_aui", return_value=(object(), [])):
            with patch(
                "arepy_ui.markup.loader.parse_acss",
                side_effect=lambda content: {"content": content},
            ) as mock_parse_acss:
                with (
                    patch(
                        "arepy_ui.markup.loader.build_component",
                        return_value=object(),
                    ),
                    patch("arepy_ui.markup.loader._get_components", return_value={}),
                ):
                    load_aui_string("<text>Hello</text>", ".title { color: #fff; }")
                    load_aui_string("<text>Hello</text>", ".title { color: #fff; }")

        assert mock_parse_acss.call_count == 1

    def test_load_aui_string_reuses_parsed_aui_cache(self):
        with patch(
            "arepy_ui.markup.loader.parse_aui",
            return_value=(object(), []),
        ) as mock_parse_aui:
            with (
                patch(
                    "arepy_ui.markup.loader.build_component",
                    return_value=object(),
                ),
                patch("arepy_ui.markup.loader._get_components", return_value={}),
            ):
                load_aui_string("<text>Hello</text>")
                load_aui_string("<text>Hello</text>")

        assert mock_parse_aui.call_count == 1

    @patch("arepy_ui.markup.loader._get_components", return_value={})
    @patch("arepy_ui.markup.loader.build_component", return_value=object())
    def test_load_aui_file_cache_uses_lru_bound(
        self, _mock_build, _mock_components, tmp_path, monkeypatch
    ):
        monkeypatch.setattr("arepy_ui.markup.loader._MAX_AUI_FILE_CACHE_ENTRIES", 2)

        paths = []
        for index in range(3):
            path = tmp_path / f"{index}.aui"
            path.write_text("<text>Hello</text>", encoding="utf-8")
            paths.append(path)

        with patch(
            "arepy_ui.markup.loader.parse_aui_file",
            return_value=(object(), []),
        ):
            for path in paths:
                load_aui(str(path), stylesheet=None)

        assert len(_AUI_FILE_CACHE) == 2

    def test_inline_stylesheet_cache_uses_lru_bound(self, monkeypatch):
        monkeypatch.setattr(
            "arepy_ui.markup.loader._MAX_INLINE_STYLESHEET_CACHE_ENTRIES", 2
        )

        with patch("arepy_ui.markup.loader.parse_aui", return_value=(object(), [])):
            with patch(
                "arepy_ui.markup.loader.parse_acss",
                side_effect=lambda content: {"content": content},
            ):
                with (
                    patch(
                        "arepy_ui.markup.loader.build_component",
                        return_value=object(),
                    ),
                    patch("arepy_ui.markup.loader._get_components", return_value={}),
                ):
                    load_aui_string("<text>Hello</text>", ".a { color: #111; }")
                    load_aui_string("<text>Hello</text>", ".b { color: #222; }")
                    load_aui_string("<text>Hello</text>", ".c { color: #333; }")

        assert len(_INLINE_STYLESHEET_CACHE) == 2

    def test_aui_string_cache_uses_lru_bound(self, monkeypatch):
        monkeypatch.setattr("arepy_ui.markup.loader._MAX_AUI_STRING_CACHE_ENTRIES", 2)

        with patch("arepy_ui.markup.loader.parse_aui", return_value=(object(), [])):
            with (
                patch(
                    "arepy_ui.markup.loader.build_component",
                    return_value=object(),
                ),
                patch("arepy_ui.markup.loader._get_components", return_value={}),
            ):
                load_aui_string("<text>One</text>")
                load_aui_string("<text>Two</text>")
                load_aui_string("<text>Three</text>")

        assert len(_AUI_STRING_CACHE) == 2
