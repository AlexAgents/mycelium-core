"""
Тесты для VotingService — утилитные методы.
Не требует запущенного блокчейна.
"""
import pytest
from src.core.voting_service import VotingService


class TestHumanizeErrors:
    @pytest.fixture
    def svc(self):
        from unittest.mock import MagicMock
        provider = MagicMock()
        return VotingService(provider)

    def test_not_whitelisted(self, svc):
        msg = svc._humanize_contract_error("NotWhitelisted()")
        assert "whitelist" in msg.lower()

    def test_already_voted(self, svc):
        msg = svc._humanize_contract_error("AlreadyVoted()")
        assert "already voted" in msg.lower()

    def test_candidate_not_found(self, svc):
        msg = svc._humanize_contract_error("CandidateNotFound()")
        assert "not registered" in msg.lower()

    def test_invalid_stage(self, svc):
        msg = svc._humanize_contract_error("InvalidStage()")
        assert "stage" in msg.lower()

    def test_unauthorized(self, svc):
        msg = svc._humanize_contract_error("Unauthorized()")
        assert "owner" in msg.lower()

    def test_unknown_error(self, svc):
        msg = svc._humanize_contract_error("SomethingNew()")
        assert "SomethingNew" in msg


class TestReset:
    def test_reset_clears_state(self):
        from unittest.mock import MagicMock
        provider = MagicMock()
        svc = VotingService(provider)
        svc.contract = MagicMock()
        svc.contract_address = "0x123"
        svc.abi = [{"test": True}]
        svc.bytecode = "0xabcdef"

        svc.reset()

        assert svc.contract is None
        assert svc.contract_address is None
        assert svc.abi is None
        assert svc.bytecode is None


class TestRequireContract:
    def test_raises_without_contract(self):
        from unittest.mock import MagicMock
        provider = MagicMock()
        svc = VotingService(provider)
        with pytest.raises(RuntimeError, match="Contract not loaded"):
            svc._require_contract()