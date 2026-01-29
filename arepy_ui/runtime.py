"""
Runtime context for arepy-ui.
Holds references to arepy's Renderer2D, Input, Display, and AssetStore.
"""

from typing import Any, Optional

from arepy.asset_store.asset_store import AssetStore
from arepy.engine.audio import AudioDevice
from arepy.engine.display import Display
from arepy.engine.input import Input, Key, MouseButton
from arepy.engine.renderer.renderer_2d import Renderer2D


class _RuntimeContext:
    """Singleton context holding arepy runtime references."""

    _instance: Optional["_RuntimeContext"] = None

    def __init__(self):
        self._renderer: Optional[Renderer2D] = None
        self._input: Optional[Input] = None
        self._display: Optional[Display] = None
        self._asset_store: Optional[AssetStore] = None
        self._audio_device: Optional[AudioDevice] = None

    @classmethod
    def get_instance(cls) -> "_RuntimeContext":
        if cls._instance is None:
            cls._instance = _RuntimeContext()
        return cls._instance

    def configure(
        self,
        renderer: Renderer2D,
        input: Input,
        display: Display,
        asset_store: Optional[AssetStore] = None,
        audio_device: Optional[AudioDevice] = None,
    ) -> None:
        """Configure the runtime with arepy components."""
        self._renderer = renderer
        self._input = input
        self._display = display
        self._asset_store = asset_store
        self._audio_device = audio_device

    @property
    def renderer(self) -> Renderer2D:
        if self._renderer is None:
            raise RuntimeError(
                "arepy-ui not configured. Call configure_runtime() with Renderer2D, Input, and Display."
            )
        return self._renderer

    @property
    def input(self) -> Input:
        if self._input is None:
            raise RuntimeError(
                "arepy-ui not configured. Call configure_runtime() with Renderer2D, Input, and Display."
            )
        return self._input

    @property
    def display(self) -> Display:
        if self._display is None:
            raise RuntimeError(
                "arepy-ui not configured. Call configure_runtime() with Renderer2D, Input, and Display."
            )
        return self._display

    @property
    def asset_store(self) -> AssetStore:
        if self._asset_store is None:
            raise RuntimeError(
                "AssetStore not configured. Pass asset_store to configure_runtime()."
            )
        return self._asset_store

    @property
    def has_asset_store(self) -> bool:
        return self._asset_store is not None

    @property
    def audio_device(self) -> AudioDevice:
        if self._audio_device is None:
            raise RuntimeError(
                "AudioDevice not configured. Pass audio_device to configure_runtime()."
            )
        return self._audio_device

    @property
    def has_audio_device(self) -> bool:
        return self._audio_device is not None

    @property
    def is_configured(self) -> bool:
        return (
            self._renderer is not None
            and self._input is not None
            and self._display is not None
        )


def get_runtime() -> _RuntimeContext:
    """Get the runtime context instance."""
    return _RuntimeContext.get_instance()


def configure_runtime(
    renderer: Renderer2D,
    input: Input,
    display: Display,
    asset_store: Optional[AssetStore] = None,
    audio_device: Optional[AudioDevice] = None,
) -> None:
    """
    Configure arepy-ui with arepy components.

    Must be called before using any UI components.

    Args:
        renderer: Arepy's Renderer2D instance
        input: Arepy's Input instance
        display: Arepy's Display instance
        asset_store: Arepy's AssetStore instance (optional, required for Image component)
        audio_device: Arepy's AudioDevice instance (optional, required for Video audio)
    """
    get_runtime().configure(renderer, input, display, asset_store, audio_device)


# Mouse button constants (matching raylib/arepy values)
MOUSE_BUTTON_LEFT = MouseButton.LEFT
MOUSE_BUTTON_RIGHT = MouseButton.RIGHT
MOUSE_BUTTON_MIDDLE = MouseButton.MIDDLE

# Keyboard key constants
KEY_BACKSPACE = Key.BACKSPACE
KEY_ENTER = Key.ENTER
KEY_TAB = Key.TAB
KEY_DELETE = Key.DELETE
KEY_LEFT = Key.LEFT
KEY_RIGHT = Key.RIGHT
KEY_UP = Key.UP
KEY_DOWN = Key.DOWN
KEY_HOME = Key.HOME
KEY_END = Key.END

# Texture filter constants
TEXTURE_FILTER_BILINEAR = 1
