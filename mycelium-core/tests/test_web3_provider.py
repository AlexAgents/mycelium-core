"""
Тесты для Web3Provider.
Мокированные — не требуют запущенного Geth.
"""
import pytest
from unittest.mock import MagicMock, patch, PropertyMock

from src.core.web3_provider import Web3Provider


class TestWeb3ProviderInit:
    def test_initial_state(self):
        provider = Web3Provider("http://127.0.0.1:8545")
        assert provider.rpc_url == "http://127.0.0.1:8545"
        assert provider._w3 is None

    def test_not_connected_initially(self):
        provider = Web3Provider("http://127.0.0.1:8545")
        assert provider.is_connected() is False

    def test_ping_before_connect(self):
        provider = Web3Provider("http://127.0.0.1:8545")
        assert provider.ping() is False

    def test_client_version_before_connect(self):
        provider = Web3Provider("http://127.0.0.1:8545")
        assert provider.client_version() == "unknown"


class TestWeb3ProviderAccess:
    def test_w3_property_raises_if_not_connected(self):
        provider = Web3Provider("http://127.0.0.1:8545")
        with pytest.raises(RuntimeError, match="not connected"):
            _ = provider.w3

    def test_get_block_number_returns_none_if_disconnected(self):
        provider = Web3Provider("http://127.0.0.1:8545")
        # _w3 = None, get_block_number должен обработать корректно
        assert provider.get_block_number() is None

    def test_get_accounts_returns_empty_if_disconnected(self):
        provider = Web3Provider("http://127.0.0.1:8545")
        # Попытается получить доступ к w3, должен вернуть []
        assert provider.get_accounts() == []

    def test_get_balance_returns_zero_if_disconnected(self):
        provider = Web3Provider("http://127.0.0.1:8545")
        assert provider.get_balance("0x" + "0" * 40) == 0


class TestWeb3ProviderWithMock:
    @pytest.fixture
    def connected_provider(self):
        provider = Web3Provider("http://127.0.0.1:8545")
        mock_w3 = MagicMock()
        mock_w3.is_connected.return_value = True
        mock_w3.eth.block_number = 42
        mock_w3.eth.chain_id = 1337
        mock_w3.eth.accounts = ["0x" + "a" * 40]
        mock_w3.eth.get_balance.return_value = 10**18
        mock_w3.client_version = "Geth/v1.13.0-test"
        provider._w3 = mock_w3
        return provider

    def test_is_connected(self, connected_provider):
        assert connected_provider.is_connected() is True

    def test_ping(self, connected_provider):
        assert connected_provider.ping() is True

    def test_get_block_number(self, connected_provider):
        assert connected_provider.get_block_number() == 42

    def test_get_chain_id(self, connected_provider):
        assert connected_provider.get_chain_id() == 1337

    def test_get_accounts(self, connected_provider):
        accounts = connected_provider.get_accounts()
        assert len(accounts) == 1
        assert accounts[0] == "0x" + "a" * 40

    def test_get_balance(self, connected_provider):
        bal = connected_provider.get_balance("0x" + "0" * 40)
        assert bal == 10**18

    def test_client_version(self, connected_provider):
        ver = connected_provider.client_version()
        assert "Geth" in ver

    def test_validate_abi_hash_empty(self, connected_provider):
        """Пустой ожидаемый хэш всегда проходит проверку."""
        assert connected_provider.validate_abi_hash([], "") is True

    def test_validate_abi_hash_match(self, connected_provider):
        import hashlib, json
        abi = [{"name": "test"}]
        abi_json = json.dumps(abi, sort_keys=True, separators=(",", ":"))
        expected = hashlib.sha256(abi_json.encode()).hexdigest()
        assert connected_provider.validate_abi_hash(abi, expected) is True

    def test_validate_abi_hash_mismatch(self, connected_provider):
        abi = [{"name": "test"}]
        assert connected_provider.validate_abi_hash(abi, "wrong_hash") is False