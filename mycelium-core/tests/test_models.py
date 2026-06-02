from src.core.models import (
    AuditCheck,
    AuditReport,
    Candidate,
    ElectionStage,
    SessionContext,
    VoteReceipt,
)


def test_candidate_model():
    candidate = Candidate(
        name="Alice",
        party="Independent",
        address="0x0000000000000000000000000000000000000001",
    )
    assert candidate.name == "Alice"
    assert candidate.vote_count == 0


def test_stage_enum():
    assert ElectionStage.SETUP.value == 0
    assert ElectionStage.ACTIVE.value == 1
    assert ElectionStage.FINISHED.value == 2


def test_vote_receipt():
    receipt = VoteReceipt(
        tx_hash="0x" + "1" * 64,
        voter_address="0x000000000000000000000000000000000000aaaa",
        candidate_address="0x000000000000000000000000000000000000bbbb",
        block_number=1,
        session_id="test",
    )
    data = receipt.to_dict()
    assert data["tx_hash"] == "0x" + "1" * 64


def test_audit_report():
    report = AuditReport(
        session_id="abc",
        audit_timestamp=__import__(
            "datetime"
        ).datetime.utcnow(),#мб заменить
    )
    report.checks.append(
        AuditCheck(
            check_name="Check",
            status="PASSED",
            details="OK",
        )
    )
    assert report.all_passed
    assert report.passed_count == 1


def test_session_context():
    session = SessionContext()
    session.contract_address = "0x0000000000000000000000000000000000000123"
    assert session.is_deployed
    session.reset()
    assert not session.is_deployed