"""
Тесты утилит управления путями проекта.
"""
import pytest
from pathlib import Path

from src.utils.paths import (
    ROOT,
    DATA_DIR,
    BIN_DIR,
    CONTRACTS_DIR,
    ABI_DIR,
    SRC_DIR,
    CHAIN_ACTIVE,
    CHAIN_ARCHIVES,
    LOGS_ACTIVE,
    LOGS_ARCHIVE,
    SESSION_LOG,
    CONTRACT_SOL,
    CONTRACT_ABI,
    GETH_BIN,
    THEMES_DIR,
    I18N_DIR,
    APP_CFG,
    ensure_directories,
    get_archive_session_path,
    get_chain_archive_path,
)


class TestPathDefinitions:
    def test_root_contains_main_py(self):
        assert (ROOT / "main.py").exists()

    def test_contract_sol_exists(self):
        assert CONTRACT_SOL.exists()

    def test_i18n_dir_exists(self):
        assert I18N_DIR.exists()

    def test_themes_dir_exists(self):
        assert THEMES_DIR.exists()

    def test_src_dir_exists(self):
        assert SRC_DIR.exists()

    def test_contracts_dir_exists(self):
        assert CONTRACTS_DIR.exists()

    def test_app_cfg_path(self):
        assert APP_CFG.name == "app.cfg"
        assert APP_CFG.parent == ROOT


class TestPathRelationships:
    def test_data_dir_under_root(self):
        assert DATA_DIR.parent == ROOT

    def test_chain_active_under_chain(self):
        assert CHAIN_ACTIVE.parent.parent == DATA_DIR

    def test_logs_active_under_logs(self):
        assert LOGS_ACTIVE.parent.parent == DATA_DIR

    def test_session_log_under_logs_active(self):
        assert SESSION_LOG.parent == LOGS_ACTIVE

    def test_contract_abi_under_abi_dir(self):
        assert CONTRACT_ABI.parent == ABI_DIR

    def test_geth_bin_under_bin(self):
        assert GETH_BIN.parent == BIN_DIR


class TestPathFunctions:
    def test_ensure_directories_creates_dirs(self, tmp_path, monkeypatch):
        """ensure_directories не должна падать на существующих директориях."""
        # Просто проверяем что не падает
        ensure_directories()

    def test_get_archive_session_path(self):
        path = get_archive_session_path("abc-123")
        assert "abc-123" in str(path)
        assert path.parent == LOGS_ARCHIVE

    def test_get_chain_archive_path(self):
        path = get_chain_archive_path("20250718_120000")
        assert "old_20250718_120000" in path.name
        assert path.parent == CHAIN_ARCHIVES


class TestGethBin:
    def test_geth_extension(self):
        import platform
        if platform.system() == "Windows":
            assert GETH_BIN.suffix == ".exe"
        else:
            assert GETH_BIN.suffix == ""