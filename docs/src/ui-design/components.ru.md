# Спецификация компонентов интерфейса

Документ описывает стили, размеры и состояния кастомных виджетов
интерфейса **MYCELIUM CORE**.

---

## 1. Функциональные кнопки (`QPushButton`)

Кнопки действий следуют строгим контурным или сплошным стилям
в зависимости от важности. Все кнопки используют `min-height: 30px`,
если не указано иное.

### Кнопка деплоя (`#deployButton`)

Главная кнопка действия для развёртывания контракта.

- **По умолчанию:** `bg #0969da`, `border #0969da`, `text #ffffff`, `font-weight bold`
- **Hover:** `bg #0860ca`
- **Disabled:** `bg #f4f7fb`, `border #c4d3e8`, `text #7286a5`
- **Ширина:** 100% родительской секции
- **Использование:** Deploy VotingCore, кнопки подтверждения в диалогах

### Кнопка регистрации (`#registerCandidatesButton`)

Вторичная кнопка для on-chain регистрации.

- **По умолчанию:** `bg #dbeafe`, `border #0969da`, `text #0550ae`, `font-weight bold`
- **Hover:** `bg #0969da`, `text #ffffff`
- **Disabled:** `bg #f4f7fb`, `border #c4d3e8`, `text #7286a5`
- **Использование:** Зарегистрировать в сети

### Кнопка Whitelist / Голосования (`#whitelistButton`)

Зелёная кнопка действия для операций с избирателями.

- **По умолчанию:** `bg #dcfce7`, `border #1a7f37`, `text #116329`, `font-weight bold`
- **Hover:** `bg #1a7f37`, `text #ffffff`
- **Disabled:** `bg #f4f7fb`, `border #c4d3e8`, `text #7286a5`
- **Использование:** Добавить избирателей в Whitelist, Запустить аудит

### Кнопка подачи голоса (`#castVoteButton`)

Самая заметная кнопка действия в приложении.

- **По умолчанию:** `bg #1a7f37`, `border #1a7f37`, `text #ffffff`
- **Hover:** `bg #176f30`
- **Disabled:** `bg #f4f7fb`, `border #c4d3e8`, `text #7286a5`
- **Шрифт:** `15px bold`, `letter-spacing 1px`
- **Размер:** `min-height 46px`, `border-radius 6px`, `width 100%`
- **Использование:** ПРОГОЛОСОВАТЬ на вкладке Голосование

### Кнопка начала голосования (`#startButton`)

- **По умолчанию:** `bg #dcfce7`, `border #1a7f37`, `text #116329`, `font-weight bold`
- **Hover:** `bg #1a7f37`, `text #ffffff`
- **Disabled:** `bg #f4f7fb`, `border #c4d3e8`, `text #7286a5`
- **Размер:** `min-height 36px`, `flex 1` (делит ширину с Finish пополам)

### Кнопка завершения голосования (`#finishButton`)

- **По умолчанию:** `bg #fef3e7`, `border #bf6a02`, `text #8a4b00`, `font-weight bold`
- **Hover:** `bg #bf6a02`, `text #ffffff`
- **Disabled:** `bg #f4f7fb`, `border #c4d3e8`, `text #7286a5`
- **Размер:** `min-height 36px`, `flex 1` (делит ширину с Start пополам)

### Кнопка-иконка (`#iconButton`)

Маленькие утилитарные кнопки с опциональным текстом.

- **По умолчанию:** `bg transparent`, `border 1px solid #c4d3e8`, `text #3d5a80`
- **Hover:** `bg #e7eef7`, `border #0969da`, `text #0969da`
- **Размер:** `min-width 32px`, `min-height 30px`, `padding 6px 10px`
- **Вариант только иконка:** `width 32px`, `padding 6px`
- **Использование:** Refresh, Copy, Save, Import, Export, Generate, Fund, глаз

---

## 2. Значки статусов (`StatusBadge`)

Скруглённые пилюли-индикаторы состояния. Автоматически подбирают
палитру под текущую тему через `_detect_light_theme()`.

### Стиль

```css
border-radius: 10px;
padding: 3px 10px;
font-size: 11px;
font-weight: bold;
letter-spacing: 1px;
border: none;
```

### Палитра светлой темы

| Ключ | Фон | Текст |
|:---|:---|:---|
| `SETUP` / `OFFLINE` / `SKIPPED` | `#c4d3e8` | `#1f3a68` |
| `ACTIVE` / `CONNECTED` / `DEV` / `PASSED` | `#dcfce7` | `#1a7f37` |
| `FINISHED` | `#ede9fe` | `#6e40c9` |
| `FAILED` | `#fee2e2` | `#cf222e` |
| `WARNING` / `CUSTOM` | `#fef3e7` | `#bf6a02` |

### Палитра тёмной темы

| Ключ | Фон | Текст |
|:---|:---|:---|
| `SETUP` / `OFFLINE` / `SKIPPED` | `#2a2f3a` | `#8b949e` |
| `ACTIVE` / `CONNECTED` / `DEV` / `PASSED` | `#1a3a1f` | `#3fb950` |
| `FINISHED` | `#2d1b69` | `#a78bfa` |
| `FAILED` | `#3d1a1a` | `#f85149` |
| `WARNING` / `CUSTOM` | `#3d2f00` | `#e3b341` |

### Переключение темы

