#!/usr/bin/env bash
# ============================================================
# MYCELIUM CORE - Project deep clean (Linux/macOS)
# ============================================================
# Удаляет: chain-data, logs, exports, runtime, build, dist,
#          __pycache__, .pytest_cache, *.spec, ABI артефакты
# Не трогает: .env, app.cfg, исходный код, тесты, bin/geth
# ============================================================

set -u

# Перейти в корень проекта (на уровень выше scripts/)
SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$( cd -- "$SCRIPT_DIR/.." &> /dev/null && pwd )"
cd "$PROJECT_ROOT" || exit 1

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

# Parse args
FORCE=0
QUIET=0
for arg in "$@"; do
    case $arg in
        -f|--force)  FORCE=1 ;;
        -q|--quiet)  QUIET=1 ;;
        -h|--help)
            echo "Usage: $0 [-f|--force] [-q|--quiet] [-h|--help]"
            echo "  -f, --force   Skip confirmation"
            echo "  -q, --quiet   Minimal output"
            echo "  -h, --help    Show this help"
            exit 0
            ;;
    esac
done

print_step() {
    local status="$1"
    local text="$2"
    case "$status" in
        OK)   echo -e "  ${GREEN}[OK]${NC}   $text" ;;
        FAIL) echo -e "  ${RED}[FAIL]${NC} $text" ;;
        WARN) echo -e "  ${YELLOW}[WARN]${NC} $text" ;;
        *)    echo -e "  [$status] $text" ;;
    esac
}

remove_if_exists() {
    local path="$1"
    local label="${2:-$path}"
    if [[ -e "$path" ]]; then
        if rm -rf "$path" 2>/dev/null; then
            print_step "OK" "$label"
            return 0
        else
            print_step "FAIL" "$label (permission denied)"
            return 1
        fi
    fi
    return 0
}

# Header
if [[ $QUIET -eq 0 ]]; then
    echo ""
    echo -e "${CYAN}============================================================${NC}"
    echo -e "${CYAN}  MYCELIUM CORE - Project Clean${NC}"
    echo -e "${GRAY}  Working dir: $(pwd)${NC}"
    echo -e "${CYAN}============================================================${NC}"
    echo ""
    echo -e "${YELLOW}  WARNING: this will delete:${NC}"
    echo "    - data/chain-data/ (blockchain state)"
    echo "    - data/logs/       (all session logs)"
    echo "    - data/exports/    (exported JSON/CSV)"
    echo "    - data/runtime/    (cache)"
    echo "    - build/           (PyInstaller temp)"
    echo "    - dist/            (built EXE)"
    echo "    - contracts/abi/   (compiled artifacts)"
    echo "    - All __pycache__/ folders"
    echo "    - All .pytest_cache, .mypy_cache folders"
    echo "    - *.spec files"
    echo ""
    echo -e "${GREEN}  WILL NOT TOUCH:${NC}"
    echo "    - .env, app.cfg (your config)"
    echo "    - src/, contracts/VotingCore.sol (source code)"
    echo "    - tests/ (tests)"
    echo "    - bin/geth (binary)"
    echo ""
fi

# Confirmation
if [[ $FORCE -eq 0 ]]; then
    read -r -p "Continue? [y/N]: " CONFIRM
    if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Cancelled.${NC}"
        exit 0
    fi
fi

echo ""
echo -e "${CYAN}Cleaning...${NC}"
echo -e "${GRAY}------------------------------------------------------------${NC}"

# Static folders
remove_if_exists "data/chain-data/active"     "data/chain-data/active"
remove_if_exists "data/chain-data/archives"   "data/chain-data/archives"
remove_if_exists "data/logs/active"           "data/logs/active"
remove_if_exists "data/logs/archive"          "data/logs/archive"
remove_if_exists "data/exports"               "data/exports"
remove_if_exists "data/runtime"               "data/runtime"
remove_if_exists "build"                      "build/"
remove_if_exists "dist"                       "dist/"
remove_if_exists "contracts/abi"              "contracts/abi/"
remove_if_exists ".pytest_cache"              ".pytest_cache"

# Recursive __pycache__ removal
PYCACHE_COUNT=$(find . -type d -name "__pycache__" 2>/dev/null | wc -l)
if [[ $PYCACHE_COUNT -gt 0 ]]; then
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
    print_step "OK" "Removed $PYCACHE_COUNT __pycache__ folders"
fi

# Recursive .mypy_cache removal
MYPY_COUNT=$(find . -type d -name ".mypy_cache" 2>/dev/null | wc -l)
if [[ $MYPY_COUNT -gt 0 ]]; then
    find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null
    print_step "OK" "Removed $MYPY_COUNT .mypy_cache folders"
fi

# *.spec files in root
SPEC_FILES=$(find . -maxdepth 1 -type f -name "*.spec" 2>/dev/null)
if [[ -n "$SPEC_FILES" ]]; then
    while IFS= read -r f; do
        if rm -f "$f" 2>/dev/null; then
            print_step "OK" "$(basename "$f")"
        else
            print_step "FAIL" "$(basename "$f")"
        fi
    done <<< "$SPEC_FILES"
fi

# *.pyc files recursively
PYC_COUNT=$(find . -type f -name "*.pyc" 2>/dev/null | wc -l)
if [[ $PYC_COUNT -gt 0 ]]; then
    find . -type f -name "*.pyc" -delete 2>/dev/null
    print_step "OK" "Removed $PYC_COUNT .pyc files"
fi

echo -e "${GRAY}------------------------------------------------------------${NC}"
echo ""
echo -e "${GREEN}Done!${NC}"
echo ""

if [[ $QUIET -eq 0 ]]; then
    echo -e "${CYAN}To start fresh:${NC}"
    echo "  1. python main.py"
    echo "  2. Deploy contract again"
    echo ""
fi