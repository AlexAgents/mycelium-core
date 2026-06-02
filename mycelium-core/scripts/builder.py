"""
Project build script for MYCELIUM CORE EXE generation.

Автоматически:
- Находит hidden imports (web3, eth_account, solcx, PyQt6 и др.)
- Использует существующий логотип Original.png как иконку
- Включает в EXE: themes/, i18n/, contracts/, icons/
- НЕ включает: bin/geth.exe (внешний binary), chain-data/, logs/
- Вычисляет SHA-256 контрольные суммы
- Поддерживает русский и английский языки

Использование:
    python builder.py                    # интерактивное меню
    python builder.py --build            # сборка без меню
    python builder.py --clean            # очистка build/
    python builder.py --clean-all        # очистка всего
    python builder.py --checksums        # SHA-256 хеши
    python builder.py --lang en          # английский язык
"""

import os
import sys
import shutil
import subprocess
import hashlib
import time
import struct
import argparse
import re
import locale
from datetime import datetime
from typing import List, Optional, Dict

# ════════════════════ CONFIGURATION ════════════════════

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Скрипт лежит в scripts/, корень проекта — на уровень выше
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
ASSETS_DIR = os.path.join(SRC_DIR, "assets")
ICONS_DIR = os.path.join(ASSETS_DIR, "icons")
THEMES_DIR = os.path.join(SRC_DIR, "ui", "themes")
I18N_DIR = os.path.join(SRC_DIR, "ui", "i18n")
CONTRACTS_DIR = os.path.join(PROJECT_ROOT, "contracts")
BUILD_DIR = os.path.join(PROJECT_ROOT, "build")
DIST_DIR = os.path.join(PROJECT_ROOT, "dist")
SPEC_DIR = os.path.join(BUILD_DIR, "spec")

# Иконка для EXE — берём из ассетов проекта
SOURCE_ICON_PNG = os.path.join(ICONS_DIR, "Original.png")
ICON_ICO = os.path.join(ICONS_DIR, "app.ico")

PROJECT_NAME = "MYCELIUM_CORE"
EXE_EXT = ".exe" if sys.platform.startswith("win") else ""
EXE_NAME = f"{PROJECT_NAME}{EXE_EXT}"
EXE_PATH = os.path.join(DIST_DIR, EXE_NAME)

ICON_SIZES = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
ICON_FALLBACK_COLOR = (56, 139, 253)  # #388bfd

# Subdirectories to scan for imports
PROJECT_PACKAGES = ["src/core", "src/ui", "src/utils"]


def default_ui_mode() -> str:
    """Windows -> windowed, Linux/macOS -> console."""
    return "windowed" if sys.platform.startswith("win") else "console"


def resolve_ui_mode(args) -> str:
    """Resolve UI mode by priority: flag > debug > platform default."""
    if getattr(args, "console", False):
        return "console"
    if getattr(args, "windowed", False):
        return "windowed"
    if getattr(args, "debug", False):
        return "console"
    return default_ui_mode()


# ════════════════════ LOCALIZATION ════════════════════

CURRENT_LANG = "en"

