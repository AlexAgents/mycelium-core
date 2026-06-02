# ADR-002: Use Geth Dev Mode instead of PoA Private Chain

## Status
Accepted

## Date
2026-05-20

## Context
For a sandbox application, we need a local blockchain with fast block times, zero cost setup, and unlocked developer accounts with pre-allocated ether to fund admin/voter wallets.

## Decision
We decided to use Geth in `--dev` mode with automatic block period
generation (`--dev.period 5`).

`--dev.period 5` means a new block is sealed every 5 seconds even
when no transactions are pending. This keeps the chain progressing
predictably for audit timestamp checks (SEC-03 Stage Enforcement
relies on monotonic block numbers between `VotingStarted` and
`VotingFinished` events). Lower values (`1`) were tested but caused
unnecessary CPU usage and noisy logs during idle UI sessions.

## Consequences

### Positive

- Zero manual setup: Geth starts instantly without a genesis file or custom sealers.
- A pre-funded developer account is unlocked and available immediately as `eth.coinbase`.
- Predictable block sealing every 5 seconds simplifies audit verification.

### Negative

- Ephemeral state: Geth `--dev` stores blockchain state in memory by design; data is lost on restart.
- Not a true simulation of a multi-node Proof-of-Authority (PoA) network.