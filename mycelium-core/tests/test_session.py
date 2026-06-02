"""
Тесты для SessionContext и управления сессиями AppController.
"""
import pytest
from datetime import datetime

from src.core.models import (
    Candidate,
    SessionContext,
    Voter,
    ElectionStage,
)


class TestSessionContext:
    def test_initial_state(self):
        ctx = SessionContext()
        assert ctx.session_id is None
        assert ctx.contract_address is None
        assert not ctx.is_deployed
        assert ctx.candidate_count == 0
        assert ctx.voter_count == 0

    def test_reset(self):
        ctx = SessionContext()
        ctx.session_id = "test-id"
        ctx.contract_address = "0x0000000000000000000000000000000000000123"
        ctx.candidates.append(
            Candidate(
                name="A", party="P",
                address="0x0000000000000000000000000000000000000001",
            )
        )
        ctx.voters.append(
            Voter(address="0x0000000000000000000000000000000000000002")
        )
        ctx.deploy_block = 42

        ctx.reset()

        assert ctx.session_id is None
        assert ctx.contract_address is None
        assert ctx.candidate_count == 0
        assert ctx.voter_count == 0
        assert ctx.deploy_block == 0
        assert ctx.created_at is not None

    def test_is_deployed(self):
        ctx = SessionContext()
        assert not ctx.is_deployed
        ctx.contract_address = "0x00000000000000000000000000000000000000ab"
        assert ctx.is_deployed

    def test_candidate_count(self):
        ctx = SessionContext()
        ctx.candidates.append(
            Candidate(
                name="A", party="P",
                address="0x0000000000000000000000000000000000000001",
            )
        )
        ctx.candidates.append(
            Candidate(
                name="B", party="Q",
                address="0x0000000000000000000000000000000000000002",
            )
        )
        assert ctx.candidate_count == 2

    def test_voter_count(self):
        ctx = SessionContext()
        for i in range(5):
            ctx.voters.append(
                Voter(address=f"0x{i:040x}")
            )
        assert ctx.voter_count == 5


class TestVoterModel:
    def test_to_export_dict_with_key(self):
        addr = "0x00000000000000000000000000000000000000ab"
        v = Voter(
            address=addr,
            private_key="0xdef",
            has_voted=True,
        )
        d = v.to_export_dict()
        assert d["address"] == addr
        assert d["private_key"] == "0xdef"
        assert d["has_voted"] is True

    def test_to_export_dict_without_key(self):
        v = Voter(address="0x00000000000000000000000000000000000000ab")
        d = v.to_export_dict()
        assert "private_key" not in d

    def test_address_strip(self):
        addr = "0x00000000000000000000000000000000000000ab"
        v = Voter(address=f"  {addr}  ")
        assert v.address == addr


class TestCandidateModel:
    def test_defaults(self):
        c = Candidate(
            name="Test", party="Party",
            address="0x0000000000000000000000000000000000000001",
        )
        assert c.vote_count == 0
        assert c.registered is False

    def test_strip(self):
        addr = "0x0000000000000000000000000000000000000001"
        c = Candidate(
            name="  Alice  ",
            party="  Ind  ",
            address=f"  {addr}  ",
        )
        assert c.name == "Alice"
        assert c.party == "Ind"
        assert c.address == addr


class TestElectionStage:
    def test_values(self):
        assert ElectionStage.SETUP.value == 0
        assert ElectionStage.ACTIVE.value == 1
        assert ElectionStage.FINISHED.value == 2

    def test_display_name(self):
        assert ElectionStage.SETUP.display_name() == "SETUP"
        assert ElectionStage.ACTIVE.display_name() == "ACTIVE"
        assert ElectionStage.FINISHED.display_name() == "FINISHED"