LANG: Dict[str, Dict[str, str]] = {
    "ru": {
        "menu_title": "Сборщик MYCELIUM CORE",
        "menu_root": "Корень",
        "menu_entry": "Вход",
        "menu_icon": "Иконка",
        "menu_exe": "EXE",
        "menu_choice": "Ваш выбор",
        "opt_build": "Собрать EXE",
        "opt_regen_icon": "Перегенерировать иконку",
        "opt_clean_build": "Очистить build/",
        "opt_clean_dist": "Очистить dist/",
        "opt_clean_all": "Очистить всё (build + dist)",
        "opt_clean_project": "Глубокая очистка проекта (chain, logs, кэш)",
        "opt_checksums": "Показать SHA-256 хеши",
        "opt_change_lang": "Change language / Сменить язык",
        "opt_exit": "Выход",
        "status_yes": "Есть",
        "status_no": "Нет",
        "status_not_built": "не собран",
        "status_not_found": "НЕ НАЙДЕН",
        "checking_pyinstaller": "Проверка PyInstaller...",
        "pyinstaller_found": "PyInstaller найден",
        "pyinstaller_not_found": "PyInstaller не найден!",
        "pyinstaller_install_prompt": "Установить автоматически через pip? (y/n)",
        "pyinstaller_installed": "PyInstaller установлен",
        "pyinstaller_install_failed": "Не удалось установить PyInstaller",
        "generating_icon": "Генерация иконки из",
        "icon_created_pillow": "Иконка создана (Pillow)",
        "icon_created_fallback": "Иконка создана (Fallback struct)",
        "icon_create_failed": "Не удалось создать иконку",
        "source_icon_missing": "Исходный логотип Original.png не найден",
        "cleaning_build": "Очистка build/ и кэша...",
        "cleaning_dist": "Очистка dist/...",
        "cleaning_project": "Глубокая очистка проекта...",
        "temp_files_cleaned": "Временные файлы очищены",
        "dist_cleaned": "Папка dist очищена",
        "project_cleaned": "Проект очищен (chain, logs, кэш)",
        "clean_error": "Ошибка очистки",
        "starting_pyinstaller": "ЗАПУСК PYINSTALLER",
        "building": "Сборка",
        "entry_point": "Точка входа",
        "icon_label": "Иконка",
        "yes": "Да",
        "no": "Нет",
        "build_complete": "Сборка завершена за",
        "sec": "сек",
        "file_label": "Файл",
        "size_label": "Размер",
        "build_error": "Сборка завершилась с ошибкой!",
        "last_errors": "ПОСЛЕДНИЕ ОШИБКИ (STDERR)",
        "full_log": "Полный лог",
        "build_timeout": "Превышено время ожидания (15 мин)",
        "critical_error": "Критическая ошибка",
        "entry_not_found": "Точка входа (main.py) не найдена!",
        "press_enter": "Нажмите Enter для продолжения...",
        "goodbye": "До свидания!",
        "ready_files": "Готовые файлы здесь",
        "invalid_choice": "Неверный выбор",
        "select_language": "Выберите язык / Select language",
        "lang_option_ru": "Русский",
        "lang_option_en": "English",
        "operation_cancelled": "Операция прервана пользователем",
        "scanning_imports": "Сканирование импортов...",
        "found_imports": "Найдено скрытых импортов",
        "checksum_title": "SHA-256 КОНТРОЛЬНЫЕ СУММЫ",
        "checksum_saved": "Сохранено в",
        "checksum_no_files": "В dist/ нет файлов",
        "checksum_no_dist": "Папка dist/ не найдена. Сначала соберите EXE",
        "checksum_computing": "Вычисление контрольных сумм...",
        "checksum_github": "Для GitHub Release Notes",
        "checksum_verify_ps": "Проверка (PowerShell)",
        "checksum_verify_bash": "Проверка (Linux/macOS)",
        "warn_geth_external": "ВНИМАНИЕ: bin/geth.exe НЕ включается в EXE",
        "warn_geth_distribute": "Распространяйте geth.exe отдельно или скачивайте при первом запуске",
        "deep_clean_warn": "ВНИМАНИЕ: будут удалены данные blockchain, логи, кэш",
        "deep_clean_confirm": "Продолжить? (y/n)",
        "deep_clean_aborted": "Глубокая очистка отменена",
    },
    "en": {
        "menu_title": "MYCELIUM CORE Builder",
        "menu_root": "Root",
        "menu_entry": "Entry",
        "menu_icon": "Icon",
        "menu_exe": "EXE",
        "menu_choice": "Your choice",
        "opt_build": "Build EXE",
        "opt_regen_icon": "Regenerate icon",
        "opt_clean_build": "Clean build/",
        "opt_clean_dist": "Clean dist/",
        "opt_clean_all": "Clean all (build + dist)",
        "opt_clean_project": "Deep clean project (chain, logs, cache)",
        "opt_checksums": "Show SHA-256 checksums",
        "opt_change_lang": "Change language / Сменить язык",
        "opt_exit": "Exit",
        "status_yes": "Yes",
        "status_no": "No",
        "status_not_built": "not built",
        "status_not_found": "NOT FOUND",
        "checking_pyinstaller": "Checking PyInstaller...",
        "pyinstaller_found": "PyInstaller found",
        "pyinstaller_not_found": "PyInstaller not found!",
        "pyinstaller_install_prompt": "Install automatically via pip? (y/n)",
        "pyinstaller_installed": "PyInstaller installed",
        "pyinstaller_install_failed": "Failed to install PyInstaller",
        "generating_icon": "Generating icon from",
        "icon_created_pillow": "Icon created (Pillow)",
        "icon_created_fallback": "Icon created (Fallback struct)",
        "icon_create_failed": "Failed to create icon",
        "source_icon_missing": "Source logo Original.png not found",
        "cleaning_build": "Cleaning build/ and cache...",
        "cleaning_dist": "Cleaning dist/...",
        "cleaning_project": "Deep cleaning project...",
        "temp_files_cleaned": "Temp files cleaned",
        "dist_cleaned": "Dist folder cleaned",
        "project_cleaned": "Project cleaned (chain, logs, cache)",
        "clean_error": "Clean error",
        "starting_pyinstaller": "STARTING PYINSTALLER",
        "building": "Building",
        "entry_point": "Entry point",
        "icon_label": "Icon",
        "yes": "Yes",
        "no": "No",
        "build_complete": "Build complete in",
        "sec": "sec",
        "file_label": "File",
        "size_label": "Size",
        "build_error": "Build finished with error!",
        "last_errors": "LAST ERRORS (STDERR)",
        "full_log": "Full log",
        "build_timeout": "Build timeout exceeded (15 min)",
        "critical_error": "Critical error",
        "entry_not_found": "Entry point (main.py) not found!",
        "press_enter": "Press Enter to continue...",
        "goodbye": "Goodbye!",
        "ready_files": "Ready files here",
        "invalid_choice": "Invalid choice",
        "select_language": "Select language / Выберите язык",
        "lang_option_ru": "Русский",
        "lang_option_en": "English",
        "operation_cancelled": "Operation cancelled by user",
        "scanning_imports": "Scanning imports...",
        "found_imports": "Hidden imports found",
        "checksum_title": "SHA-256 CHECKSUMS",
        "checksum_saved": "Saved to",
        "checksum_no_files": "No files in dist/",
        "checksum_no_dist": "dist/ not found. Build EXE first",
        "checksum_computing": "Computing checksums...",
        "checksum_github": "For GitHub Release Notes",
        "checksum_verify_ps": "Verify (PowerShell)",
        "checksum_verify_bash": "Verify (Linux/macOS)",
        "warn_geth_external": "WARNING: bin/geth.exe is NOT bundled into EXE",
        "warn_geth_distribute": "Distribute geth.exe separately or download on first run",
        "deep_clean_warn": "WARNING: blockchain data, logs, cache will be deleted",
        "deep_clean_confirm": "Continue? (y/n)",
        "deep_clean_aborted": "Deep clean cancelled",
    }
}


