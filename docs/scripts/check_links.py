"""
check_links.py — Проверка консистентности ссылок в MD-файлах.

Правила:
1. В *.md (EN) файлах не должно быть ссылок на .ru.md
2. В *.ru.md (RU) файлах все внутренние .md ссылки должны вести на .ru.md
3. Все внутренние ссылки должны указывать на существующие файлы
4. Внешние ссылки (http/https), якоря (#) и не-MD файлы игнорируются

Использование:
    python docs/scripts/check_links.py              # проверка
    python docs/scripts/check_links.py --fix         # автоисправление
    python docs/scripts/check_links.py --verbose     # подробный вывод
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple

SCRIPT_DIR = Path(__file__).resolve().parent
DOCS_SRC = SCRIPT_DIR.parent / "src"

LINK_PATTERN = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')

SKIP_EXTENSIONS = {
    '.png', '.svg', '.jpg', '.jpeg', '.gif',
    '.bpmn', '.puml', '.iuml',
    '.css', '.json', '.txt', '.log',
    '.sol', '.py', '.qss', '.cfg',
    '.ico', '.bmp',
}


class LinkIssue(NamedTuple):
    filepath: Path
    line_num: int
    link_text: str
    href: str
    issue_type: str    # WRONG_LANG | MISSING_FILE | MISSING_RU_VERSION
    suggestion: str    # предлагаемое исправление или пояснение
    fixable: bool


def is_internal_md_link(href: str) -> bool:
    """Проверяет что ссылка ведёт на внутренний MD-файл."""
    if href.startswith(('http://', 'https://', '#', 'mailto:')):
        return False
    clean = href.split('#')[0]
    if not clean:
        return False
    lower = clean.lower()
    for ext in SKIP_EXTENSIONS:
        if lower.endswith(ext):
            return False
    return lower.endswith('.md')


def resolve_target(source_file: Path, href: str) -> Path:
    """Вычисляет абсолютный путь к целевому файлу."""
    clean = href.split('#')[0]
    if clean.startswith('/'):
        return DOCS_SRC / clean.lstrip('/')
    return (source_file.parent / clean).resolve()


def check_file(filepath: Path) -> list[LinkIssue]:
    """Проверяет один файл. Возвращает список проблем."""
    issues = []
    is_ru = filepath.name.endswith('.ru.md')
    content = filepath.read_text(encoding='utf-8')
    lines = content.split('\n')

    for line_num, line in enumerate(lines, 1):
        for match in LINK_PATTERN.finditer(line):
            link_text = match.group(1)
            href = match.group(2)

            if not is_internal_md_link(href):
                continue

            clean_href = href.split('#')[0]
            anchor = '#' + href.split('#')[1] if '#' in href else ''

            # ── Проверка 1: файл существует? ──────────────────
            target_path = resolve_target(filepath, clean_href)
            target_exists = target_path.exists()

            if is_ru:
                # RU файл ссылается на EN (.md вместо .ru.md)
                if clean_href.endswith('.md') and not clean_href.endswith('.ru.md'):
                    ru_href = clean_href[:-3] + '.ru.md'
                    ru_target = resolve_target(filepath, ru_href)
                    ru_exists = ru_target.exists()

                    if ru_exists:
                        # RU версия существует — можно исправить
                        issues.append(LinkIssue(
                            filepath=filepath,
                            line_num=line_num,
                            link_text=link_text,
                            href=href,
                            issue_type="WRONG_LANG",
                            suggestion=f"{ru_href}{anchor}",
                            fixable=True,
                        ))
                    else:
                        # RU версии нет — нельзя исправить автоматически
                        if target_exists:
                            issues.append(LinkIssue(
                                filepath=filepath,
                                line_num=line_num,
                                link_text=link_text,
                                href=href,
                                issue_type="MISSING_RU_VERSION",
                                suggestion=f"EN file exists but {ru_href} does not. "
                                           f"Create RU version or keep EN link.",
                                fixable=False,
                            ))
                        else:
                            issues.append(LinkIssue(
                                filepath=filepath,
                                line_num=line_num,
                                link_text=link_text,
                                href=href,
                                issue_type="MISSING_FILE",
                                suggestion=f"Neither {clean_href} nor {ru_href} exists.",
                                fixable=False,
                            ))
                elif clean_href.endswith('.ru.md'):
                    # RU файл ссылается на .ru.md — правильно, но проверим существование
                    if not target_exists:
                        issues.append(LinkIssue(
                            filepath=filepath,
                            line_num=line_num,
                            link_text=link_text,
                            href=href,
                            issue_type="MISSING_FILE",
                            suggestion=f"Target file {clean_href} does not exist.",
                            fixable=False,
                        ))
            else:
                # EN файл ссылается на .ru.md
                if clean_href.endswith('.ru.md'):
                    en_href = clean_href.replace('.ru.md', '.md')
                    en_target = resolve_target(filepath, en_href)

                    if en_target.exists():
                        issues.append(LinkIssue(
                            filepath=filepath,
                            line_num=line_num,
                            link_text=link_text,
                            href=href,
                            issue_type="WRONG_LANG",
                            suggestion=f"{en_href}{anchor}",
                            fixable=True,
                        ))
                    else:
                        issues.append(LinkIssue(
                            filepath=filepath,
                            line_num=line_num,
                            link_text=link_text,
                            href=href,
                            issue_type="MISSING_FILE",
                            suggestion=f"EN version {en_href} does not exist.",
                            fixable=False,
                        ))
                elif clean_href.endswith('.md'):
                    # EN файл ссылается на .md — правильно, но проверим существование
                    if not target_exists:
                        issues.append(LinkIssue(
                            filepath=filepath,
                            line_num=line_num,
                            link_text=link_text,
                            href=href,
                            issue_type="MISSING_FILE",
                            suggestion=f"Target file {clean_href} does not exist.",
                            fixable=False,
                        ))

    return issues


def apply_fixes(filepath: Path, issues: list[LinkIssue]) -> int:
    """Применяет исправления к файлу. Возвращает количество исправлений."""
    fixable = [i for i in issues if i.fixable and i.filepath == filepath]
    if not fixable:
        return 0

    content = filepath.read_text(encoding='utf-8')
    fixed_count = 0

    for issue in fixable:
        old = f']({issue.href})'
        new = f']({issue.suggestion})'
        if old in content:
            content = content.replace(old, new, 1)
            fixed_count += 1

    if fixed_count > 0:
        filepath.write_text(content, encoding='utf-8')

    return fixed_count


def print_issues(issues: list[LinkIssue], verbose: bool = False) -> None:
    """Выводит проблемы сгруппированные по типу."""

    fixable = [i for i in issues if i.fixable]
    unfixable = [i for i in issues if not i.fixable]
    wrong_lang = [i for i in issues if i.issue_type == "WRONG_LANG"]
    missing_file = [i for i in issues if i.issue_type == "MISSING_FILE"]
    missing_ru = [i for i in issues if i.issue_type == "MISSING_RU_VERSION"]

    # ── FIXABLE: Wrong Language ──────────────────────────
    if wrong_lang:
        print()
        print("-" * 60)
        print(f"  FIXABLE: Wrong language links ({len(wrong_lang)})")
        print(f"  Run with --fix to auto-correct")
        print("-" * 60)

        for issue in wrong_lang:
            rel = issue.filepath.relative_to(DOCS_SRC)
            lang = "RU->EN" if issue.filepath.name.endswith('.ru.md') else "EN->RU"
            print(f"  {rel}:{issue.line_num}")
            print(f"    {lang}: [{issue.link_text}]({issue.href})")
            print(f"    FIX:   [{issue.link_text}]({issue.suggestion})")
            if verbose:
                print(f"    Type:  {issue.issue_type}")
            print()

    # ── UNFIXABLE: Missing RU version ────────────────────
    if missing_ru:
        print()
        print("-" * 60)
        print(f"  MANUAL: Missing RU version ({len(missing_ru)})")
        print(f"  Create .ru.md files or intentionally keep EN links")
        print("-" * 60)

        for issue in missing_ru:
            rel = issue.filepath.relative_to(DOCS_SRC)
            print(f"  {rel}:{issue.line_num}")
            print(f"    Link:   [{issue.link_text}]({issue.href})")
            print(f"    Reason: {issue.suggestion}")
            if verbose:
                target = resolve_target(issue.filepath, issue.href.split('#')[0])
                print(f"    Target: {target}")
                print(f"    Exists: {target.exists()}")
            print()

    # ── UNFIXABLE: Missing file ──────────────────────────
    if missing_file:
        print()
        print("-" * 60)
        print(f"  BROKEN: Missing target files ({len(missing_file)})")
        print(f"  These links point to files that do not exist")
        print("-" * 60)

        for issue in missing_file:
            rel = issue.filepath.relative_to(DOCS_SRC)
            print(f"  {rel}:{issue.line_num}")
            print(f"    Link:   [{issue.link_text}]({issue.href})")
            print(f"    Reason: {issue.suggestion}")
            if verbose:
                target = resolve_target(issue.filepath, issue.href.split('#')[0])
                print(f"    Resolved: {target}")
            print()


def main():
    parser = argparse.ArgumentParser(
        description="Check MD link consistency (EN/RU)"
    )
    parser.add_argument(
        '--fix', action='store_true',
        help='Auto-fix wrong language links where target exists'
    )
    parser.add_argument(
        '--verbose', '-v', action='store_true',
        help='Show detailed information for each issue'
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  MYCELIUM CORE -- MD Link Checker")
    print("=" * 60)

    if not DOCS_SRC.exists():
        print(f"\nERROR: docs/src/ not found at {DOCS_SRC}")
        sys.exit(1)

    md_files = sorted(DOCS_SRC.rglob('*.md'))
    all_issues: list[LinkIssue] = []
    files_with_issues = set()

    print(f"\nScanning {len(md_files)} files...")

    for filepath in md_files:
        issues = check_file(filepath)
        if issues:
            all_issues.extend(issues)
            files_with_issues.add(filepath)

    # ── Summary ──────────────────────────────────────────
    fixable = [i for i in all_issues if i.fixable]
    unfixable = [i for i in all_issues if not i.fixable]
    wrong_lang = [i for i in all_issues if i.issue_type == "WRONG_LANG"]
    missing_file = [i for i in all_issues if i.issue_type == "MISSING_FILE"]
    missing_ru = [i for i in all_issues if i.issue_type == "MISSING_RU_VERSION"]

    print()
    print("=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    print(f"  Total files scanned:     {len(md_files)}")
    print(f"  Files with issues:       {len(files_with_issues)}")
    print(f"  Total issues:            {len(all_issues)}")
    print(f"    Wrong language:        {len(wrong_lang)}  (auto-fixable)")
    print(f"    Missing RU version:    {len(missing_ru)}  (manual)")
    print(f"    Missing target file:   {len(missing_file)}  (broken)")
    print(f"  Auto-fixable:            {len(fixable)}")
    print(f"  Requires manual action:  {len(unfixable)}")

    # ── Details ──────────────────────────────────────────
    if all_issues:
        print_issues(all_issues, verbose=args.verbose)

    # ── Apply fixes ──────────────────────────────────────
    if args.fix and fixable:
        print()
        print("=" * 60)
        print("  APPLYING FIXES")
        print("=" * 60)

        total_fixed = 0
        fixed_files = set()

        for filepath in files_with_issues:
            file_issues = [i for i in fixable if i.filepath == filepath]
            if file_issues:
                count = apply_fixes(filepath, file_issues)
                if count > 0:
                    rel = filepath.relative_to(DOCS_SRC)
                    print(f"  [FIXED] {rel}: {count} link(s)")
                    total_fixed += count
                    fixed_files.add(filepath)

        print()
        print(f"  Fixed {total_fixed} links in {len(fixed_files)} files.")

        if unfixable:
            print(f"  {len(unfixable)} issues require manual attention (see above).")

    elif args.fix and not fixable:
        print("\n  Nothing to auto-fix.")

    # ── Exit code ────────────────────────────────────────
    if not all_issues:
        print("\n  OK: All links are consistent.")
        sys.exit(0)
    elif args.fix and not unfixable:
        print("\n  OK: All fixable issues resolved.")
        sys.exit(0)
    else:
        remaining = len(unfixable) if args.fix else len(all_issues)
        print(f"\n  {remaining} issue(s) remain.")
        if not args.fix and fixable:
            print("  Run with --fix to auto-correct fixable issues.")
        sys.exit(1)


if __name__ == "__main__":
    main()