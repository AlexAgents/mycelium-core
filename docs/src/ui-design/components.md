# Widget Components Specification

This document specifies the style sheets, sizes, and states of custom
UI widgets used in **MYCELIUM CORE**.

---

## 1. Action Buttons (`QPushButton`)

Action buttons follow a strict outlined or solid style depending on
importance. All buttons use `min-height: 30px` unless specified otherwise.

### Deploy Button (`#deployButton`)

Primary action button for contract deployment.

- **Default:** `bg #0969da`, `border #0969da`, `text #ffffff`, `font-weight bold`
- **Hover:** `bg #0860ca`
- **Disabled:** `bg #f4f7fb`, `border #c4d3e8`, `text #7286a5`
- **Width:** 100% of parent section
- **Usage:** Deploy VotingCore, dialog confirm buttons

### Register Button (`#registerCandidatesButton`)

Secondary action button for on-chain registration.

- **Default:** `bg #dbeafe`, `border #0969da`, `text #0550ae`, `font-weight bold`
- **Hover:** `bg #0969da`, `text #ffffff`
- **Disabled:** `bg #f4f7fb`, `border #c4d3e8`, `text #7286a5`
- **Usage:** Register On-Chain

### Whitelist / Cast Vote Button (`#whitelistButton`)

Green action button for voter operations and voting.

- **Default:** `bg #dcfce7`, `border #1a7f37`, `text #116329`, `font-weight bold`
- **Hover:** `bg #1a7f37`, `text #ffffff`
- **Disabled:** `bg #f4f7fb`, `border #c4d3e8`, `text #7286a5`
- **Usage:** Add Voters To Whitelist, Run Audit

### Cast Vote Button (`#castVoteButton`)

The most prominent action button in the application.

- **Default:** `bg #1a7f37`, `border #1a7f37`, `text #ffffff`
- **Hover:** `bg #176f30`
- **Disabled:** `bg #f4f7fb`, `border #c4d3e8`, `text #7286a5`
- **Font:** `15px bold`, `letter-spacing 1px`
- **Size:** `min-height 46px`, `border-radius 6px`, `width 100%`
- **Usage:** CAST VOTE on Vote tab

### Start Voting Button (`#startButton`)

- **Default:** `bg #dcfce7`, `border #1a7f37`, `text #116329`, `font-weight bold`
- **Hover:** `bg #1a7f37`, `text #ffffff`
- **Disabled:** `bg #f4f7fb`, `border #c4d3e8`, `text #7286a5`
- **Size:** `min-height 36px`, `flex 1` (shares width with Finish)

### Finish Voting Button (`#finishButton`)

- **Default:** `bg #fef3e7`, `border #bf6a02`, `text #8a4b00`, `font-weight bold`
- **Hover:** `bg #bf6a02`, `text #ffffff`
- **Disabled:** `bg #f4f7fb`, `border #c4d3e8`, `text #7286a5`
- **Size:** `min-height 36px`, `flex 1` (shares width with Start)

### Icon Button (`#iconButton`)

Small utility buttons with optional text.

- **Default:** `bg transparent`, `border 1px solid #c4d3e8`, `text #3d5a80`
- **Hover:** `bg #e7eef7`, `border #0969da`, `text #0969da`
- **Size:** `min-width 32px`, `min-height 30px`, `padding 6px 10px`
- **Icon-only variant:** `width 32px`, `padding 6px`
- **Usage:** Refresh, Copy, Save, Import, Export, Generate, Fund, eye toggle

---

## 2. Status Badges (`StatusBadge`)

Pill-shaped, non-interactive indicators of state. Automatically select
palette based on current theme via `_detect_light_theme()`.

### Style

```css
border-radius: 10px;
padding: 3px 10px;
font-size: 11px;
font-weight: bold;
letter-spacing: 1px;
border: none;
```

### Light Theme Palette

| Key | Background | Text |
|:---|:---|:---|
| `SETUP` / `OFFLINE` / `SKIPPED` | `#c4d3e8` | `#1f3a68` |
| `ACTIVE` / `CONNECTED` / `DEV` / `PASSED` | `#dcfce7` | `#1a7f37` |
| `FINISHED` | `#ede9fe` | `#6e40c9` |
| `FAILED` | `#fee2e2` | `#cf222e` |
| `WARNING` / `CUSTOM` | `#fef3e7` | `#bf6a02` |

### Dark Theme Palette

| Key | Background | Text |
|:---|:---|:---|
| `SETUP` / `OFFLINE` / `SKIPPED` | `#2a2f3a` | `#8b949e` |
| `ACTIVE` / `CONNECTED` / `DEV` / `PASSED` | `#1a3a1f` | `#3fb950` |
| `FINISHED` | `#2d1b69` | `#a78bfa` |
| `FAILED` | `#3d1a1a` | `#f85149` |
| `WARNING` / `CUSTOM` | `#3d2f00` | `#e3b341` |

### Theme Switching

