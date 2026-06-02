"""
Тесты DTO статуса избирателя (VoterStatus).
Проверяет все поля, значения по умолчанию и неизменяемость.
"""
import pytest
from src.core.voter_status import VoterStatus


class TestVoterStatus:
    def test_valid_key_full_status(self):
        vs = VoterStatus(
            key_valid=True,
            address="0x1234567890abcdef1234567890abcdef12345678",
            is_whitelisted=True,
            has_voted=False,
            balance_eth="1.5000",
            stage_name="ACTIVE",
        )
        assert vs.key_valid is True
        assert vs.address.startswith("0x")
        assert vs.is_whitelisted is True
        assert vs.has_voted is False
        assert vs.balance_eth == "1.5000"
        assert vs.stage_name == "ACTIVE"
        assert vs.error is None

    def test_invalid_key(self):
        vs = VoterStatus(key_valid=False)
        assert vs.key_valid is False
        assert vs.address == ""
        assert vs.is_whitelisted is None
        assert vs.has_voted is None

    def test_invalid_key_with_error(self):
        vs = VoterStatus(
            key_valid=False,
            error="Invalid hex format",
        )
        assert vs.error == "Invalid hex format"

    def test_partial_status(self):
        """RPC-вызовы могут падать по отдельности — некоторые поля могут быть None."""
        vs = VoterStatus(
            key_valid=True,
            address="0xabc",
            is_whitelisted=True,
            has_voted=None,  # RPC failed
            balance_eth=None,  # RPC failed
            stage_name="SETUP",
        )
        assert vs.has_voted is None
        assert vs.balance_eth is None

    def test_frozen(self):
        vs = VoterStatus(key_valid=True)
        with pytest.raises(AttributeError):
            vs.key_valid = False

    def test_defaults(self):
        vs = VoterStatus(key_valid=True)
        assert vs.address == ""
        assert vs.is_whitelisted is None
        assert vs.has_voted is None
        assert vs.balance_eth is None
        assert vs.stage_name is None
        assert vs.error is None