# Executable Generation (PyInstaller)

This guide describes how to compile the Python source code of **MYCELIUM CORE** into a standalone, single-file executable using the automated build script.

---

## Build Automation Script

The project provides a comprehensive builder script located at
`scripts/builder.py`. This script handles hidden imports, icon
generation, and SHA-256 checksum computation, and exposes a localized
interactive menu (EN / RU).

### How to Build

1. Open your terminal in the project root directory.
2. Run the build script:
   ```bash
   python scripts/builder.py
   ```

3. Select **[1] Build EXE** from the interactive menu.

### Non-interactive build
For CI or scripted builds, pass flags directly:

```bash
python scripts/builder.py --build         # build without menu
python scripts/builder.py --clean-all     # clean build/ + dist/
python scripts/builder.py --checksums     # print SHA-256 of dist/
python scripts/builder.py --lang en       # force English output
```

### Under the Hood
The script runs `PyInstaller` with the following configuration:

- `--onefile` — Bundles all python modules and dependencies into a single executable.
- `--windowed` — Compiles without an attached console window (Windows only).
- `--add-data` — Packages QSS themes, translation JSON dictionaries, and contract files directly into the executable binary.

> **Crucial Note:** The external `bin/geth.exe` process is **not** bundled inside the single executable to prevent excessive file size. Distribute `geth.exe` in the `bin/` directory alongside your compiled EXE.
