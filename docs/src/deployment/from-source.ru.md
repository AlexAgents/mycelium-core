# Сборка из исходников

Настройка среды разработки для **MYCELIUM CORE**.

---

## Предусловия

- Python 3.11+
- Git
- Бинарник Geth (см. [Установка](../getting-started/installation.ru.md))

---

## Клонирование и установка

```bash
git clone <repository-url> mycelium-core
cd mycelium-core
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/macOS
pip install -r requirements.txt
```

---

## Структура проекта

```text
mycelium-core/
├── main.py                     # Точка входа
├── app.cfg                     # Пользовательские настройки (автогенерация)
├── .env                        # Конфигурация окружения (gitignored)
├── .env.example                # Шаблон окружения
├── pytest.ini                  # Конфигурация тестов
├── requirements.txt            # Зависимости Python
├── readme.ru.md                # Описание проекта
├── .gitignore                  # Исключения Git
│
├── bin/                        # Бинарные файлы
│   └── geth.exe                # Локальный узел Geth
│
├── contracts/                  # Смарт-контракты
│   └── VotingCore.sol          # Основной контракт
│
├── data/                       # Данные времени выполнения (gitignored)
│   ├── chain-data/             # Состояние блокчейна
│   └── logs/                   # Журналы сессий
│
├── scripts/                    # Скрипты сборки и очистки
│   ├── builder.py              # Скрипт сборки EXE
│   └── clean.*                 # Скрипты очистки (.bat, .ps1, .sh)
│
├── src/                        # Исходный код
│   ├── assets/                 # Статика (иконки приложения)
│   ├── core/                   # Бизнес-логика и сервисы
│   ├── ui/                     # Интерфейс PyQt6
│   │   ├── i18n/               # JSON-словари локализации
│   │   ├── tabs/               # Вкладки интерфейса
│   │   ├── themes/             # QSS-темы
│   │   ├── widgets/            # Кастомные виджеты
│   │   └── workers/            # Фоновые потоки (QThread)
│   └── utils/                  # Утилиты (логгер, пути, конфиг, крипто)
│
└── tests/                      # Тесты
    ├── conftest.py             # Фикстуры Pytest
    └── test_*.py               # Unit и интеграционные тесты
```

---

## Запуск

```bash
python main.py
```

---

## Запуск тестов

```bash
python -m pytest -v
```

---

## Рекомендации по IDE

- **VSCode:** расширения Python, Pylance, Solidity.
- **PyCharm:** пометить `src/` как Sources Root; pytest как тест-раннер.

Обе IDE должны использовать виртуальную среду проекта в качестве интерпретатора Python.