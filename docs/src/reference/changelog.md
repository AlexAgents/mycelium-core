# Changelog

All notable changes to MYCELIUM CORE are documented in this file.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.1] — 2026-05-20

Maintenance release. Critical bug fixes and code maturity improvements
identified during pre-defence code review. No breaking changes.

### Added

#### Core / Backend

- `VoterStatus` DTO in `src/core/voter_status.py` — typed snapshot of
  voter state (whitelist, has_voted, balance, stage) for UI consumption.
- `AppController.get_voter_status()` — single-call method aggregating
  multiple RPC queries, returns `VoterStatus`.
- `VoterStatusWorker` in `src/ui/workers/voter_status_worker.py` —
  background worker for non-blocking voter status refresh.
- 12 new i18n keys `err.parser.*` for all parsed RPC and contract errors
  (insufficient funds, nonce conflict, timeout, NotWhitelisted,
  AlreadyVoted, CandidateNotFound, InvalidStage, Unauthorized, generic
  contract revert) plus 3 action keys for actionable dialogs.

### Changed

- `ErrorParser.parse()` now returns i18n keys (`message_key`,
  `action_key`) instead of hardcoded English strings. UI calls `t(key)`
  itself, preserving strict layer separation.
- `AppController.parse_rpc_error()` payload reshaped:
  `{message_key, raw_message, action_key, action_id}` instead of
  `{message, action, action_id}`.
- `VoteTab._check_voter_status` replaced with debounced async request
  via `VoterStatusWorker` — UI no longer blocks on RPC calls when typing
  the private key.
- `VoteTab._sec06_shown` moved from module-level global to instance
  attribute, properly reset by `reset_ui()`.
- Russian translation of `admin.dialog.cannot_start.no_whitelist`:
  button name inside the message now matches the actual button label
  in the Russian UI.
- Test fixtures updated to use valid 40-character Ethereum addresses
  instead of placeholders like `0x1`, `0xabc`.

### Fixed

- `GethManager._force_kill_pid` was defined twice in the same class;
  the second definition silently overrode the first and lost the `/T`
  flag (kill child processes on Windows). Duplicate removed.
- `Account.enable_unaudited_hdwallet_features()` was called at module
  import time in `crypto.py` despite HD wallets being unused. Removed
  to avoid altering global `eth_account` state on every import.
- `MainWindow.closeEvent` called `geth.stop()` twice (once via
  `controller.shutdown()` finally-block, once directly). Resulted in
  duplicate `taskkill` invocations and noisy logs. Direct call removed.
- UI freeze (~50–200 ms) on every keystroke in the private key input
  on Vote tab, caused by three synchronous RPC calls in the UI thread.
  Fixed by moving the entire status query into `VoterStatusWorker`.

### Removed

- Module-level `_sec06_shown` global in `vote_tab.py`.
- Duplicate `_force_kill_pid` method definition in `geth_manager.py`.
- `Account.enable_unaudited_hdwallet_features()` call from `crypto.py`.
- Duplicate `self.controller.geth.stop()` call from
  `MainWindow.closeEvent`.

### Security

- All error messages shown to the user are now properly localized,
  preventing English error text from leaking through a Russian UI.

### Tests

- **180 passed** (100.86s) — full run includes integration tests with
  real local Geth node.
- `test_integration.py` — 12 full lifecycle voting tests (01–12).
- `pytest.ini`: `addopts = --strict-markers` — integration tests require
  explicit `-m integration` flag to run; excluded by default.

---

## [1.0.0] — 2026-05-10

Final release. All architectural, functional and UX requirements
from the original SRS are met. Production-ready for demo and audit
purposes.

### Added

#### Core / Backend

- `AppController.precheck_vote()` — full pre-vote validation in domain
  layer.
- `AppController.build_full_report()` — single source of truth for audit
  export.
- `AppController.fund_from_dev()` — async transfer from Geth dev account.
- `AppController.check_start_voting_ready()` — pre-flight check for
  `startVoting`.
- `AppController.get_chain_stats()` — disk usage and session statistics.
- `AppController.reset_blockchain_data()` — full reset with retry on
  Windows.
- `AppController.get_client_version()`, `is_contract_deployed()`,
  `get_contract_address()`, `is_dev_mode()` — facade getters.
- `ErrorParser` — extracted from AppController to
  `src/core/error_parser.py`.
- `PrecheckResult` / `PrecheckStatus` — typed result objects in
  `src/core/precheck.py`.
- `GethManager._taskkill_all_geth()` — safety net for zombie processes.
- `GethManager._is_port_in_use()` — pre-flight port check.
- `GethManager._shutting_down` flag — prevents false crash callbacks.

#### UI / UX

