# Typography

Font families, sizes, and weights used in **MYCELIUM CORE**.

---

## Font Families

| Context | Font | Fallback | Usage |
|---|---|---|---|
| UI text | `Segoe UI` | `Ubuntu`, `sans-serif` | All labels, buttons, headers, dialogs |
| Monospace | `Consolas` | `Courier New`, `monospace` | Contract addresses, TX hashes, log viewer, private key fields |

Both fonts are system-installed on Windows. On Linux/macOS the
fallback fonts are used automatically.

---

## Size Hierarchy

| Element | Size | Weight | QSS Selector |
|---|---|---|---|
| Header title | 14px | Bold | `#headerTitle` |
| Section header | 13px | Bold | `#sectionHeader` |
| Body text | 13px | Normal | `QWidget` (base) |
| Field labels | 11px | Bold | `#fieldLabel` |
| Status values | 13px | Bold | `#statusValue` |
| Monospace fields | 12px | Normal | `#monoLabel` |
| Log viewer | 11px | Normal | `#logsViewer` |
| Mini log box | 11px | Normal | `#logBox` |
| Status bar | 12px | Normal | `QStatusBar` |
| Tab labels | 13px | 500 | `QTabBar::tab` |
| Toast text | 13px | 600 | `#toastContainer QLabel` |
| Badge text | 11px | Bold | `StatusBadge` (inline) |
| Table header | 11px | Bold | `QHeaderView::section` |
| Tooltip | inherited | Normal | `QToolTip` |

---

## Weight Scale

| Weight | CSS Value | Usage |
|---|---|---|
| Normal | 400 | Body text, input fields |
| Medium | 500 | Tab labels, standard buttons |
| Semi-bold | 600 | Toast notifications |
| Bold | 700 | Headers, field labels, badges, action buttons |

---

## Letter Spacing

| Element | Spacing | Purpose |
|---|---|---|
| Header title | 2px | Branding emphasis |
| Field labels | 1px | Uppercase readability |
| Group box titles | 2px | Section separation |
| Badge text | 1px | Compact readability |

---

## Line Height

The default Qt line height is used for all widgets. The only explicit
override is in `MessageDialog` text labels:

```css
QLabel#messageDialogText {
    line-height: 140%;
}
```