def t(key: str) -> str:
    """Get localized string by key."""
    return LANG.get(CURRENT_LANG, LANG["en"]).get(key, key)


def detect_system_language() -> str:
    """Detect system language."""
    if sys.platform == "win32":
        try:
            import ctypes
            user32 = ctypes.windll.user32
            num_layouts = user32.GetKeyboardLayoutList(0, None)
            if num_layouts > 0:
                layout_ids = (ctypes.c_void_p * num_layouts)()
                user32.GetKeyboardLayoutList(num_layouts, layout_ids)
                for lid in layout_ids:
                    if (lid & 0xFFFF if lid else 0) == 0x0419:
                        return "ru"
        except Exception:
            pass
    try:
        loc = locale.getdefaultlocale()[0] or ""
        if loc.lower().startswith("ru"):
            return "ru"
    except Exception:
        pass
    return "en"


def set_language(lang: str):
    global CURRENT_LANG
    if lang in LANG:
        CURRENT_LANG = lang


def prompt_language_selection():
    print(f"\n{t('select_language')}")
    print(f"   [1] {t('lang_option_ru')}")
    print(f"   [2] {t('lang_option_en')}")
    choice = input("   > ").strip()
    if choice == "1":
        set_language("ru")
    elif choice == "2":
        set_language("en")