- About dialog with logo, version, author and GitHub link.
- Reset Blockchain Data button in header with confirmation dialog.
- Startup warning for large chain-data folder (>500 MB).
- Stage-aware availability indicator in Audit mode combo.
- Voters section: blocked until contract deployed.
- Candidates section: blocked after registration or outside SETUP stage.
- Admin key input: read-only after deploy (until New Session).
- Stage-based pre-checks before vote/mass-vote (SETUP / FINISHED
  warnings).
- "Fund from Dev" button (icon-only) for dev-mode balance management.
- Toast notification queue with deduplication.
- Logs tab: live search filter, autoscroll checkbox, info bar
  (lines / size / path).
- About / Theme / Exit buttons as icon-only (cleaner header).

#### Architecture

- Single source of truth for full report (`build_full_report`).
- Strict separation: UI never imports `web3`, `eth_account`, `solcx`.
- Unified `MessageDialog` widget replacing scattered `QMessageBox` calls.
- `msgbox_helpers` utility for translated standard buttons.
- Pytest fixture `conftest.py` for clean test runs.
- Logger auto-archives previous `session.log` on startup.

#### Documentation

- Architecture Decision Records (ADR-001 through ADR-007).
- Comprehensive README with setup instructions.
- Inline docstrings for all public methods.

### Changed

- Geth launched with `--dev.period 5` for stable block sealing.
- Chain-data cleaned on each startup (Geth `--dev` incompatible with
  persistent datadir).
- Balance display switched to scientific notation for very large values
  (`1.16e+59 ETH`).
- `QGroupBox` titles redesigned (flush with card border).
- `StatusBadge` contrast improved in light theme.
- Toasts: stacked queue instead of parallel display.
- All hardcoded strings moved to `i18n/ru.json` and `i18n/en.json`.
- Default language switched to English on first launch.

### Fixed

- pytest collection error (`ModuleNotFoundError: src`) via root-level
  `pytest.ini` + `conftest.py`.
- Geth crash dialog showing on intentional shutdown (added
  `_shutting_down` flag).
- Toast appearing on top of other Windows applications (now child of
  central widget).
- Duplicate toasts when language switched twice.
- Admin balance label overflowing on small windows.
- Stage-dependent buttons not updating without manual refresh.
- Geth manager: file locks on Windows after stop (retry with backoff).
- Logs tab auto-reloading on tab switch (now manual via Refresh).
- `session.log` not clearing between application restarts.
- Light theme: black text replaced with dark blue navigation tones.

### Removed

- `audit_worker.py` (replaced by inline `_StagedAuditWorker`).
- `_SENTINEL_PATTERNS` dead constant in logger.
- `SOLC_BIN` unused path (solc installed via solcx).
- Duplicate audit checks in `_run_checks` for full mode.
- `[dev]` section from `app.cfg` defaults.
- `parse_rpc_error()` static method removed in favour of instance method.

### Security

- `session.log` auto-redacts strings matching private key pattern.
- Voters export requires explicit user confirmation.
- SEC-06 warning shown on first private key input per session.
- All admin actions verified against contract owner in
  `_check_owner_actions`.

---

## [0.3.0] — 2024-03-14

### Added

- Mass Vote with pre-filtering (whitelist + balance check).
- Improved error handling: non-blocking UI, retry suggestions.
- Status bar progress indicator with gradient fill.
- Internationalization (`ru.json`, `en.json`) with runtime language
  switch.
- Owner-only administration audit check.
- `VotingStarted` and `VotingFinished` events in smart contract.
- Toast notifications (bottom-right, colored by type).

### Changed

- Audit refactored into staged checks (pre-vote, live, final, full).
- Light theme: all widgets covered, no missing styles.
- Balance display: ETH format with adaptive precision.

### Fixed

- Receipt QR cleared on mass vote start.
- New Session: complete UI table cleanup.
- Logs tab: icon colors aligned with theme.
- Winner shown only after FINISHED stage.
- Voters layout: spread across full row instead of left-clustered.

---

## [0.2.0] — 2024-03-10

### Added

- Register candidates button: enabled only with ≥2 candidates.
- Fund Voters button for gas distribution.
- Mass Vote feature (JSON file or current session).
- Geth mode indicator in header.
- Exit button with confirmation dialog.
- New Session button: archive logs, reset state, optional auto-deploy.
- Logs tab as separate UI section.
- Staged audit (pre-vote / during / post-vote).
- Drag-and-drop JSON import for voters.
- Auto-loading candidates in VoteTab after registration.
- Close confirmation when active workers running.
- `DEV_ADMIN_KEY` auto-fill in dev mode.

### Fixed

- Voters buttons blocking logic after whitelist add.
- Multiple architectural cleanups per SRS section 6.

---

## [0.1.0] — 2024-03-01

Initial implementation based on SRS v1.0.

- Smart contract `VotingCore.sol`.
- Service layer (`VotingService`, `AuditService`, `NonceManager`).
- `AppController` facade.
- Three main tabs: Admin, Vote, Audit.
- Local Geth process management.