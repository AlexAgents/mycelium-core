# Color Palette

This document specifies the complete set of color tokens used in both
Light and Dark themes of **MYCELIUM CORE**.

---

## Light Theme (Deep Navy & Blues)

### Base Colors

| Semantic | Variable | Hex | Description |
|:---|:---|:---|:---|
| Window Background | `window-bg` | `#f4f7fb` | Main window, scroll areas |
| Card Background | `card-bg` | `#ffffff` | Group boxes, input backgrounds |
| Header Background | `header-bg` | `#e7eef7` | Header bar, tab bar, status bar |
| Input Background | `input-bg` | `#ffffff` | QLineEdit, QSpinBox default |
| Input Background Focus | `input-bg-focus` | `#ffffff` | QLineEdit focused |
| Hover Background | `hover-bg` | `#e7eef7` | Button hover, radio hover |
| Selected Background | `selected-bg` | `#d6e2f0` | Tab hover, button pressed |
| Alternate Row | `alt-row` | `#f4f7fb` | Table alternating row color |

### Text Colors

| Semantic | Variable | Hex | Description |
|:---|:---|:---|:---|
| Primary Text | `text-primary` | `#1f3a68` | Headers, labels, body text |
| Secondary Text | `text-secondary` | `#3d5a80` | Field labels, help text, descriptions |
| Muted Text | `text-muted` | `#7286a5` | Disabled text, info bar, path labels |
| Mono Text | `text-mono` | `#0969da` | Ethereum addresses, TX hashes, contract labels |
| Link Text | `text-link` | `#0969da` | Header title, accent elements |

### Border Colors

| Semantic | Variable | Hex | Description |
|:---|:---|:---|:---|
| Border Subtle | `border-subtle` | `#c4d3e8` | Card borders, input borders, separators |
| Border Muted | `border-muted` | `#e7eef7` | Log box borders, alternate borders |
| Border Focus | `border-focus` | `#0969da` | Input focus state |
| Border Drag | `border-drag` | `#0969da` | Drag-drop zone active (2px dashed) |

### Accent Colors

| Semantic | Variable | Hex | Description |
|:---|:---|:---|:---|
| Accent Blue | `accent-blue` | `#0969da` | Deploy buttons, primary selections, tab active |
| Accent Blue Hover | `accent-blue-hover` | `#0860ca` | Deploy button hover |
| Accent Blue Light | `accent-blue-light` | `#dbeafe` | Register button background |
| Accent Blue Dark | `accent-blue-dark` | `#0550ae` | Register button text, progress bar start |
| Accent Blue Bright | `accent-blue-bright` | `#54aeff` | Progress bar end gradient |
| Accent Green | `accent-green` | `#1a7f37` | Start button, whitelist button, cast vote |
| Accent Green Light | `accent-green-light` | `#dcfce7` | Start button bg, whitelist bg, PASSED badge bg |
| Accent Green Dark | `accent-green-dark` | `#116329` | Whitelist button text |
| Accent Green Hover | `accent-green-hover` | `#176f30` | Cast vote hover |
| Accent Yellow | `accent-yellow` | `#bf6a02` | Finish button border, WARNING badge text |
| Accent Yellow Light | `accent-yellow-light` | `#fef3e7` | Finish button bg, WARNING badge bg |
| Accent Yellow Dark | `accent-yellow-dark` | `#8a4b00` | Finish button text |
| Accent Red | `accent-red` | `#cf222e` | Error icons, FAILED badge text, exit button |
| Accent Red Light | `accent-red-light` | `#fee2e2` | FAILED badge bg, error dialog icon bg |
| Accent Purple | `accent-purple` | `#6e40c9` | FINISHED badge text |
| Accent Purple Light | `accent-purple-light` | `#ede9fe` | FINISHED badge bg |

### Toast Colors

| Semantic | Hex | Description |
|:---|:---|:---|
| Toast Success | `#2da44e` | Success notification background |
| Toast Error | `#cf222e` | Error notification background |
| Toast Warning | `#bf8700` | Warning notification background |
| Toast Info | `#0969da` | Info notification background |
| Toast Text | `#ffffff` | All toast text and icons |