# ════════════════════ UI HELPERS ════════════════════

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(text: str):
    print(f"\n{'=' * 64}")
    print(f"   {text}")
    print(f"{'=' * 64}")


def print_section(text: str):
    print(f"\n{'-' * 64}")
    print(f" {text}")
    print(f"{'-' * 64}")


def print_success(text: str):
    print(f"[OK] {text}")


def print_error(text: str):
    print(f"[ERROR] {text}")


def print_warn(text: str):
    print(f"[WARN] {text}")


def print_info(text: str):
    print(f"[INFO] {text}")


def pause():
    input(f"\n{t('press_enter')}")


def get_file_info(path: str) -> str:
    if not os.path.exists(path):
        return t("status_not_built")
    size_mb = os.path.getsize(path) / (1024 * 1024)
    mtime = os.path.getmtime(path)
    date_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
    return f"{size_mb:.2f} MB | {date_str}"


# ════════════════════ CHECKSUM ════════════════════

def sha256_file(filepath: str) -> str:
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def compute_checksums(show_github: bool = True) -> bool:
    """Compute SHA-256 for all files in dist/, save checksums.txt."""
    if not os.path.exists(DIST_DIR):
        print_error(t("checksum_no_dist"))
        return False

    files = sorted([
        f for f in os.listdir(DIST_DIR)
        if os.path.isfile(os.path.join(DIST_DIR, f))
        and not f.endswith(".txt")
    ])

    if not files:
        print_error(t("checksum_no_files"))
        return False

    print_info(t('checksum_computing'))
    print_section(t("checksum_title"))

    lines = []
    for filename in files:
        filepath = os.path.join(DIST_DIR, filename)
        file_hash = sha256_file(filepath)
        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        line = f"{file_hash}  {filename}"
        lines.append(line)
        print(f"\n  File: {filename}")
        print(f"  SHA256: {file_hash}")
        print(f"  Size:   {size_mb:.1f} MB")

    checksum_path = os.path.join(DIST_DIR, "checksums.txt")
    with open(checksum_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"\n{'-' * 64}")
    print_success(f"{t('checksum_saved')}: {checksum_path}")

    if show_github:
        print(f"\n{t('checksum_github')}:\n")
        print("```text")
        for line in lines:
            print(line)
        print("```")
        print(f"\n{t('checksum_verify_ps')}:")
        print("```powershell")
        for filename in files:
            print(f'Get-FileHash "{filename}" -Algorithm SHA256 | Format-List')
        print("```")
        print(f"\n{t('checksum_verify_bash')}:")
        print("```bash")
        print("sha256sum -c checksums.txt")
        print("```")

    return True


# ════════════════════ BUILD LOGIC ════════════════════

def find_entry_point() -> Optional[str]:
    """Find main.py in project root."""
    path = os.path.join(PROJECT_ROOT, "main.py")
    return path if os.path.exists(path) else None


def check_pyinstaller() -> bool:
    """Check PyInstaller installation."""
    print_info(t("checking_pyinstaller"))
    try:
        subprocess.run(
            [sys.executable, "-m", "PyInstaller", "--version"],
            capture_output=True, check=True
        )
        print_success(t("pyinstaller_found"))
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_warn(t("pyinstaller_not_found"))
        choice = input(f"   {t('pyinstaller_install_prompt')}: ").strip().lower()
        if choice in ('y', 'д', 'yes', 'да'):
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "pyinstaller"],
                    check=True
                )
                print_success(t("pyinstaller_installed"))
                return True
            except subprocess.CalledProcessError:
                print_error(t("pyinstaller_install_failed"))
                return False
        return False


