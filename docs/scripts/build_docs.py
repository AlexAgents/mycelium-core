"""
build_docs.py — Оркестратор сборки документации.
Находит mkdocs.yml в корне, собирает диаграммы и запускает локальный сервер.
"""
from __future__ import annotations
import os
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
DOCS_ROOT = SCRIPTS_DIR.parent

CONFIG_PATH = DOCS_ROOT / "mkdocs.yml"

def main() -> None:
    # 1. Сборка диаграмм
    gen_script = SCRIPTS_DIR / "generate_diagrams.py"
    if gen_script.exists():
        try:
            subprocess.run([sys.executable, str(gen_script)], check=True)
        except subprocess.CalledProcessError:
            print("\n[WARN] Ошибка при сборке диаграмм. Продолжаем запуск MkDocs...\n")
    else:
        print("[WARN] Скрипт генерации диаграмм не найден.")

    if not CONFIG_PATH.exists():
        print(f"[ERROR] Конфигурационный файл 'mkdocs.yml' не найден по пути: {CONFIG_PATH}")
        sys.exit(1)

    print(f"\n[INFO] Найдена конфигурация: {CONFIG_PATH}")
    print("Запуск локального сервера документации MkDocs...")
    print("Для остановки сервера нажмите Ctrl+C\n")

    # Переходим в директорию, где лежит mkdocs.yml
    os.chdir(str(CONFIG_PATH.parent))

    try:
        # Запускаем MkDocs (требует установленного пакета mkdocs)
        subprocess.run(["mkdocs", "serve"], check=True)
    except KeyboardInterrupt:
        print("\n[INFO] Сервер остановлен.")
    except FileNotFoundError:
        print("[ERROR] MkDocs не установлен.")
        print(" Выполните команду: pip install -r requirements-docs.txt")
        sys.exit(1)
    except Exception as exc:
        print(f"[ERROR] Не удалось запустить MkDocs: {exc}")
        sys.exit(1)

if __name__ == "__main__":
    main()