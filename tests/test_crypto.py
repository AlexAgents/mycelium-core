from src.utils.crypto import (
    address_from_private_key,
    generate_eth_keypair,
    generate_test_voters,
)


def test_generate_keypair():

    priv, addr = generate_eth_keypair()

    assert priv.startswith("0x")

    assert addr.startswith("0x")

    assert len(priv) == 66

    assert len(addr) == 42


def test_address_derivation():

    priv, addr = generate_eth_keypair()

    derived = address_from_private_key(
        priv
    )

    assert derived == addr


def test_generate_test_voters():

    voters = generate_test_voters(5)

    assert len(voters) == 5

    for voter in voters:

        assert "address" in voter

        assert "private_key" in voter