def generate_icon_from_png(source_png: str, target_ico: str) -> bool:
    """Generate .ico from source PNG using Pillow."""
    try:
        from PIL import Image
    except ImportError:
        return False
    try:
        img = Image.open(source_png).convert("RGBA")
        img.save(target_ico, format='ICO', sizes=ICON_SIZES)
        return True
    except Exception as e:
        print_warn(f"Pillow error: {e}")
        return False


def generate_icon_fallback(target_ico: str) -> bool:
    """Create simple ICO without Pillow (single colored 32x32)."""
    header = struct.pack('<HHH', 0, 1, 1)
    w, h = 32, 32
    bmp_header_size = 40
    pixel_data_size = w * h * 4
    total_size = bmp_header_size + pixel_data_size
    offset = 22
    entry = struct.pack('<BBBBHHII', w, h, 0, 0, 1, 32, total_size, offset)
    bmp_info = struct.pack(
        '<IIIHHIIIIII',
        bmp_header_size, w, h * 2, 1, 32, 0,
        pixel_data_size, 0, 0, 0, 0
    )
    r, g, b = ICON_FALLBACK_COLOR
    pixel = struct.pack('BBBB', b, g, r, 255)
    pixels = pixel * (w * h)
    try:
        os.makedirs(os.path.dirname(target_ico), exist_ok=True)
        with open(target_ico, 'wb') as f:
            f.write(header + entry + bmp_info + pixels)
        return True
    except Exception as e:
        print_error(f"Fallback icon error: {e}")
        return False


def ensure_icon():
    """Ensure app.ico exists. Try Pillow from Original.png, else fallback."""
    os.makedirs(ICONS_DIR, exist_ok=True)
    if os.path.exists(ICON_ICO) and os.path.getsize(ICON_ICO) > 0:
        return

    print_info(f"{t('generating_icon')} {SOURCE_ICON_PNG}")

    if not os.path.exists(SOURCE_ICON_PNG):
        print_warn(t("source_icon_missing"))
        if generate_icon_fallback(ICON_ICO):
            print_success(t("icon_created_fallback"))
        else:
            print_error(t("icon_create_failed"))
        return

    if generate_icon_from_png(SOURCE_ICON_PNG, ICON_ICO):
        print_success(t("icon_created_pillow"))
    elif generate_icon_fallback(ICON_ICO):
        print_success(t("icon_created_fallback"))
    else:
        print_error(t("icon_create_failed"))


def scan_hidden_imports() -> List[str]:
    """Scan project for hidden imports needed by PyInstaller."""
    print_info(t("scanning_imports"))
    imports = set()

    # Always required for MYCELIUM CORE
    imports.update([
        # PyQt6 and Qt extensions
        "PyQt6.sip",
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.QtWidgets",

        # Web3 and Ethereum
        "web3",
        "web3.middleware",
        "web3.providers.rpc",
        "eth_account",
        "eth_account.hdaccount",
        "eth_utils",
        "eth_typing",
        "eth_keys",
        "eth_hash",
        "eth_hash.auto",
        "eth_hash.backends.pysha3",
        "hexbytes",

        # Solidity compiler
        "solcx",
        "solcx.install",

        # QR generation
        "qrcode",
        "qrcode.image.pil",
        "PIL",
        "PIL.Image",
        "PIL.ImageDraw",
        "PIL.ImageFont",

        # Icons
        "qtawesome",
        "qtawesome._icon",

        # Config
        "dotenv",

        # HTTP and protocols
        "requests",
        "websockets",
        "websockets.legacy.client",

        # Crypto
        "cytoolz",
        "lru",
    ])

    # Stdlib and local modules to skip
    stdlib_skip = {
        'os', 'sys', 're', 'time', 'json', 'math', 'hashlib', 'secrets',
        'logging', 'traceback', 'subprocess', 'shutil', 'tempfile', 'uuid',
        'struct', 'argparse', 'locale', 'csv', 'datetime', 'enum',
        'dataclasses', 'typing', '__future__', 'collections', 'pathlib',
        'threading', 'queue', 'io', 'functools', 'itertools', 'contextlib',
        'src',
    }

    # Scan project .py files for additional imports
    py_files = []
    for pkg_rel in PROJECT_PACKAGES:
        pkg_dir = os.path.join(PROJECT_ROOT, pkg_rel)
        if not os.path.isdir(pkg_dir):
            continue
        for root, _, files in os.walk(pkg_dir):
            for file in files:
                if file.endswith(".py"):
                    py_files.append(os.path.join(root, file))

    # Also scan main.py
    main_py = os.path.join(PROJECT_ROOT, "main.py")
    if os.path.exists(main_py):
        py_files.append(main_py)

    for filepath in py_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                matches = re.findall(r'^(?:from|import)\s+([\w.]+)', content, re.MULTILINE)
                for m in matches:
                    top_level = m.split('.')[0]
                    if top_level not in stdlib_skip:
                        imports.add(m)
        except Exception:
            pass

    result = sorted(imports)
    print_info(f"   {t('found_imports')}: {len(result)}")
    return result


