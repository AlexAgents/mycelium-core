"""
Тесты для NonceManager: потокобезопасность и корректность поведения.
"""
import pytest
import threading
from unittest.mock import MagicMock, patch

from src.core.nonce_manager import NonceManager


@pytest.fixture
def mock_w3():
    w3 = MagicMock()
    w3.eth.get_transaction_count.return_value = 0
    return w3


class TestNonceManager:
    def test_first_call_fetches_from_network(self, mock_w3):
        mock_w3.eth.get_transaction_count.return_value = 5
        nm = NonceManager(mock_w3, "0x0000000000000000000000000000000000000001")
        nonce = nm.get_next_nonce()
        assert nonce == 5
        mock_w3.eth.get_transaction_count.assert_called_once()

    def test_subsequent_calls_increment(self, mock_w3):
        mock_w3.eth.get_transaction_count.return_value = 10
        nm = NonceManager(mock_w3, "0x0000000000000000000000000000000000000001")
        n1 = nm.get_next_nonce()
        n2 = nm.get_next_nonce()
        n3 = nm.get_next_nonce()
        assert n1 == 10
        assert n2 == 11
        assert n3 == 12
        # Только один сетевой вызов
        assert mock_w3.eth.get_transaction_count.call_count == 1

    def test_sync_re_fetches(self, mock_w3):
        mock_w3.eth.get_transaction_count.return_value = 5
        nm = NonceManager(mock_w3,
                          "0x0000000000000000000000000000000000000001")
        assert nm.get_next_nonce() == 5
        assert nm.get_next_nonce() == 6
        # Сеть теперь говорит: следующий pending nonce = 20
        mock_w3.eth.get_transaction_count.return_value = 20
        nm.sync()
        # После sync get_next_nonce() должен вернуть РОВНО 20,
        # не 21 — иначе пропустим pending nonce и получим "nonce too low".
        assert nm.get_next_nonce() == 20
        assert nm.get_next_nonce() == 21
        
    def test_reset_clears(self, mock_w3):
        mock_w3.eth.get_transaction_count.return_value = 5
        nm = NonceManager(mock_w3, "0x0000000000000000000000000000000000000001")
        nm.get_next_nonce()
        nm.reset()

        mock_w3.eth.get_transaction_count.return_value = 100
        n = nm.get_next_nonce()
        assert n == 100

    def test_thread_safety(self, mock_w3):
        mock_w3.eth.get_transaction_count.return_value = 0
        nm = NonceManager(mock_w3, "0x0000000000000000000000000000000000000001")

        results = []
        errors = []

        def get_nonces(count):
            try:
                for _ in range(count):
                    results.append(nm.get_next_nonce())
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=get_nonces, args=(50,))
            for _ in range(4)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(results) == 200
        # Все nonce должны быть уникальными
        assert len(set(results)) == 200