"""
Тесты для системы i18n.

Покрывает:
- Симметрия ключей между ru.json и en.json
- Корректная работа подстановки
- Сигнал languageChanged эмитится при смене языка
"""
import json
from pathlib import Path

import pytest

from src.utils.i18n import I18N
from src.utils.paths import I18N_DIR


def _load(name: str) -> dict:
    return json.loads(
        (I18N_DIR / f"{name}.json").read_text(encoding="utf-8")
    )


class TestSymmetry:
    def test_ru_en_have_same_keys(self):
        ru = set(_load("ru").keys())
        en = set(_load("en").keys())

        missing_in_en = ru - en
        missing_in_ru = en - ru

        assert not missing_in_en, (
            f"Keys present in ru.json but missing in en.json: "
            f"{sorted(missing_in_en)}"
        )
        assert not missing_in_ru, (
            f"Keys present in en.json but missing in ru.json: "
            f"{sorted(missing_in_ru)}"
        )

    def test_no_empty_values(self):
        for lang in ("ru", "en"):
            data = _load(lang)
            empty = [k for k, v in data.items() if not v]
            assert not empty, (
                f"Empty translation values in {lang}.json: {empty}"
            )


class TestI18NRuntime:
    def test_load_ru(self):
        i18n = I18N("ru")
        assert i18n.language == "ru"
        assert i18n.t("common.ok") == "OK"

    def test_load_en(self):
        i18n = I18N("en")
        assert i18n.language == "en"
        assert i18n.t("common.cancel") == "Cancel"

    def test_unknown_key_returns_key(self):
        i18n = I18N("ru")
        assert i18n.t("nonexistent.key.here") == "nonexistent.key.here"

    def test_format_substitution(self):
        i18n = I18N("ru")
        result = i18n.t("admin.toast.voters_generated", count=42)
        assert "42" in result

    def test_signal_emitted_on_switch(self):
        i18n = I18N("ru")
        received = []
        i18n.languageChanged.connect(lambda lang: received.append(lang))

        i18n.load("en")
        assert received == ["en"]

        # Повторная загрузка того же языка не эмитит сигнал
        i18n.load("en")
        assert received == ["en"]

    def test_no_signal_on_same_language(self):
        i18n = I18N("ru")
        received = []
        i18n.languageChanged.connect(lambda lang: received.append(lang))

        i18n.load("ru")  # тот же язык
        assert received == []