def clean_build_dir():
    """Clean build/, *.spec, __pycache__."""
    print_info(t("cleaning_build"))
    try:
        if os.path.exists(BUILD_DIR):
            shutil.rmtree(BUILD_DIR)
        for file in os.listdir(PROJECT_ROOT):
            if file.endswith(".spec"):
                os.remove(os.path.join(PROJECT_ROOT, file))
        for root, dirs, _ in os.walk(PROJECT_ROOT):
            for d in dirs:
                if d in ("__pycache__", ".pytest_cache", ".mypy_cache"):
                    shutil.rmtree(os.path.join(root, d), ignore_errors=True)
        print_success(t("temp_files_cleaned"))
    except Exception as e:
        print_error(f"{t('clean_error')}: {e}")


def clean_dist_dir():
    """Clean dist/ folder."""
    print_info(t("cleaning_dist"))
    try:
        if os.path.exists(DIST_DIR):
            shutil.rmtree(DIST_DIR)
        print_success(t("dist_cleaned"))
    except Exception as e:
        print_error(f"{t('clean_error')}: {e}")


def deep_clean_project():
    """Глубокая очистка: chain-data, logs, exports, runtime, кэши."""
    print_warn(t("deep_clean_warn"))
    confirm = input(f"   {t('deep_clean_confirm')}: ").strip().lower()
    if confirm not in ('y', 'д', 'yes', 'да'):
        print_info(t("deep_clean_aborted"))
        return

    print_info(t("cleaning_project"))

    targets = [
        os.path.join(PROJECT_ROOT, "data", "chain-data", "active"),
        os.path.join(PROJECT_ROOT, "data", "chain-data", "archives"),
        os.path.join(PROJECT_ROOT, "data", "logs", "active"),
        os.path.join(PROJECT_ROOT, "data", "logs", "archive"),
        os.path.join(PROJECT_ROOT, "data", "exports"),
        os.path.join(PROJECT_ROOT, "data", "runtime"),
        BUILD_DIR,
        DIST_DIR,
        os.path.join(PROJECT_ROOT, ".pytest_cache"),
        os.path.join(CONTRACTS_DIR, "abi"),
    ]

    for target in targets:
        if os.path.exists(target):
            try:
                shutil.rmtree(target, ignore_errors=True)
                print(f"  removed: {os.path.relpath(target, PROJECT_ROOT)}")
            except Exception as e:
                print(f"  error:   {os.path.relpath(target, PROJECT_ROOT)}: {e}")

    # __pycache__ рекурсивно
    pycache_count = 0
    for root, dirs, _ in os.walk(PROJECT_ROOT):
        for d in dirs:
            if d in ("__pycache__", ".pytest_cache", ".mypy_cache"):
                full = os.path.join(root, d)
                shutil.rmtree(full, ignore_errors=True)
                pycache_count += 1
    if pycache_count:
        print(f"  removed: {pycache_count} __pycache__ folders")

    # *.spec в корне
    for file in os.listdir(PROJECT_ROOT):
        if file.endswith(".spec"):
            try:
                os.remove(os.path.join(PROJECT_ROOT, file))
                print(f"  removed: {file}")
            except Exception:
                pass

    print_success(t("project_cleaned"))


