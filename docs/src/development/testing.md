# Testing

MYCELIUM CORE uses `pytest` for automated tests.

The test suite focuses on domain logic, utilities, models, validation, nonce
management, i18n consistency and selected service behavior.

---

## Run Default Tests

From the application root:

```bash
cd mycelium-core
python -m pytest -v
```

Default test run excludes integration tests.

---

## Run Integration Tests

```bash
python -m pytest -m integration -v
```

Integration tests may require:

- installed Solidity compiler;
- internet access for first compiler installation;
- local environment suitable for compilation.

---

## Run Specific Test Files

### By file
```bash
# Audit service
python -m pytest tests/test_audit_service.py -v

# Nonce manager
python -m pytest tests/test_nonce_manager.py -v

# i18n coverage
python -m pytest tests/test_i18n_coverage.py -v

# Voting service helpers
python -m pytest tests/test_voting_service.py -v

# App controller
python -m pytest tests/test_app_controller.py -v
```

### By keyword (fast filtering)
```bash
# Run only tests related to error parsing
python -m pytest -k "error" -v

# Run only model and session tests
python -m pytest -k "model or session" -v

# Run only crypto and validator tests
python -m pytest -k "crypto or validator" -v

# Exclude integration tests explicitly
python -m pytest -m "not integration" -v
```

---

## Test Areas

| Area | Files |
|---|---|
| Models | `tests/test_models.py`, `tests/test_session.py` |
| Validators | `tests/test_validators.py` |
| Crypto utilities | `tests/test_crypto.py` |
| Nonce handling | `tests/test_nonce_manager.py` |
| Error parsing | `tests/test_error_parser.py` |
| Audit logic | `tests/test_audit_service.py` |
| Voting service helpers | `tests/test_voting_service.py` |
| App controller | `tests/test_app_controller.py` |
| i18n consistency | `tests/test_i18n_coverage.py` |
| Compiler integration | `tests/test_compiler.py` |
| Web3 provider | `tests/test_web3_provider.py` |
| Geth manager | `tests/test_geth_manager.py` |
| Precheck logic | `tests/test_precheck.py` |
| Voter status DTO | `tests/test_voter_status.py` |
| QR generation | `tests/test_qr.py` |
| Path utilities | `tests/test_paths.py` |
| Configuration | `tests/test_config.py` |

---

## Integration Marker

The compiler and full lifecycle tests are marked as `integration`.
Default pytest configuration enforces strict markers:

```ini
addopts = --strict-markers
```

Integration tests require the Geth binary in `bin/` and internet
access for the first Solidity compiler download. They are excluded
by default — run explicitly:

```bash
python -m pytest -m integration -v
```

---

## Documentation Checks

From the documentation root:

```bash
cd docs
mkdocs build --strict
```

---

## Recommended Pre-release Checklist

```bash
# 1. Check documentation builds without errors
cd docs
mkdocs build --strict

# 2. Run unit tests
cd ../mycelium-core
python -m pytest -v

# 3. Run integration tests (requires Geth binary)
python -m pytest -m integration -v
```

---

## Current Scope

The test suite covers unit-level and selected integration-level logic.

**Current status: 180 tests passed** in ~100 seconds (including full
lifecycle integration test with real local Geth node).

Full UI E2E testing is not implemented in this version.