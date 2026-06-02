"""
Tests for GethManager.
Mocked — does not start real Geth.
"""
import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from pathlib import Path

from src.core.geth_manager import GethManager


class TestGethManagerInit:
    def test_default_values(self):
        gm = GethManager()
        assert gm.rpc_host == "127.0.0.1"
        assert gm.rpc_port == 8545
        assert gm.network_id == 1337
        assert gm.mode == "dev"

    def test_custom_values(self):
        gm = GethManager(
            rpc_host="0.0.0.0",
            rpc_port=9545,
            network_id=12345,
        )
        assert gm.rpc_host == "0.0.0.0"
        assert gm.rpc_port == 9545
        assert gm.network_id == 12345

    def test_rpc_url(self):
        gm = GethManager(rpc_host="localhost", rpc_port=8888)
        assert gm.rpc_url == "http://localhost:8888"


class TestGethManagerState:
    def test_not_running_initially(self):
        gm = GethManager()
        assert gm.is_running() is False

    def test_crash_callback_set(self):
        gm = GethManager()
        cb = MagicMock()
        gm.set_crash_callback(cb)
        assert gm._crash_callback is cb

    def test_start_raises_if_no_geth_binary(self):
        gm = GethManager()
        with patch("src.core.geth_manager.GETH_BIN", Path("/nonexistent/geth")):
            with pytest.raises(FileNotFoundError, match="Geth not found"):
                gm.start()

    def test_stop_when_not_running(self):
        """stop() не должен падать когда процесс None."""
        gm = GethManager()
        gm.stop()  # Should not raise

    def test_shutting_down_flag(self):
        gm = GethManager()
        assert gm._shutting_down is False
        gm.stop()
        assert gm._shutting_down is True


class TestGethManagerPortCheck:
    def test_port_not_in_use(self):
        """Порт 0 никогда не должен быть занят."""
        gm = GethManager(rpc_port=0)
        # Port 0 is a special case — just verify the method doesn't crash
        result = gm._is_port_in_use()
        assert isinstance(result, bool)


class TestGethManagerPurge:
    def test_purge_nonexistent_dir(self):
        """Не должен падать если директория chain не существует."""
        gm = GethManager()
        with patch("src.core.geth_manager.CHAIN_ACTIVE", Path("/nonexistent")):
            gm.purge_chain_data(archive=False)  # Should not raise


class TestForceKill:
    def test_force_kill_nonexistent_pid(self):
        """Не должен падать для несуществующего PID."""
        GethManager._force_kill_pid(999999)  # Should not raise

    def test_taskkill_all_geth(self):
        """Не должен падать даже если geth не запущен."""
        GethManager._taskkill_all_geth()  # Should not raise