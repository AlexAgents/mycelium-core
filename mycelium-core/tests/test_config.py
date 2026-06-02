"""
Тесты конфигурации: AppConfig и EnvConfig.
"""
import os
import pytest
from pathlib import Path
from unittest.mock import patch

from src.utils.config import AppConfig, EnvConfig, APP_VERSION


class TestAppConfig:
    def test_default_language(self):
        cfg = AppConfig()
        assert cfg.language in ("en", "ru")

    def test_default_theme(self):
        cfg = AppConfig()
        assert cfg.theme in ("dark", "light")

    def test_set_and_get(self):
        cfg = AppConfig()
        cfg.set("test_section", "test_key", "test_value")
        assert cfg.get("test_section", "test_key") == "test_value"

    def test_get_bool(self):
        cfg = AppConfig()
        cfg.set("test_section", "flag", "true")
        assert cfg.get_bool("test_section", "flag") is True
        cfg.set("test_section", "flag", "false")
        assert cfg.get_bool("test_section", "flag") is False

    def test_get_bool_fallback(self):
        cfg = AppConfig()
        result = cfg.get_bool("nonexistent", "key", fallback=True)
        assert result is True

    def test_get_int(self):
        cfg = AppConfig()
        cfg.set("test_section", "number", "42")
        assert cfg.get_int("test_section", "number") == 42

    def test_get_int_fallback(self):
        cfg = AppConfig()
        result = cfg.get_int("nonexistent", "key", fallback=99)
        assert result == 99

    def test_language_setter(self):
        cfg = AppConfig()
        cfg.language = "en"
        assert cfg.language == "en"
        cfg.language = "ru"
        assert cfg.language == "ru"

    def test_theme_setter(self):
        cfg = AppConfig()
        cfg.theme = "light"
        assert cfg.theme == "light"
        cfg.theme = "dark"
        assert cfg.theme == "dark"

    def test_preferred_session_mode(self):
        cfg = AppConfig()
        cfg.preferred_session_mode = "clean"
        assert cfg.preferred_session_mode == "clean"


class TestEnvConfig:
    def test_default_rpc_host(self):
        env = EnvConfig()
        assert env.rpc_host == os.getenv("RPC_HOST", "127.0.0.1")

    def test_default_rpc_port(self):
        env = EnvConfig()
        assert isinstance(env.rpc_port, int)

    def test_rpc_url_format(self):
        env = EnvConfig()
        assert env.rpc_url.startswith("http://")

    def test_default_network_id(self):
        env = EnvConfig()
        assert isinstance(env.network_id, int)

    def test_default_gas_price(self):
        env = EnvConfig()
        assert env.gas_price > 0

    def test_default_gas(self):
        env = EnvConfig()
        assert env.default_gas > 0

    def test_log_level(self):
        env = EnvConfig()
        assert env.log_level in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")

    def test_solidity_version(self):
        env = EnvConfig()
        assert env.solidity_version.startswith("0.8")

    def test_dev_admin_key_none_in_production(self):
        """В не-dev режиме admin key должен быть None."""
        with patch.dict(os.environ, {"DEV_MODE": "false"}, clear=False):
            env = EnvConfig()
            assert env.dev_admin_key is None

    def test_gas_limit(self):
        env = EnvConfig()
        assert env.gas_limit > 0