При переключении темы `MainWindow._refresh_all_status_badges()`
перебирает все дочерние `StatusBadge` через `findChildren()` и вызывает
`refresh_theme()` на каждом. Метод пересчитывает цвета из словарей
палитры `_SCHEME_DARK` и `_SCHEME_LIGHT`.

**Код:** `src/ui/widgets/status_badge.py`

---

## 3. Всплывающие тосты (`Toast`)

Плавающие уведомления с глобальной очередью через `_ToastManager`.
Только один тост виден одновременно. Дублирующийся текст подавляется.

### Стиль

```css
border-radius: 12px;
border: none;
min-width: 240px;
max-width: 420px;
font-size: 13px;
font-weight: 600;
color: #ffffff;
```

### Типы и цвета

| Тип | Фон | Иконка |
|:---|:---|:---|
| `success` | `#2da44e` | `fa5s.check-circle` |
| `error` | `#cf222e` | `fa5s.times-circle` |
| `warning` | `#bf8700` | `fa5s.exclamation-triangle` |
| `info` | `#0969da` | `fa5s.info-circle` |

Текст и иконка всегда `#ffffff` независимо от темы.

### Анимация

- **Появление:** 220мс, `QEasingCurve.OutCubic`, прозрачность 0.0 -> 1.0
- **Показ:** 2500мс
- **Исчезновение:** 280мс, `QEasingCurve.InCubic`, прозрачность 1.0 -> 0.0
- **Пауза между тостами:** 150мс

### Позиционирование

Тост является дочерним виджетом `MainWindow.centralWidget()`, не
отдельным окном. Позиция: правый нижний угол, отступ 20px от краёв.
Размер иконки: 20x20px. Layout: `QHBoxLayout`, margins `16 12 18 12`,
spacing `12`.

### Независимость от темы

Цвета тостов заданы через inline `setStyleSheet()` в Python-коде.
Они **не** управляются QSS-файлами тем и остаются одинаковыми
в обеих темах.

**Код:** `src/ui/widgets/toast.py`

---

## 4. Индикатор прогресса (`QProgressBar`)

Горизонтальный градиентный индикатор прогресса в footer.

### Стиль

```css
background-color: #e7eef7;       /* контейнер, светлая тема */
border: 1px solid #c4d3e8;
border-radius: 4px;
height: 14px;
font-size: 10px;
text-align: center;
```

### Градиент заполнения (светлая тема)

```css
background: qlineargradient(
    x1:0, y1:0, x2:1, y2:0,
    stop:0 #0550ae,
    stop:0.5 #0969da,
    stop:1.0 #54aeff
);
border-radius: 3px;
```

### Градиент заполнения (тёмная тема)

```css
background: qlineargradient(
    x1:0, y1:0, x2:1, y2:0,
    stop:0 #1f6feb,
    stop:0.5 #388bfd,
    stop:1.0 #58a6ff
);
```

### Поведение

- **По умолчанию скрыт** (`visible: false`)
- Появляется при запуске любого worker через `connect_worker_progress()`
- Worker эмитит сигнал `percent(int)`, диапазон 0-100
- После завершения worker скрывается через 800мс (QTimer.singleShot)
- Ширина: `180px` (фиксированная в footer)
- `textVisible: true` (показывает процент)

### Типичные значения прогресса по операциям

| Операция | Значения |
|:---|:---|
| Деплой | 20% компиляция, 60% деплой, 100% готово |
| Финансирование | `idx/total * 100` на каждого избирателя |
| Регистрация кандидатов | `idx/total * 100` на каждого кандидата |
| Whitelist | 30% отправка, 100% готово |
| Аудит | 20% старт, 100% готово |
| Массовое голосование | `idx/total * 100` на каждого избирателя |
| Fund from dev | 30% отправка, 100% готово |
| Сброс блокчейна | 15% стоп, 35% ожидание, 60% удаление, 85% перезапуск, 100% готово |

**Код:** `src/ui/main_window.py` (`show_progress`, `update_progress`, `hide_progress`)

---

## 5. Мини-лог операций (`#logBox`)

Компактное текстовое поле только для чтения, отображающее ход операций
внутри секций вкладок.

### Стиль

```css
background-color: #f4f7fb;       /* светлая тема */
border: 1px solid #e7eef7;
border-radius: 4px;
color: #3d5a80;
font-family: "Consolas", "Courier New", monospace;
font-size: 11px;
padding: 8px;
```

### Размер

Высота вычисляется как `строки * 22px + 16px`:

| Экземпляр | Строк | Макс. высота | Расположение |
|:---|:---|:---|:---|
| Лог деплоя | 3 | 82px | Админ > секция Контракт |
| Лог кандидатов | 2 | 60px | Админ > секция Кандидаты |
| Лог избирателей | 3 | 82px | Админ > секция Избиратели |
| Лог массового голосования | 6 | 148px | Голосование > секция Mass Vote |

### Поведение

- Только чтение (`setReadOnly(True)`)
- Сообщения поступают через сигнал `worker.progress` и добавляются через `append()`
- Очищается при `reset_ui()` родительского таба
- Переполнение: `overflow-y: auto`
- ObjectName: `logBox`

### Отличие от просмотра логов

LogBox (`#logBox`) компактный и фиксированной высоты. Полный просмотр
лога сессии (`#logsViewer`) на вкладке Логи использует stretch-layout
и имеет другой фон (`#ffffff` в светлой теме против `#f4f7fb` для
LogBox).

**Код:** `src/ui/tabs/admin_tab.py`, `src/ui/tabs/vote_tab.py`