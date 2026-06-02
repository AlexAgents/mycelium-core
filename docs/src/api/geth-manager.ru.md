# Модуль: GethManager

Управляет жизненным циклом локального процесса Geth.

- **Файл:** `src/core/geth_manager.py`
- **Класс:** `GethManager`

---

## Свойства

### `mode -> str`
`"dev"` или `"custom"`.

### `rpc_url -> str`
`http://{rpc_host}:{rpc_port}`.

---

## Жизненный цикл

### `start() -> None`

1. Проверяет наличие `geth.exe` в `bin/`.
2. Завершает зомби-процессы Geth (`taskkill`).
3. Очищает `chain-data/active/` (dev-режим несовместим с постоянными данными).
4. Проверяет доступность порта 8545.
5. Запускает подпроцесс Geth с `--dev --dev.period 5`.
6. Запускает поток мониторинга.

Генерирует `FileNotFoundError`, если бинарник Geth отсутствует.
Генерирует `RuntimeError`, если порт занят после очистки.

### `stop() -> None`
Устанавливает `_shutting_down = True` перед завершением во избежание ложных
crash-callback. Graceful terminate → kill → taskkill → закрытие лог-файла.

### `is_running() -> bool`
Возвращает `True`, если процесс активен.

---

## Данные цепи

### `purge_chain_data(archive: bool = True) -> None`
Архивирует или удаляет `chain-data/active/`. Завершает зомби-процессы,
пересоздаёт пустую директорию.

---

## Мониторинг крэшей

### `set_crash_callback(cb: Callable) -> None`
Callback вызывается только при неожиданном завершении (не при намеренном `stop()`).
Поток мониторинга проверяет флаг `_shutting_down` для разграничения крэша и штатной
остановки.