def build_exe(args=None) -> bool:
    """Main build process."""
    entry_point = find_entry_point()
    if not entry_point:
        print_error(t("entry_not_found"))
        return False

    if not check_pyinstaller():
        return False

    ensure_icon()

    if args is None:
        class _A:
            debug = False
            console = False
            windowed = False
        args = _A()

    ui_mode = resolve_ui_mode(args)
    sep = ";" if sys.platform.startswith("win") else ":"

    hidden_imports = scan_hidden_imports()
    hidden_args = []
    for imp in hidden_imports:
        hidden_args.extend(["--hidden-import", imp])

    # Data files: themes, i18n, contracts, icons
    add_data = []

    if os.path.exists(THEMES_DIR):
        add_data.append(f"{THEMES_DIR}{sep}src/ui/themes")

    if os.path.exists(I18N_DIR):
        add_data.append(f"{I18N_DIR}{sep}src/ui/i18n")

    if os.path.exists(CONTRACTS_DIR):
        sol_file = os.path.join(CONTRACTS_DIR, "VotingCore.sol")
        if os.path.exists(sol_file):
            add_data.append(f"{sol_file}{sep}contracts")

    if os.path.exists(ICONS_DIR):
        add_data.append(f"{ICONS_DIR}{sep}src/assets/icons")

    # Build PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm", "--onefile", "--clean",
        "--name", PROJECT_NAME,
        "--distpath", DIST_DIR,
        "--workpath", BUILD_DIR,
        "--specpath", BUILD_DIR,
        "--paths", PROJECT_ROOT,
    ]

    cmd.append("--windowed" if ui_mode == "windowed" else "--console")

    if getattr(args, "debug", False):
        cmd += ["--log-level", "DEBUG"]

    if os.path.exists(ICON_ICO):
        cmd.extend(["--icon", ICON_ICO])

    # Collect package data for libraries with runtime files
    cmd += ["--collect-all", "qtawesome"]
    cmd += ["--collect-all", "web3"]
    cmd += ["--collect-data", "solcx"]
    cmd += ["--collect-submodules", "eth_account"]
    cmd += ["--collect-submodules", "PyQt6"]

    cmd.extend(hidden_args)

    for data in add_data:
        cmd.extend(["--add-data", data])

    cmd.append(entry_point)

    # Print build info
    print_section(t("starting_pyinstaller"))
    print(f"Project:  {PROJECT_NAME}")
    print(f"Entry:    {os.path.basename(entry_point)}")
    print(f"Icon:     {t('yes') if os.path.exists(ICON_ICO) else t('no')}")
    print(f"UI mode:  {ui_mode}")
    print(f"Debug:    {'YES' if getattr(args, 'debug', False) else 'NO'}")
    print(f"Imports:  {len(hidden_imports)} hidden")
    print(f"Data:     {len(add_data)} folders")

    print_warn(t("warn_geth_external"))
    print(f"          {t('warn_geth_distribute')}")

    os.makedirs(BUILD_DIR, exist_ok=True)
    log_file = os.path.join(BUILD_DIR, "build.log")
    start_time = time.time()

    try:
        with open(log_file, "w", encoding="utf-8") as log:
            process = subprocess.run(
                cmd,
                capture_output=True, text=True,
                encoding="utf-8", errors="replace",
                timeout=900  # 15 minutes
            )
            log.write(process.stdout)
            log.write("\n=== STDERR ===\n")
            log.write(process.stderr)

        if process.returncode == 0:
            elapsed = time.time() - start_time
            print_success(f"{t('build_complete')} {elapsed:.1f} {t('sec')}!")
            print(f"  {t('file_label')}: {EXE_PATH}")
            if os.path.exists(EXE_PATH):
                size = os.path.getsize(EXE_PATH) / (1024 * 1024)
                print(f"  {t('size_label')}: {size:.2f} MB")
            print()
            compute_checksums(show_github=True)
            return True

        print_error(t("build_error"))
        print_section(t("last_errors"))
        for line in process.stderr.splitlines()[-25:]:
            print(f"  {line}")
        print_info(f"{t('full_log')}: {log_file}")
        return False

    except subprocess.TimeoutExpired:
        print_error(t("build_timeout"))
        return False
    except Exception as e:
        print_error(f"{t('critical_error')}: {e}")
        return False


