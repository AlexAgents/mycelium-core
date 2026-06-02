# UI Design System

MYCELIUM CORE follows a clean, structured, and modern design language
adapted for multi-theme PyQt6 desktop clients.

---

## Design Principles

1. **Structure over Clutter:** Use distinct cards (`QGroupBox`) and
   vertical spacing instead of dense borders or separation lines.

2. **Theme Consistency:** Every component, status badge, and custom
   dialog must dynamically adapt to dark and light modes.

3. **No Raw Black in Light Theme:** Pure black (`#000000`) is
   completely banned in the Light Theme. It is replaced by a palette
   of deep navy (`#1f3a68`) and navigation blues (`#3d5a80`).

4. **Action-oriented Colors:** Colors represent semantic states:
   - **Green** for success, active stages, and vote actions.
   - **Blue** for secondary processes, deployment, and data display.
   - **Orange/Yellow** for warnings, setup stage, and finish actions.
   - **Red** for critical actions, errors, and failed checks.
   - **Purple** for finished state and global system notes.

5. **Two Greens Are Intentional:** `#1a7f37` / `#3fb950` for badges
   and buttons, `#2da44e` for toast notifications. Different brightness
   levels provide proper contrast on different background colors.

6. **Theme-Independent Toasts:** Toast notification colors are set via
   inline `setStyleSheet()` in Python code, not through QSS files.
   They remain identical in both themes.

---

## Component Hierarchy (Atomic Design)

The UI follows a simplified Atomic Design approach:

| Level | Examples | Location |
|:---|:---|:---|
| **Atoms** | `StatusBadge`, `Toast`, field labels, pins | `src/ui/widgets/` |
| **Molecules** | `_StatusBlock` (caption + value), key row (input + eye button) | Inline in tab files |
| **Organisms** | `QGroupBox` sections (Contract, Candidates, Voters, Stage) | Tab `_build_*_section()` methods |
| **Templates** | Tab layouts (`AdminTab`, `VoteTab`, `AuditTab`, `LogsTab`) | `src/ui/tabs/` |
| **Pages** | `MainWindow` with header, tabs, and status bar | `src/ui/main_window.py` |

---

## Typography

### Font Families

| Context | Font | Fallback | Usage |
|:---|:---|:---|:---|
| UI text | `Segoe UI` | `Ubuntu`, `sans-serif` | All labels, buttons, headers, dialogs |
| Monospace | `Consolas` | `Courier New`, `monospace` | Addresses, TX hashes, log viewer, key fields |

### Size Hierarchy

| Element | Size | Weight | ObjectName |
|:---|:---|:---|:---|
| Header title | 14px | Bold | `headerTitle` |
| Section header | 13px | Bold | `sectionHeader` |
| Body text | 13px | Normal | `QWidget` (base) |
| Field labels | 11px | Bold | `fieldLabel` |
| Status values | 13px | Bold | `statusValue` |
| Monospace fields | 12px | Normal | `monoLabel` |
| Log viewer | 11px | Normal | `logsViewer` |
| Mini log box | 11px | Normal | `logBox` |
| Status bar | 12px | Normal | `QStatusBar` |
| Tab labels | 13px | 500 | `QTabBar::tab` |
| Toast text | 13px | 600 | `toastContainer QLabel` |
| Badge text | 11px | Bold | `StatusBadge` (inline) |
| Table header | 11px | Bold | `QHeaderView::section` |

### Letter Spacing

| Element | Spacing | Purpose |
|:---|:---|:---|
| Header title | 2px | Branding emphasis |
| Field labels | 1px | Uppercase readability |
| Group box titles | 2px | Section separation |
| Badge text | 1px | Compact readability |

---

## QSS ObjectName Registry

All custom-styled widgets use `setObjectName()` for QSS targeting:

### Layout and Structure

