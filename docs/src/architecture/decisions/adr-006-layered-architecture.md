# ADR-006: Layered Architecture Pattern

## Status
Accepted

## Date
2026-05-20

## Context
Mixing blockchain transaction logic directly into Qt widgets creates "spaghetti code", violates separation of concerns, and makes testing impossible.

## Decision
We decided to enforce a strict layered architecture: `UI -> AppController (Facade) -> Services -> Infrastructure -> Smart Contract`. The UI layer is prohibited from importing Web3 or contract classes. All operations must pass through the `AppController` facade.

## Consequences

### Positive

- Clean code: UI files only handle layouts, styling, and basic validation.
- Testability: domain services (`AuditService`, `ErrorParser`) can be fully unit-tested without PyQt.
- Easy UI modification: stylesheets or widgets can be swapped without touching core business logic.

### Negative

- Minor boilerplate: adding a new feature requires passing calls through the Controller layer.