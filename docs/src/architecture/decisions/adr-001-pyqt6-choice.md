# ADR-001: Selection of PyQt6 over PySide6

## Status
Accepted

## Date
2026-05-20

## Context
The original SRS recommended PySide6 as the primary GUI framework. However, during the implementation phase, PyQt6 was selected due to existing library compatibility and more stable PyInstaller support on the target Windows environment.

## Decision
We decided to use PyQt6 (>=6.7.0) for the Presentation Layer. 

## Consequences

### Positive

- Robust, industry-proven window management on Windows 10/11.
- Better compatibility with `qtawesome` icon compilation.
- Seamless integration with PyInstaller without complex import-hook configuration.

### Negative

- Deviation from PySide6 (the official Qt Company library).
- Minor import adjustments are needed if migrating to PySide6 in the future.