# Scripts

Utility scripts for developing and building MYCELIUM CORE.

All scripts are run from the project root and work with paths
relative to the root.

## Files

| File | OS | Purpose |
|---|---|---|
| `builder.py` | All | Build EXE via PyInstaller |
| `clean.bat` | Windows | Deep project cleanup (CMD) |
| `clean.ps1` | Windows | Deep project cleanup (PowerShell) |
| `clean.sh` | Linux/macOS | Deep project cleanup (Bash) |

## Usage

### Building EXE

```bash
python scripts/builder.py                # interactive menu
python scripts/builder.py --build        # without menu
python scripts/builder.py --checksums    # SHA-256
python scripts/builder.py --clean-all   # clean build/ + dist/
python scripts/builder.py --help
```