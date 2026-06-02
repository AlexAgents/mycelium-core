# ADR-007: Extraction of ErrorParser and Precheck from AppController

## Status
Accepted

## Date
2026-05-20

## Context
As more pre-vote validations and raw RPC error-handling cases were added, `AppController` was becoming too large and started violating the Single Responsibility Principle.

## Decision
We decided to extract low-level parsing and validation logic into dedicated domain modules: `ErrorParser` (for error translation) and `Precheck` (containing `PrecheckResult` and `PrecheckStatus` enums). `AppController` delegates tasks to these services.

## Consequences

### Positive

- Keeps `AppController` thin and maintainable.
- Highly isolated unit testing for `ErrorParser` cases.
- Strongly-typed `PrecheckResult` objects instead of dicts.

### Negative

- Introduces two new files to the codebase.