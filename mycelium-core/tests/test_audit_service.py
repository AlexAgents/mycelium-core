"""
Тесты для AuditService.
Покрывает: staged audit, методы проверок, построение результатов.
"""
import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch, PropertyMock

from src.core.audit_service import AuditService
from src.core.models import (
    AuditCheck,
    AuditReport,
    Candidate,
    ElectionStage,
)


# Валидные тестовые адреса (40 hex-символов)
ADDR_1 = "0x0000000000000000000000000000000000000001"
ADDR_2 = "0x0000000000000000000000000000000000000002"
ADDR_3 = "0x0000000000000000000000000000000000000003"
ADDR_A = "0x000000000000000000000000000000000000000a"
ADDR_B = "0x000000000000000000000000000000000000000b"
ADDR_VOTER_1 = "0x0000000000000000000000000000000000000111"


@pytest.fixture
def mock_voting_service():
    svc = MagicMock()
    svc.contract = MagicMock()
    svc.provider = MagicMock()
    svc.provider.w3.eth.block_number = 100
    return svc


@pytest.fixture
def audit_service(mock_voting_service):
    return AuditService(mock_voting_service)


class TestBuildResults:
    def test_empty_candidates(self, audit_service, mock_voting_service):
        mock_voting_service.get_candidates.return_value = []
        results = audit_service.build_results()
        assert results == []

    def test_sorted_by_votes(self, audit_service, mock_voting_service):
        mock_voting_service.get_candidates.return_value = [
            Candidate(name="A", party="P1", address=ADDR_1, vote_count=3),
            Candidate(name="B", party="P2", address=ADDR_2, vote_count=7),
            Candidate(name="C", party="P3", address=ADDR_3, vote_count=1),
        ]
        results = audit_service.build_results()
        assert results[0].name == "B"
        assert results[1].name == "A"
        assert results[2].name == "C"


class TestDetectWinner:
    def test_no_candidates(self, audit_service, mock_voting_service):
        mock_voting_service.get_candidates.return_value = []
        winner = audit_service.detect_winner()
        assert winner is None

    def test_clear_winner(self, audit_service, mock_voting_service):
        mock_voting_service.get_candidates.return_value = [
            Candidate(name="A", party="P1", address=ADDR_1, vote_count=10),
            Candidate(name="B", party="P2", address=ADDR_2, vote_count=5),
        ]
        winner = audit_service.detect_winner()
        assert winner["type"] == "winner"
        assert winner["candidate"].name == "A"

    def test_tie(self, audit_service, mock_voting_service):
        mock_voting_service.get_candidates.return_value = [
            Candidate(name="A", party="P1", address=ADDR_1, vote_count=5),
            Candidate(name="B", party="P2", address=ADDR_2, vote_count=5),
        ]
        winner = audit_service.detect_winner()
        assert winner["type"] == "tie"
        assert len(winner["candidates"]) == 2


class TestPreVoteChecks:
    def test_candidate_count_pass(self, audit_service, mock_voting_service):
        mock_voting_service.get_candidates.return_value = [
            Candidate(name="A", party="P1", address=ADDR_1),
            Candidate(name="B", party="P2", address=ADDR_2),
        ]
        check = audit_service._check_candidate_count()
        assert check.status == "PASSED"

    def test_candidate_count_fail(self, audit_service, mock_voting_service):
        mock_voting_service.get_candidates.return_value = [
            Candidate(name="A", party="P1", address=ADDR_1),
        ]
        check = audit_service._check_candidate_count()
        assert check.status == "FAILED"

    def test_whitelist_populated_empty(self, audit_service, mock_voting_service):
        mock_voting_service.contract.functions.getVoterAddresses.return_value.call.return_value = []
        check = audit_service._check_whitelist_populated()
        assert check.status == "WARNING"

    def test_whitelist_populated_ok(self, audit_service, mock_voting_service):
        mock_voting_service.contract.functions.getVoterAddresses.return_value.call.return_value = [
            ADDR_VOTER_1,
        ]
        check = audit_service._check_whitelist_populated()
        assert check.status == "PASSED"


class TestDoubleVoteCheck:
    def test_no_duplicates(self, audit_service):
        events = [
            {"args": {"voter": ADDR_1, "candidate": ADDR_A}},
            {"args": {"voter": ADDR_2, "candidate": ADDR_B}},
        ]
        check = audit_service._check_double_vote(events)
        assert check.status == "PASSED"

    def test_with_duplicates(self, audit_service):
        events = [
            {"args": {"voter": ADDR_1, "candidate": ADDR_A}},
            {"args": {"voter": ADDR_1, "candidate": ADDR_B}},
        ]
        check = audit_service._check_double_vote(events)
        assert check.status == "FAILED"
        assert ADDR_1 in check.details


class TestVoteCountIntegrity:
    def test_matching(self, audit_service, mock_voting_service):
        events = [
            {"args": {"voter": ADDR_1, "candidate": ADDR_A}},
            {"args": {"voter": ADDR_2, "candidate": ADDR_A}},
        ]
        mock_voting_service.get_candidates.return_value = [
            Candidate(
                name="A", party="P", address=ADDR_A,
                vote_count=2,
            ),
        ]
        check = audit_service._check_vote_count_integrity(events)
        assert check.status == "PASSED"

    def test_mismatch(self, audit_service, mock_voting_service):
        events = [
            {"args": {"voter": ADDR_1, "candidate": ADDR_A}},
        ]
        mock_voting_service.get_candidates.return_value = [
            Candidate(
                name="A", party="P", address=ADDR_A,
                vote_count=5,
            ),
        ]
        check = audit_service._check_vote_count_integrity(events)
        assert check.status == "FAILED"


class TestStagedAudit:
    def test_pre_vote_has_skipped(self, audit_service, mock_voting_service):
        mock_voting_service.get_candidates.return_value = [
            Candidate(name="A", party="P1", address=ADDR_1),
            Candidate(name="B", party="P2", address=ADDR_2),
        ]
        mock_voting_service.contract.functions.getVoterAddresses.return_value.call.return_value = [ADDR_VOTER_1]
        mock_voting_service.get_stage.return_value = ElectionStage.SETUP
        report = audit_service.run_pre_vote_audit("test-session", 0)
        statuses = {c.check_name: c.status for c in report.checks}
        assert statuses.get("Double Vote Protection") == "SKIPPED"
        assert statuses.get("Candidate Count") == "PASSED"