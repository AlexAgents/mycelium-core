# Data Flow Specifications

This document describes how transaction and state data flows between system layers during key operations.

---

## 1. Casting a Vote (Data Flow Pipeline)

When a voter submits a vote, data travels down through the layers, mutating the blockchain state, and returns a cryptographic receipt to the user.

```text
  [ Voter GUI ]
        │  1. Submit Private Key & Candidate Address
        ▼
  [ AppController ]
        │  2. Delegate precheck_vote()
        ├──────────────────────────┐
        ▼                          ▼
  [ Precheck Service ]      [ ErrorParser ]
        │  3. Valid? (Yes)         │ (In case of RPC failure)
        ▼                          ▼
  [ VotingService ] <──────────────┘
        │  4. Estimate gas, fetch nonce, sign TX on-chain
        ▼
  [ Web3Provider ]
        │  5. Send Signed Raw Transaction (JSON-RPC)
        ▼
  [ Geth Local Node ] ──(State mutated)──> [ VotingCore Contract ]
        │
        │  6. Return Transaction Receipt (Block Number, Gas Used)
        ▼
  [ Web3Provider ]
        │  7. Wrap in VoteReceipt DTO
        ▼
  [ Presentation Layer ] ──> Generate QR Code payload
```

## 2. Key Milestones

1. **Local Precheck:** Prevents sending txs that will obviously fail (e.g. voter has already voted, or is not in the whitelist). This saves CPU time and avoids state pollution.
2. **Nonce Synchronization:** Managed by `NonceManager` to prevent tx collisions when executing multiple calls sequentially.
3. **Receipt Generation:** The returned transaction receipt is formatted into a strictly-typed `VoteReceipt` object and passed back to the GUI for QR-code rendering.