When the user toggles the theme, `MainWindow._refresh_all_status_badges()`
iterates over all `StatusBadge` children using `findChildren()` and calls
`refresh_theme()` on each. This recalculates colors from the palette
dictionaries `_SCHEME_DARK` and `_SCHEME_LIGHT`.

**Code:** `src/ui/widgets/status_badge.py`

---

## 3. Toast Notifications (`Toast`)

Floating notifications managed by a global `_ToastManager` queue.
Only one toast is visible at a time. Duplicate text is suppressed.

### Style

```css
border-radius: 12px;
border: none;
min-width: 240px;
max-width: 420px;
font-size: 13px;
font-weight: 600;
color: #ffffff;
```

### Types and Colors

| Type | Background | Icon |
|:---|:---|:---|
| `success` | `#2da44e` | `fa5s.check-circle` |
| `error` | `#cf222e` | `fa5s.times-circle` |
| `warning` | `#bf8700` | `fa5s.exclamation-triangle` |
| `info` | `#0969da` | `fa5s.info-circle` |

Text and icon color is always `#ffffff` regardless of theme.

### Animation

- **Fade in:** 220ms, `QEasingCurve.OutCubic`, opacity 0.0 to 1.0
- **Display:** 2500ms
- **Fade out:** 280ms, `QEasingCurve.InCubic`, opacity 1.0 to 0.0
- **Gap between toasts:** 150ms

### Positioning

Toast is a child of `MainWindow.centralWidget()`, not a separate window.
Position: bottom-right corner, 20px margin from edges. Icon size: 20x20px.
Layout: `QHBoxLayout`, margins `16 12 18 12`, spacing `12`.

### Theme Independence

Toast colors are set via inline `setStyleSheet()` in Python code.
They are **not** controlled by QSS theme files and remain identical
in both dark and light modes.

**Code:** `src/ui/widgets/toast.py`

---

## 4. Progress Bar (`QProgressBar`)

Horizontal gradient progress indicator in the footer status bar.

### Style

```css
background-color: #e7eef7;       /* light theme container */
border: 1px solid #c4d3e8;
border-radius: 4px;
height: 14px;
font-size: 10px;
text-align: center;
```

### Gradient Fill (Light)

```css
background: qlineargradient(
    x1:0, y1:0, x2:1, y2:0,
    stop:0 #0550ae,
    stop:0.5 #0969da,
    stop:1.0 #54aeff
);
border-radius: 3px;
```

### Gradient Fill (Dark)

```css
background: qlineargradient(
    x1:0, y1:0, x2:1, y2:0,
    stop:0 #1f6feb,
    stop:0.5 #388bfd,
    stop:1.0 #58a6ff
);
```

### Behavior

- **Hidden by default** (`visible: false`)
- Appears when any worker starts via `connect_worker_progress()`
- Worker emits `percent(int)` signal, range 0 to 100
- After worker completion, hides after 800ms delay via `QTimer.singleShot`
- Width: `180px` (fixed in footer)
- `textVisible: true` (shows percentage)

### Typical Progress Values by Operation

| Operation | Values |
|:---|:---|
| Deploy | 20% compile, 60% deploy, 100% done |
| Fund voters | `idx/total * 100` per voter |
| Register candidates | `idx/total * 100` per candidate |
| Whitelist | 30% sending, 100% done |
| Audit | 20% start, 100% done |
| Mass vote | `idx/total * 100` per voter |
| Fund from dev | 30% sending, 100% done |
| Reset blockchain | 15% stop, 35% wait, 60% delete, 85% restart, 100% done |

**Code:** `src/ui/main_window.py` (`show_progress`, `update_progress`, `hide_progress`)

---

## 5. Log Box (Mini Log) (`#logBox`)

Compact read-only text area for displaying operation progress inside
tab sections.

### Style

```css
background-color: #f4f7fb;       /* light theme */
border: 1px solid #e7eef7;
border-radius: 4px;
color: #3d5a80;
font-family: "Consolas", "Courier New", monospace;
font-size: 11px;
padding: 8px;
```

### Size

Height is calculated as `lines * 22px + 16px`:

| Instance | Lines | Max Height | Location |
|:---|:---|:---|:---|
| Deploy log | 3 | 82px | Admin > Contract section |
| Candidates log | 2 | 60px | Admin > Candidates section |
| Voters log | 3 | 82px | Admin > Voters section |
| Mass vote log | 6 | 148px | Vote > Mass Vote section |

### Behavior

- Read-only (`setReadOnly(True)`)
- Messages arrive via `worker.progress` signal and are appended
- Cleared on `reset_ui()` of the parent tab
- Overflow: `overflow-y: auto`
- ObjectName: `logBox`

### Difference from Logs Viewer

LogBox (`#logBox`) is compact and fixed-height. The full session log
viewer (`#logsViewer`) on the Logs tab uses `stretch` layout and has
a different background color (`#ffffff` in light theme vs `#f4f7fb`
for LogBox).

**Code:** `src/ui/tabs/admin_tab.py`, `src/ui/tabs/vote_tab.py`