Toast colors are hardcoded in Python (`toast.py`), not applied
through QSS themes. They remain the same in both dark and light modes.

### StatusBadge Colors

| Key | Background | Text | Usage |
|:---|:---|:---|:---|
| SETUP | `#c4d3e8` | `#1f3a68` | Stage badge before voting |
| ACTIVE | `#dcfce7` | `#1a7f37` | Stage badge during voting |
| FINISHED | `#ede9fe` | `#6e40c9` | Stage badge after voting |
| CONNECTED | `#dcfce7` | `#1a7f37` | RPC status connected |
| OFFLINE | `#c4d3e8` | `#1f3a68` | RPC status disconnected |
| DEV | `#dcfce7` | `#1a7f37` | Geth mode dev |
| CUSTOM | `#fef3e7` | `#bf6a02` | Geth mode custom |
| PASSED | `#dcfce7` | `#1a7f37` | Audit check passed |
| FAILED | `#fee2e2` | `#cf222e` | Audit check failed |
| WARNING | `#fef3e7` | `#bf6a02` | Audit check warning |
| SKIPPED | `#c4d3e8` | `#1f3a68` | Audit check skipped |

StatusBadge style: `border-radius: 10px`, `padding: 3px 10px`,
`font-size: 11px`, `font-weight: bold`, `letter-spacing: 1px`.

### ProgressBar Gradient

```text
Light theme gradient (left to right):
  stop 0.0  #0550ae
  stop 0.5  #0969da
  stop 1.0  #54aeff
```

Background: `#e7eef7`. Border: `1px solid #c4d3e8`. Height: `14px`.
Border-radius: `4px` (container), `3px` (chunk).

### Button State Colors

| Button Type | Default BG | Default Border | Default Text | Hover BG | Hover Text | Disabled BG | Disabled Text |
|:---|:---|:---|:---|:---|:---|:---|:---|
| Standard | `#ffffff` | `#c4d3e8` | `#1f3a68` | `#e7eef7` | `#0969da` | `#f4f7fb` | `#7286a5` |
| Deploy | `#0969da` | `#0969da` | `#ffffff` | `#0860ca` | `#ffffff` | `#f4f7fb` | `#7286a5` |
| Register | `#dbeafe` | `#0969da` | `#0550ae` | `#0969da` | `#ffffff` | `#f4f7fb` | `#7286a5` |
| Whitelist | `#dcfce7` | `#1a7f37` | `#116329` | `#1a7f37` | `#ffffff` | `#f4f7fb` | `#7286a5` |
| Start | `#dcfce7` | `#1a7f37` | `#116329` | `#1a7f37` | `#ffffff` | `#f4f7fb` | `#7286a5` |
| Finish | `#fef3e7` | `#bf6a02` | `#8a4b00` | `#bf6a02` | `#ffffff` | `#f4f7fb` | `#7286a5` |
| Cast Vote | `#1a7f37` | `#1a7f37` | `#ffffff` | `#176f30` | `#ffffff` | `#f4f7fb` | `#7286a5` |
| Icon Button | transparent | `#c4d3e8` | `#3d5a80` | `#e7eef7` | `#0969da` | -- | -- |
| Danger | -- | `#cf222e` | `#cf222e` | `#fee2e2` | `#cf222e` | -- | -- |

---

## Dark Theme (Slate & Midnight)

### Base Colors

| Semantic | Variable | Hex | Description |
|:---|:---|:---|:---|
| Window Background | `window-bg` | `#0d1117` | Main window, scroll areas |
| Card Background | `card-bg` | `#161b22` | Group boxes, input backgrounds |
| Header Background | `header-bg` | `#161b22` | Header bar, tab bar, status bar |
| Input Background | `input-bg` | `#161b22` | QLineEdit, QSpinBox default |
| Input Background Focus | `input-bg-focus` | `#1c2128` | QLineEdit focused |
| Hover Background | `hover-bg` | `#21262d` | Button hover, radio hover |
| Selected Background | `selected-bg` | `#1c2128` | Tab hover, button pressed |
| Alternate Row | `alt-row` | `#1c2128` | Table alternating row color |

