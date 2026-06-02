# ADR-004: One Session = One Voting Contract

## Status
Accepted

## Date
2026-05-20

## Context
A smart contract designed for elections should be secure and single-use. Re-using a contract or reverting its stages introduces security risks and compromises audit integrity.

## Decision
We decided to enforce a strict "One Session = One Voting Contract" workflow. The `VotingCore.sol` stages move strictly forward: `SETUP → ACTIVE → FINISHED`. Re-use or restart is disabled on the smart contract level. Starting a new election requires deploying a new contract.

## Consequences

### Positive

- Enforces election integrity: finished votes can never be altered or restarted.
- Simple audit model: all events within a session contract belong to a single election.
- Aligns perfectly with the ephemeral nature of the Geth dev-mode blockchain.

### Negative

- Deployment transaction costs (gas) must be paid for every new election.