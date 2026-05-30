"""
Setup script for building Cython extensions.
This is called automatically by setuptools during pip install.
"""

import os

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext as setuptools_build_ext

# Check if Cython is available
try:
    from Cython.Build import cythonize

    USE_CYTHON = True
except ImportError:
    USE_CYTHON = False


class build_ext(setuptools_build_ext):
    def finalize_options(self):
        super().finalize_options()
        if self.editable_mode and self._uses_strict_editable_mode():
            self.inplace = False

    def _uses_strict_editable_mode(self):
        editable_wheel = self.distribution.get_command_obj("editable_wheel")
        mode = getattr(editable_wheel, "mode", None)
        return str(mode).lower() == "strict"


def get_extensions():
    """Get list of Cython extensions to build."""
    if not USE_CYTHON:
        return []

    parsers_dir = os.path.join("arepy_ui", "markup", "parsers")
    core_dir = os.path.join("arepy_ui", "core")
    colorpicker_dir = os.path.join("arepy_ui", "components", "colorpicker")

    extensions = [
        # Markup parsers
        Extension(
            "arepy_ui.markup.parsers.css_parser",
            [os.path.join(parsers_dir, "css_parser.pyx")],
            language="c",
        ),
        Extension(
            "arepy_ui.markup.parsers.aui_parser",
            [os.path.join(parsers_dir, "aui_parser.pyx")],
            language="c",
        ),
        # Core types and layout
        Extension(
            "arepy_ui.core.types",
            [os.path.join(core_dir, "types.pyx")],
            language="c",
        ),
        Extension(
            "arepy_ui.core.easing",
            [os.path.join(core_dir, "easing.pyx")],
            language="c",
        ),
        Extension(
            "arepy_ui.core.layout",
            [os.path.join(core_dir, "layout.pyx")],
            language="c",
        ),
        # ColorPicker HSV operations
        Extension(
            "arepy_ui.components.colorpicker._hsv",
            [os.path.join(colorpicker_dir, "_hsv.pyx")],
            language="c",
        ),
    ]

    return cythonize(
        extensions,
        compiler_directives={
            "language_level": 3,
            "boundscheck": False,
            "wraparound": False,
        },
        quiet=True,
    )


# Only run setup if called directly or during build
if __name__ == "__main__":
    setup(
        ext_modules=get_extensions(),
        cmdclass={"build_ext": build_ext},
    )
