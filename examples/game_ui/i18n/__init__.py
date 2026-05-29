from __future__ import annotations

from dataclasses import dataclass

from .catalog import TRANSLATIONS


@dataclass(frozen=True)
class Translator:
    locale: str = "es"
    fallback_locale: str = "en"

    def text(self, key: str, **kwargs: object) -> str:
        primary = TRANSLATIONS.get(self.locale, {})
        fallback = TRANSLATIONS.get(self.fallback_locale, {})
        template = primary.get(key, fallback.get(key, key))
        if not kwargs:
            return template
        return template.format(**kwargs)
