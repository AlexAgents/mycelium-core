# ADR-003: Strict Ephemeral chain-data on Startup

## Status
Accepted

## Date
2026-05-20

## Context
Geth `--dev` preserves block headers in persistent `--datadir` but discards state trie data (such as account balances and contract storage) from memory on shutdown. This causes a corrupted state database on the next launch, leading to `missing trie node` and `historical state not available` errors.

## Decision
We decided to perform a strict clean up of `chain-data/active/` on every application startup.

## Consequences

### Positive

- Guaranteed clean state on launch: Geth never encounters "corrupted state database" errors.
- Stable mining and transaction processing on every run.
- Zero disk-bloat (active chain size remains minimal).

### Negative

- Historical blocks are not preserved across application restarts.
- Deployed contract addresses must be re-created on each launch.