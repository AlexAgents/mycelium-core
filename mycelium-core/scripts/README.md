# Scripts

Служебные скрипты для разработки и сборки MYCELIUM CORE.

Все скрипты запускаются из корня проекта и работают с путями
относительно корня.

## Файлы

| Файл | ОС | Назначение |
|---|---|---|
| `builder.py` | Все | Сборка EXE через PyInstaller |
| `clean.bat` | Windows | Глубокая очистка проекта (CMD) |
| `clean.ps1` | Windows | Глубокая очистка проекта (PowerShell) |
| `clean.sh` | Linux/macOS | Глубокая очистка проекта (Bash) |

## Использование

### Сборка EXE

```bash
python scripts/builder.py                # интерактивное меню
python scripts/builder.py --build        # без меню
python scripts/builder.py --checksums    # SHA-256
python scripts/builder.py --clean-all    # очистка build/ + dist/
python scripts/builder.py --help
```