### Text Colors

| Semantic | Variable | Hex | Description |
|:---|:---|:---|:---|
| Primary Text | `text-primary` | `#c9d1d9` | Headers, labels, body text |
| Secondary Text | `text-secondary` | `#8b949e` | Field labels, help text, descriptions |
| Muted Text | `text-muted` | `#484f58` | Disabled text, info bar |
| Mono Text | `text-mono` | `#58a6ff` | Ethereum addresses, TX hashes, contract labels |
| Link Text | `text-link` | `#388bfd` | Header title, accent elements |

### Border Colors

| Semantic | Variable | Hex | Description |
|:---|:---|:---|:---|
| Border Subtle | `border-subtle` | `#30363d` | Card borders, input borders, separators |
| Border Muted | `border-muted` | `#21262d` | Log box borders, alternate borders |
| Border Focus | `border-focus` | `#388bfd` | Input focus state |
| Border Drag | `border-drag` | `#388bfd` | Drag-drop zone active (2px dashed) |

### Accent Colors

| Semantic | Variable | Hex | Description |
|:---|:---|:---|:---|
| Accent Blue | `accent-blue` | `#388bfd` | Deploy buttons, primary selections, tab active |
| Accent Blue Hover | `accent-blue-hover` | `#1f6feb` | Deploy button hover |
| Accent Blue BG | `accent-blue-bg` | `#1a3a6e` | Register button background |
| Accent Blue Selection | `accent-blue-sel` | `#1f6feb` | Selection background, combo selected |
| Accent Green | `accent-green` | `#3fb950` | ACTIVE badge, PASSED badge text |
| Accent Green BG | `accent-green-bg` | `#1a3a1f` | ACTIVE badge bg, PASSED badge bg |
| Accent Green Hover | `accent-green-hover` | `#196c2e` | Whitelist hover, start hover |
| Accent Green Toast | `accent-green-toast` | `#2da44e` | Toast success |
| Accent Yellow | `accent-yellow` | `#e3b341` | WARNING badge text, fund icons |
| Accent Yellow BG | `accent-yellow-bg` | `#3d2f00` | WARNING badge bg, finish button bg |
| Accent Red | `accent-red` | `#f85149` | FAILED badge text, error icons |
| Accent Red BG | `accent-red-bg` | `#3d1a1a` | FAILED badge bg |
| Accent Purple | `accent-purple` | `#a78bfa` | FINISHED badge text |
| Accent Purple BG | `accent-purple-bg` | `#2d1b69` | FINISHED badge bg |

### StatusBadge Colors

| Key | Background | Text |
|:---|:---|:---|
| SETUP / OFFLINE / SKIPPED | `#2a2f3a` | `#8b949e` |
| ACTIVE / CONNECTED / DEV / PASSED | `#1a3a1f` | `#3fb950` |
| FINISHED | `#2d1b69` | `#a78bfa` |
| FAILED | `#3d1a1a` | `#f85149` |
| WARNING / CUSTOM | `#3d2f00` | `#e3b341` |

### ProgressBar Gradient

```text
Dark theme gradient (left to right):
  stop 0.0  #1f6feb
  stop 0.5  #388bfd
  stop 1.0  #58a6ff
```

Background: `#21262d`. Border: `1px solid #30363d`.

---

## Design Principles

1. **No pure black in light theme.** `#000000` is never used.
   All dark text uses `#1f3a68` (deep navy) or `#3d5a80` (secondary).

2. **Two greens are intentional.** `#1a7f37` / `#3fb950` for badges
   and buttons, `#2da44e` for toast notifications. Different brightness
   levels for contrast on different backgrounds.

3. **Toast colors are theme-independent.** They are set via inline
   `setStyleSheet()` in Python code, not through QSS files.

4. **StatusBadge updates on theme switch.** `MainWindow` calls
   `refresh_theme()` on all `StatusBadge` children after applying
   a new QSS theme.