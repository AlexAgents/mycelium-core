# MYCELIUM CORE - Исходники документации

В этой директории хранятся исходные файлы документации проекта,
включая Markdown-файлы MkDocs, диаграммы PlantUML и модели процессов
BPMN.

## Артефакты документации

| Артефакт | Расположение | Описание |
|:---|:---|:---|
| Сайт MkDocs | `docs/src/` | 70+ страниц, EN/RU двуязычный |
| Диаграммы PlantUML | `docs/src/diagrams/sources/uml/` | 17 UML-диаграмм |
| Процессы BPMN | `docs/src/diagrams/sources/bpmn/` | 6 моделей BPMN 2.0 |
| Рендеры SVG | `docs/src/assets/diagrams/` | Автогенерация из исходников |
| Скриншоты | `docs/src/assets/images/screenshots/` | 10 скриншотов приложения |
| Макеты Figma | [Открыть в Figma](https://www.figma.com/design/PWzJmLP7TrrbjcL6F85KoU/mycelium-core) | 4 таба, 53 ноты, светлая тема |

## Разделы документации

| Раздел | Страниц | Описание |
|:---|:---|:---|
| Быстрый старт | 3 | Установка, первый запуск, обзор |
| Руководство пользователя | 5 | Вкладки Admin, Vote, Audit, Logs |
| Архитектура | 11 | Обзор, слои, компоненты, потоки данных, 7 ADR |
| Диаграммы | 23 | Каталог UML + BPMN с пояснениями |
| API Reference | 10 | Все модули ядра |
| UI Design | 6 | Дизайн-система, цвета, типографика, компоненты, иконки, Figma |
| Безопасность | 4 | Модель угроз, SEC-проверки, процедура аудита, ограничения |
| Деплой | 4 | Исходники, PyInstaller, дистрибуция, устранение неполадок |
| Разработка | 5 | Настройка, тестирование, стиль, контрибьюторы, git-процесс |
| Справочник | 5 | SRS, SRS документации, changelog, глоссарий, FAQ, лицензия |

## Предусловия

Для сборки документации и рендера диаграмм потребуется:

1. **Python 3.11+**
2. **Java Runtime Environment (JRE)** -- необходима для генерации
   диаграмм PlantUML.

## Настройка

Установите необходимые Python-зависимости:

```bash
pip install -r requirements-docs.txt
```

Для локального рендера UML-диаграмм скачайте
[`plantuml.jar`](https://github.com/plantuml/plantuml/releases/)
и поместите его в папку `docs/`. Файл должен называться
именно `plantuml.jar`.

> **Примечание:** `plantuml.jar` не включён в репозиторий.
> Скачайте его вручную со страницы официальных релизов PlantUML
> и поместите по пути `docs/plantuml.jar` перед запуском
> скрипта сборки.

## Локальный запуск

Проект включает кастомный скрипт сборки, который автоматически
компилирует все файлы `.puml` в SVG/PNG и запускает сервер MkDocs
с функцией live-reload.

Запустите из корня этой папки `docs/`:

```bash
python scripts/build_docs.py
```

Затем откройте `http://127.0.0.1:8000` в браузере.

## Строгая сборка (CI/CD check)

Чтобы убедиться в отсутствии битых ссылок:

```bash
mkdocs build --strict
```

## Ключевые ссылки

| Ресурс | Ссылка |
|:---|:---|
| Макеты Figma | [Только просмотр](https://www.figma.com/design/PWzJmLP7TrrbjcL6F85KoU/mycelium-core) |
| MkDocs Material | [Документация](https://squidfunk.github.io/mkdocs-material/) |
| PlantUML | [Релизы](https://github.com/plantuml/plantuml/releases/) |
| Camunda Modeler | [Скачать](https://camunda.com/download/modeler/) |