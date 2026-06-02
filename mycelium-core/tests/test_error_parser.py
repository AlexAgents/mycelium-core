"""
Тесты для ErrorParser (бизнес-логика парсинга ошибок).
"""
from src.core.error_parser import ErrorParser


class TestErrorParser:
    def setup_method(self):
        self.parser = ErrorParser()

    def test_insufficient_funds(self):
        result = self.parser.parse(
            "insufficient funds for gas * price + value"
        )
        assert result.message_key == "err.parser.insufficient_funds"
        assert result.action_id == "fund_account"
        assert result.action_key == "err.parser.action.fund"

    def test_nonce_too_low(self):
        result = self.parser.parse(
            "nonce too low: next nonce 5, tx nonce 3"
        )
        assert result.message_key == "err.parser.nonce_conflict"
        assert result.action_id == "sync_nonce"
        assert result.action_key == "err.parser.action.sync_nonce"

    def test_already_known(self):
        result = self.parser.parse("already known")
        assert result.message_key == "err.parser.nonce_conflict"
        assert result.action_id == "sync_nonce"

    def test_timeout(self):
        result = self.parser.parse(
            "Transaction confirmation timed out"
        )
        assert result.message_key == "err.parser.timeout"
        assert result.action_id == "check_status"
        assert result.action_key == "err.parser.action.check_status"

    def test_not_whitelisted_raw(self):
        result = self.parser.parse(
            "execution reverted: NotWhitelisted()"
        )
        assert result.message_key == "err.parser.not_whitelisted"
        assert result.action_id is None

    def test_not_whitelisted_humanized(self):
        result = self.parser.parse(
            "This address is not in the whitelist."
        )
        assert result.message_key == "err.parser.not_whitelisted"

    def test_already_voted_raw(self):
        result = self.parser.parse(
            "execution reverted: AlreadyVoted()"
        )
        assert result.message_key == "err.parser.already_voted"

    def test_candidate_not_found_raw(self):
        result = self.parser.parse(
            "execution reverted: CandidateNotFound()"
        )
        assert result.message_key == "err.parser.candidate_not_found"

    def test_invalid_stage_raw(self):
        result = self.parser.parse(
            "execution reverted: InvalidStage()"
        )
        assert result.message_key == "err.parser.invalid_stage"

    def test_unauthorized_raw(self):
        result = self.parser.parse(
            "execution reverted: Unauthorized()"
        )
        assert result.message_key == "err.parser.unauthorized"

    def test_execution_reverted_generic(self):
        result = self.parser.parse(
            "execution reverted: SomethingUnexpected()"
        )
        assert result.message_key == "err.parser.contract_reverted"
        assert result.action_id is None

    def test_unknown_error(self):
        text = "Something completely unexpected"
        result = self.parser.parse(text)
        assert result.message_key is None
        assert result.raw_message == text
        assert result.action_key is None
        assert result.action_id is None