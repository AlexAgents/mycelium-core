"""
fix_svg_bg.py — Добавляет белый фон в SVG-файлы диаграмм.

Читает размеры из атрибутов SVG и вставляет rect с точными координатами.

Использование:
    python docs/scripts/fix_svg_bg.py
    python docs/scripts/fix_svg_bg.py --revert  # убрать добавленный фон
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DIAGRAMS_DIR = SCRIPT_DIR.parent / "src" / "assets" / "diagrams"

MARKER = '<!-- MYCELIUM-BG -->'


def get_svg_dimensions(svg_tag: str) -> tuple[str, str]:
    """Извлекает width и height из тега <svg>."""
    w_match = re.search(r'width="([^"]+)"', svg_tag)
    h_match = re.search(r'height="([^"]+)"', svg_tag)

    width = w_match.group(1) if w_match else "100%"
    height = h_match.group(1) if h_match else "100%"

    return width, height


def get_viewbox(svg_tag: str) -> tuple[str, str, str, str] | None:
    """Извлекает viewBox если есть."""
    vb_match = re.search(r'viewBox="([^"]+)"', svg_tag)
    if vb_match:
        parts = vb_match.group(1).split()
        if len(parts) == 4:
            return tuple(parts)
    return None


def fix_svg(filepath: Path) -> bool:
    """Добавляет белый фон в SVG. Возвращает True если файл изменён."""
    content = filepath.read_text(encoding='utf-8')

    if MARKER in content:
        return False

    pattern = re.compile(r'(<svg[^>]*>)', re.IGNORECASE | re.DOTALL)
    match = pattern.search(content)

    if not match:
        print(f"  SKIP (no <svg> tag): {filepath.name}")
        return False

    svg_tag = match.group(1)
    width, height = get_svg_dimensions(svg_tag)
    viewbox = get_viewbox(svg_tag)

    if viewbox:
        vb_x, vb_y, vb_w, vb_h = viewbox
        bg_rect = (
            f'{MARKER}\n'
            f'<rect x="{vb_x}" y="{vb_y}" '
            f'width="{vb_w}" height="{vb_h}" '
            f'fill="white"/>'
        )
    else:
        bg_rect = (
            f'{MARKER}\n'
            f'<rect x="0" y="0" '
            f'width="{width}" height="{height}" '
            f'fill="white"/>'
        )

    insert_pos = match.end()
    new_content = (
        content[:insert_pos]
        + '\n' + bg_rect + '\n'
        + content[insert_pos:]
    )

    filepath.write_text(new_content, encoding='utf-8')
    return True


def revert_svg(filepath: Path) -> bool:
    """Удаляет добавленный фон. Возвращает True если файл изменён."""
    content = filepath.read_text(encoding='utf-8')

    if MARKER not in content:
        return False

    lines = content.split('\n')
    new_lines = []
    skip_next = False

    for line in lines:
        if MARKER in line:
            skip_next = True
            continue
        if skip_next and '<rect' in line and 'fill="white"' in line:
            skip_next = False
            continue
        skip_next = False
        new_lines.append(line)

    cleaned = '\n'.join(new_lines)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

    filepath.write_text(cleaned, encoding='utf-8')
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Add white background to SVG diagrams"
    )
    parser.add_argument(
        '--revert', action='store_true',
        help='Remove previously added backgrounds'
    )
    args = parser.parse_args()

    print("=" * 60)
    if args.revert:
        print("  MYCELIUM CORE -- SVG Background Remover")
    else:
        print("  MYCELIUM CORE -- SVG Background Fixer")
    print("=" * 60)
    print()

    if not DIAGRAMS_DIR.exists():
        print(f"ERROR: diagrams dir not found: {DIAGRAMS_DIR}")
        sys.exit(1)

    svg_files = sorted(DIAGRAMS_DIR.rglob('*.svg'))
    changed = 0
    skipped = 0

    for svg in svg_files:
        rel = svg.relative_to(DIAGRAMS_DIR)
        if args.revert:
            if revert_svg(svg):
                print(f"  [REVERTED] {rel}")
                changed += 1
            else:
                skipped += 1
        else:
            if fix_svg(svg):
                print(f"  [FIXED] {rel}")
                changed += 1
            else:
                skipped += 1

    print()
    print(f"Total SVG files: {len(svg_files)}")
    print(f"Changed: {changed}")
    print(f"Skipped: {skipped}")
    print()


if __name__ == "__main__":
    main()