# ════════════════════ MENU ════════════════════

def interactive_menu():
    """Interactive text menu."""
    while True:
        clear_screen()
        entry = find_entry_point()
        entry_name = os.path.basename(entry) if entry else f"{t('status_not_found')}"
        icon_status = t('status_yes') if os.path.exists(ICON_ICO) else t('status_no')
        exe_info = get_file_info(EXE_PATH)
        lang_indicator = "RU" if CURRENT_LANG == "ru" else "EN"

        print_header(f"{t('menu_title')} [{lang_indicator}]")
        print(f"  {t('menu_root')}:  {PROJECT_ROOT}")
        print(f"  {t('menu_entry')}: {entry_name}")
        print(f"  {t('menu_icon')}:  {icon_status}")
        print(f"  {t('menu_exe')}:   {exe_info}")
        print("-" * 64)
        print(f"  1. {t('opt_build')}")
        print(f"  2. {t('opt_regen_icon')}")
        print(f"  3. {t('opt_checksums')}")
        print(f"  4. {t('opt_clean_build')}")
        print(f"  5. {t('opt_clean_dist')}")
        print(f"  6. {t('opt_clean_all')}")
        print(f"  7. {t('opt_clean_project')}")
        print(f"  8. {t('opt_change_lang')}")
        print(f"  q. {t('opt_exit')}")
        print("-" * 64)

        choice = input(f" {t('menu_choice')}: ").strip().lower()

        if choice == '1':
            build_exe()
            pause()
        elif choice == '2':
            if os.path.exists(ICON_ICO):
                os.remove(ICON_ICO)
            ensure_icon()
            pause()
        elif choice == '3':
            compute_checksums(show_github=True)
            pause()
        elif choice == '4':
            clean_build_dir()
            pause()
        elif choice == '5':
            clean_dist_dir()
            pause()
        elif choice == '6':
            clean_build_dir()
            clean_dist_dir()
            pause()
        elif choice == '7':
            deep_clean_project()
            pause()
        elif choice == '8':
            prompt_language_selection()
        elif choice in ('q', 'й'):
            print(f"\n{t('goodbye')}")
            if os.path.exists(DIST_DIR) and os.listdir(DIST_DIR):
                print(f"{t('ready_files')}: {DIST_DIR}")
                if sys.platform == 'win32':
                    os.startfile(DIST_DIR)
            break
        else:
            print_warn(t("invalid_choice"))
            time.sleep(1)


def main():
    """Entry point."""
    parser = argparse.ArgumentParser(description=f"{PROJECT_NAME} Builder")
    parser.add_argument("--build", action="store_true", help="Build EXE without menu")
    parser.add_argument("--clean", action="store_true", help="Clean build folder")
    parser.add_argument("--clean-all", action="store_true", help="Clean build + dist")
    parser.add_argument("--clean-project", action="store_true", help="Deep clean (chain, logs, cache)")
    parser.add_argument("--checksums", action="store_true", help="Show SHA-256")
    parser.add_argument("--lang", choices=["ru", "en"], help="Set language")
    parser.add_argument("--debug", action="store_true", help="Debug build (console mode)")
    ui_group = parser.add_mutually_exclusive_group()
    ui_group.add_argument("--console", action="store_true", help="Force console mode")
    ui_group.add_argument("--windowed", action="store_true", help="Force windowed mode")

    args = parser.parse_args()

    if args.lang:
        set_language(args.lang)
    else:
        set_language(detect_system_language())

    os.makedirs(ICONS_DIR, exist_ok=True)

    if args.build:
        build_exe(args)
    elif args.clean:
        clean_build_dir()
    elif args.clean_all:
        clean_build_dir()
        clean_dist_dir()
    elif args.clean_project:
        deep_clean_project()
    elif args.checksums:
        compute_checksums(show_github=True)
    else:
        prompt_language_selection()
        interactive_menu()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{t('operation_cancelled')}")
        sys.exit(0)