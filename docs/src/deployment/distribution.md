# Distribution & Releases

How to publish and verify **MYCELIUM CORE** releases.

---

## Release Structure

A release consists of:

```text
dist/
├── MYCELIUM_CORE.exe    # Standalone executable
└── checksums.txt        # SHA-256 hashes
```

Plus the external `bin/geth.exe` distributed alongside.

---

## Creating a Release

1. Build the executable:
   ```bash
   python scripts/builder.py --build
   ```

2. Verify checksums:
   ```bash
   python scripts/builder.py --checksums
   ```

3. Create a GitHub Release with tag `v1.0.x`.
4. Attach `MYCELIUM_CORE.exe` and `checksums.txt`.

---

## Verification

Recipients verify file integrity:

```powershell
Get-FileHash "MYCELIUM_CORE.exe" -Algorithm SHA256 | Format-List
```

```bash
sha256sum -c checksums.txt
```

---

## Important Notes

- `bin/geth.exe` is **not** bundled inside the EXE. Distribute it in the `bin/` folder alongside the executable.
- The EXE includes: QSS themes, i18n JSON dictionaries, contract source files, and application icons.
- Runtime data (`data/`) is created automatically on first launch.