| ObjectName | Widget Type | Usage |
|:---|:---|:---|
| `headerBar` | QWidget | Header container |
| `headerTitle` | QLabel | Application title |
| `headerSep` | QFrame | Vertical separator in header |
| `mainTabs` | QTabWidget | Tab container |
| `mainProgressBar` | QProgressBar | Footer progress indicator |

### Labels and Text

| ObjectName | Widget Type | Usage |
|:---|:---|:---|
| `fieldLabel` | QLabel | Uppercase field captions |
| `monoLabel` | QLabel | Monospace text (addresses, hashes) |
| `statusValue` | QLabel | Bold status values |
| `sectionHeader` | QLabel | Section titles within cards |
| `messageDialogText` | QLabel | Dialog message text |
| `contractLabel` | QLabel | Contract address in status bar |

### Text Areas

| ObjectName | Widget Type | Usage |
|:---|:---|:---|
| `logBox` | QTextEdit | Mini operation logs in tabs |
| `logsViewer` | QTextEdit | Full session log viewer |
| `logsTitle` | QLabel | Logs tab title |
| `logsPathLabel` | QLabel | Log file path display |
| `logsCountLabel` | QLabel | Line count and size info |

### Interactive Elements

| ObjectName | Widget Type | Usage |
|:---|:---|:---|
| `candidateScroll` | QScrollArea | Candidate selection viewport |
| `iconButton` | QPushButton | Small icon-only or icon+text buttons |
| `deployButton` | QPushButton | Deploy and primary action style |
| `registerCandidatesButton` | QPushButton | Register and secondary action style |
| `whitelistButton` | QPushButton | Whitelist and cast vote style |
| `startButton` | QPushButton | Start voting button |
| `finishButton` | QPushButton | Finish voting button |
| `castVoteButton` | QPushButton | Main vote submission button |

### Notifications and Dialogs

| ObjectName | Widget Type | Usage |
|:---|:---|:---|
| `toastContainer` | QWidget | Toast notification container |
| `aboutTitle` | QLabel | About dialog title |
| `aboutVersion` | QLabel | About dialog version |
| `aboutBody` | QLabel | About dialog body text |

---

## Sizing Rules

### Minimum Sizes for Interactive Elements

| Element | Min Height | Min Width | Notes |
|:---|:---|:---|:---|
| Standard button | 30px | -- | Default for all QPushButton |
| Stage buttons (Start/Finish) | 36px | -- | Larger for emphasis |
| Cast Vote button | 46px | -- | Most prominent action |
| Icon-only button | 30px | 32px | Eye toggle, refresh, copy |
| Progress bar | 14px | 180px | Fixed in footer |
| Status badge | -- | -- | Size determined by content |
| QR receipt frame | 140px | 140px | Fixed size |
| Pin marker | 22px | 22px | Circle on mockup |

### Window Constraints

| Element | Value |
|:---|:---|
| Minimum window size | 1100x700px |
| Header height | 44px fixed |
| Status bar height | 28px fixed |
| Tab content | Remaining height, scrollable |
| Log box (3 lines) | 82px max height |
| Log box (6 lines) | 148px max height |
| Candidates scroll | 120px min, 220px max |

---

## Drag-and-Drop Zone

The Voters section in Admin Tab implements a drag-and-drop zone
for JSON file import.

### Visual States

| State | Border Style |
|:---|:---|
| Normal | `1px solid #c4d3e8` (light) / `1px solid #30363d` (dark) |
| Drag Over | `2px dashed #0969da` (light) / `2px dashed #388bfd` (dark) |

The zone is implemented as a custom `QGroupBox` subclass
(`_VoterDropZone`) with `setAcceptDrops(True)`. The `dragOver`
property is toggled via `setProperty("dragOver", True/False)`
and styled through QSS: `QGroupBox[dragOver="true"]`.

Only files with `.json` extension are accepted.

**Code:** `src/ui/tabs/admin_tab.py`

---

## Figma Design File

The complete set of UI mockups with 53 annotation notes is
maintained in the Figma design file. See
[Figma Mockups](./figma-mockups.md) for structure, annotation
system, and pin placement rules.