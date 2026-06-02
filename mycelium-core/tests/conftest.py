"""
Pytest bootstrap.

Добавляет корень проекта в sys.path ДО любого импорта тестовых модулей.
Это нужно чтобы импорты вида `from src.core...` работали независимо
от того, откуда запущен pytest.
"""
import sys
from pathlib import Path

# Корень проекта = на уровень выше tests/
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Вставляем В НАЧАЛО sys.path, чтобы наш src имел приоритет
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))