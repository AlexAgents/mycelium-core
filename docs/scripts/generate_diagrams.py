"""
generate_diagrams.py — Скрипт компиляции PlantUML-диаграмм.
Компилирует .puml и .ru.puml в SVG и PNG.
"""
from __future__ import annotations
import argparse
import os
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
DOCS_ROOT = SCRIPTS_DIR.parent

PUML_SRC_DIR = DOCS_ROOT / "src" / "diagrams" / "sources" / "uml"
DOCS_ASSETS_DIR = DOCS_ROOT / "src" / "assets" / "diagrams"

JAR_CANDIDATES = [
    DOCS_ROOT / "plantuml.jar",
    DOCS_ROOT.parent / "plantuml.jar",
]

ACTIVE_JAR = None
for candidate in JAR_CANDIDATES:
    if candidate.exists():
        ACTIVE_JAR = candidate
        break

def check_java() -> bool:
    try:
        subprocess.run(["java", "-version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def get_plantuml_command(src_path: Path, output_dir: Path, fmt: str) -> list[str]:
    if ACTIVE_JAR:
        return [
            "java", "-jar", str(ACTIVE_JAR),
            "-charset", "UTF-8",
            f"-t{fmt}",
            "-o", str(output_dir),
            str(src_path)
        ]
    else:
        return [
            "plantuml",
            "-charset", "UTF-8",
            f"-t{fmt}",
            "-o", str(output_dir),
            str(src_path)
        ]

def should_compile(src_path: Path, output_dir: Path, force: bool) -> bool:
    """Определяет, нужно ли компилировать файл на основе mtime."""
    if force:
        return True
    
    svg_path = output_dir / f"{src_path.stem}.svg"
    png_path = output_dir / f"{src_path.stem}.png"
    
    if not svg_path.exists() or not png_path.exists():
        return True
        
    src_mtime = src_path.stat().st_mtime
    if src_mtime > svg_path.stat().st_mtime or src_mtime > png_path.stat().st_mtime:
        return True
        
    return False

def compile_file(src_path: Path, force: bool = False) -> str:
    """Компилирует один puml-файл."""
    try:
        rel_dir = src_path.parent.relative_to(PUML_SRC_DIR)
        output_dir = DOCS_ASSETS_DIR / rel_dir
    except ValueError:
        output_dir = DOCS_ASSETS_DIR
        
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not should_compile(src_path, output_dir, force):
        return "skipped"
        
    success = True
    for fmt in ("svg", "png"):
        cmd = get_plantuml_command(src_path, output_dir, fmt)
        try:
            subprocess.run(cmd, capture_output=True, check=True)
        except subprocess.CalledProcessError as exc:
            print(f" [FAIL] {src_path.name} ({fmt}): {exc.stderr.decode('utf-8', errors='ignore').strip()}")
            success = False
        except FileNotFoundError:
            print(f" [FAIL] {src_path.name} ({fmt}): Java or system PlantUML not found")
            return "failed"
            
    if success:
        print(f" [OK] {src_path.name} -> {output_dir.relative_to(DOCS_ROOT)}")
        return "compiled"
    return "failed"

def main() -> None:
    parser = argparse.ArgumentParser(description="PlantUML Differential Compiler")
    parser.add_argument("--force", "-f", action="store_true", help="Force rebuild all diagrams")
    args = parser.parse_args()
    
    print("=" * 64)
    print(" MYCELIUM CORE - PlantUML Compiler (Incremental)")
    print("=" * 64)
    
    if not check_java():
        print("[ERROR] Java Runtime Environment (JRE) не найден в PATH.")
        sys.exit(1)
        
    if not PUML_SRC_DIR.exists():
        print(f"[ERROR] Папка исходных диаграмм не найдена: {PUML_SRC_DIR}")
        sys.exit(1)
        
    puml_files = []
    for root, _, files in os.walk(PUML_SRC_DIR):
        root_path = Path(root)
        if "_common" in root_path.parts:
            continue
        for file in files:
            # Компилируем .puml и .ru.puml, игнорируем .iuml (файлы тем)
            if file.endswith(".puml") and not file.startswith("_"):
                puml_files.append(root_path / file)
                
    if not puml_files:
        print("[INFO] Файлы для компиляции (.puml) не обнаружены.")
        sys.exit(0)
        
    print(f"Обнаружено диаграмм для сборки: {len(puml_files)}")
    print("-" * 64)
    
    compiled, skipped, failed = 0, 0, 0
    for f in puml_files:
        status = compile_file(f, args.force)
        if status == "compiled": compiled += 1
        elif status == "skipped": skipped += 1
        else: failed += 1
            
    print("-" * 64)
    print(f"Результаты: скомпилировано={compiled}, пропущено={skipped}, ошибок={failed}")
    print("=" * 64)

if __name__ == "__main__":
    main()