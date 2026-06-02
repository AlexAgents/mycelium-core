# ADR-005: Runtime i18n Language Switching

## Status
Accepted

## Date
2026-05-20

## Context
The application must support English and Russian. Restarting the software to apply a new language degrades user experience. We need a way to change languages instantly.

## Decision
We decided to implement a custom `I18N` manager subclassing `QObject` with a `languageChanged` Qt signal. Each UI tab registers a `retranslate_ui()` method. When the language combobox changes, `I18N` loads the new dictionary, emits the signal, and `MainWindow` triggers `retranslate_ui()` on all tabs.

## Consequences

### Positive

- Seamless UX: language changes instantly without restarting or losing the current session.
- Centralized string storage in `ru.json` and `en.json`.

### Negative

- Requires manual widget reference tracking (`self._lbl_*`) in tabs to re-apply text at runtime.