from src.utils.validators import (
    is_valid_eth_address,
    is_valid_private_key,
    normalize_private_key,
    validate_candidate_name,
    validate_candidate_party,
    validate_candidate_limit,
    validate_voter_count,
)


def test_valid_eth_address():
    assert is_valid_eth_address(
        "0x0000000000000000000000000000000000000000"
    )


def test_invalid_eth_address():
    assert not is_valid_eth_address(
        "invalid"
    )


def test_valid_private_key():
    assert is_valid_private_key(
        "0x" + "1" * 64
    )


def test_invalid_private_key():
    assert not is_valid_private_key(
        "123"
    )


def test_normalize_private_key():
    key = "1" * 64
    normalized = normalize_private_key(
        key
    )
    assert normalized.startswith("0x")
    assert len(normalized) == 66


def test_candidate_name_validation():
    ok, _ = validate_candidate_name(
        "Alice"
    )
    assert ok
    ok, _ = validate_candidate_name(
        ""
    )
    assert not ok


def test_candidate_party_validation():
    ok, _ = validate_candidate_party(
        "Independent"
    )
    assert ok
    ok, _ = validate_candidate_party(
        ""
    )
    assert not ok


def test_candidate_limit_validation():
    ok, _ = validate_candidate_limit(2)
    assert ok
    ok, _ = validate_candidate_limit(11)
    assert not ok


def test_voter_count_validation():
    ok, _ = validate_voter_count(100)
    assert ok
    ok, _ = validate_voter_count(0)
    assert not ok