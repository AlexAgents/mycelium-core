"""
Тесты логики предварительной проверки перед голосованием.
Покрывает все 6 статусов PrecheckStatus без блокчейна.
"""
import pytest
from unittest.mock import MagicMock, patch, PropertyMock

from src.core.precheck import PrecheckResult, PrecheckStatus


class TestPrecheckResult:
    def test_ok_status(self):
        result = PrecheckResult(status=PrecheckStatus.OK, address="0x123", balance_wei=1000)
        assert result.is_ok
        assert result.status == PrecheckStatus.OK

    def test_invalid_key_status(self):
        result = PrecheckResult(status=PrecheckStatus.INVALID_KEY)
        assert not result.is_ok
        assert result.address == ""

    def test_not_whitelisted_status(self):
        result = PrecheckResult(
            status=PrecheckStatus.NOT_WHITELISTED,
            address="0xabc",
        )
        assert not result.is_ok

    def test_already_voted_status(self):
        result = PrecheckResult(
            status=PrecheckStatus.ALREADY_VOTED,
            address="0xabc",
        )
        assert not result.is_ok

    def test_insufficient_balance_status(self):
        result = PrecheckResult(
            status=PrecheckStatus.INSUFFICIENT_BALANCE,
            address="0xabc",
            balance_wei=100,
            required_wei=300_000_000_000_000,
        )
        assert not result.is_ok
        assert result.balance_wei < result.required_wei

    def test_no_contract_status(self):
        result = PrecheckResult(
            status=PrecheckStatus.NO_CONTRACT,
            address="0xabc",
        )
        assert not result.is_ok

    def test_unknown_error_status(self):
        result = PrecheckResult(
            status=PrecheckStatus.UNKNOWN_ERROR,
            address="0xabc",
            error_text="something went wrong",
        )
        assert not result.is_ok
        assert result.error_text == "something went wrong"

    def test_frozen_dataclass(self):
        result = PrecheckResult(status=PrecheckStatus.OK)
        with pytest.raises(AttributeError):
            result.status = PrecheckStatus.INVALID_KEY


class TestPrecheckEnum:
    def test_all_statuses_exist(self):
        expected = {
            "OK", "INVALID_KEY", "NOT_WHITELISTED",
            "ALREADY_VOTED", "INSUFFICIENT_BALANCE",
            "NO_CONTRACT", "UNKNOWN_ERROR",
        }
        actual = {s.name for s in PrecheckStatus}
        assert actual == expected

    def test_values_are_strings(self):
        for status in PrecheckStatus:
            assert isinstance(status.value, str)