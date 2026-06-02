# Figma Mockups & Wireframes

This document describes the structure, contents, and annotation system
of the **MYCELIUM CORE** Figma design file.

---

## Figma Design File

View the complete UI mockups with annotations:

**[Open in Figma (view only)](https://www.figma.com/design/PWzJmLP7TrrbjcL6F85KoU/mycelium-core)**

The file contains 4 tab mockups, 5 dialog types, variative components,
and 53 annotation notes. See structure details below.

### File Structure

The Figma file contains all UI mockups for the light theme, organized
in a single horizontal line from left to right:

```text
[Legend] -- [Admin Tab] -- [Vote Tab] -- [Audit Tab] -- [Logs Tab] -- [Header+Footer] -- [Messages] -- [Variative]
```

Gap between blocks: 400px. Reading direction: left to right,
matching the application workflow and tab order.

### Block Contents

| Block | Contents | Notes Count |
|:---|:---|:---|
| Legend | Color coding reference, pin style, layout rules | -- |
| Admin Tab | Full mockup + 20 annotation notes | 20 |
| Vote Tab | Full mockup + 10 annotation notes | 10 |
| Audit Tab | Full mockup + 8 annotation notes | 8 |
| Logs Tab | Full mockup + 5 annotation notes | 5 |
| Header + Footer | Header bar and status bar mockups + 3 notes | 3 |
| Messages | 5 dialog types + 3 annotation notes | 3 |
| Variative | StatusBadge, Toast, ProgressBar, LogBox + 4 notes | 4 |

**Total: 53 annotation notes across all blocks.**

---

## Layer Naming Convention

Each block follows a consistent naming structure:

```text
{tab}-tab-full/
  {tab}-tab-alexagents    -- mockup frame
  {tab}-tab-notes         -- notes container
```

Example:

```text
admin-tab-full/
  admin-tab-alexagents
  admin-tab-notes
```

Supplementary blocks:

```text
header-footer-full/
  header-footer
  header-footer-notes
msg-full
var-full
legend
```

---

## Annotation System

### Note Format

Each note is a card with the following structure:

```text
[SYS-NOTE-XXX] Title
Version: 1.0.1  Status: Current  Date: 2026-05-20  Author: AlexAgents

Binding to interface:
  WidgetClass.widget_name

Description:
  1-2 sentences about behavior.

References:
  ADR-XXX  |  FR-XXX  |  src/path/to/file.py

Limitation: (if any)
Commentary: (if any)

MYCELIUM CORE | Updated: 2026-05-20
```

### Note Border Colors

Notes use colored borders to indicate their category:

| Color | Hex | Category | Border Style |
|:---|:---|:---|:---|
| Blue | `#0969da` | Input fields, data display, tables | Side facing the tab |
| Green | `#1a7f37` | Action buttons, operations, workers | Side facing the tab |
| Orange | `#bf6a02` | Stages, restrictions, warnings | Full border (all sides) |
| Purple | `#6e40c9` | Global notes, system-wide, sections | Full border (all sides) |

Blue and green notes have a border only on the side facing the
mockup, indicating direction. Orange and purple notes have a full
border on all four sides, indicating system-wide scope.

### Note Placement Around Mockup

- **First note:** centered above the tab mockup
- **Last note:** centered below the tab mockup
- **Odd-numbered notes** (01, 03, 05...): right side of the tab
- **Even-numbered notes** (02, 04, 06...): left side of the tab

```text
              [NOTE-001]
+---------+               +---------+
|NOTE-002 |  +---------+  |NOTE-003 |
|(even)   |  |         |  |(odd)    |
+---------+  |   TAB   |  +---------+
             |  MOCKUP  |
+---------+  |         |  +---------+
|NOTE-004 |  |         |  |NOTE-005 |
|(even)   |  +---------+  |(odd)    |
+---------+               +---------+
              [NOTE-LAST]
```

---

## Pin System

Pins are numbered markers placed on the mockup to indicate which
element a note refers to.

### Pin Style

- **Shape:** Circle, 16x16px
- **Fill:** `#F5C844`
- **Border:** 2px solid `#1f3a68`
- **Text:** `#1f3a68`, 10px bold, centered
- **Layer:** Floats above all frames (not nested inside element frames)
- **Position:** Freely movable, touching the referenced element

### Pin Placement Rules

- **Number one** (1): always in the center of the element
- **Odd-numbered pins** (03, 05, 07): right side of the element
- **Even-numbered pins** (02, 04, 06): left side of the element
- **Global notes** (e.g. ADM-020): pin placed inside the content
  frame that wraps all other content of the tab

The pin number matches the note number. Pin 03 on the mockup
corresponds to note [SYS-NOTE-ADM-003] in the notes column.

---

## Note Count by Section

| Section | Prefix | Count | Range |
|:---|:---|:---|:---|
| Admin Tab | ADM | 20 | ADM-001 to ADM-020 |
| Vote Tab | VOT | 10 | VOT-001 to VOT-010 |
| Audit Tab | AUD | 8 | AUD-001 to AUD-008 |
| Logs Tab | LOG | 5 | LOG-001 to LOG-005 |
| Variative | VAR | 4 | VAR-001 to VAR-004 |
| Messages | MSG | 3 | MSG-001 to MSG-003 |
| Header + Footer | HDR | 3 | HDR-001 to HDR-003 |
| **Total** | | **53** | |

---

## Mockup Specifications

### Window Dimensions

- **Minimum size:** 1100x700px
- **Mockup size:**px
- **Header height:** 44px (fixed)
- **Status bar height:** 28px (fixed)
- **Tab content:** remaining height, scrollable

### Theme

All mockups use the **light theme** exclusively. Color values
correspond to the light theme palette documented in
[Color Palette](./color-palette.md).

### Dialog Mockups

Five dialog types are documented in the Messages block:

1. **New Session** -- confirmation with auto-deploy checkbox
2. **Mass Vote** -- confirmation before batch voting
3. **Funding** -- confirmation with amount calculation
4. **Exit** -- exit confirmation
5. **Reset Blockchain** -- destructive action with log deletion option

---

## Variative Components

The Variative block documents reusable components with all their
states and variants:

- **StatusBadge:** 11 key variants across two groups
  (Audit/Security and Stage/Connection)
- **Toast:** 4 types (success, error, warning, info) with examples
- **ProgressBar:** 4 states (0%, 30%, 60%, 100%)
- **LogBox:** 3 content examples (deploy, candidates, voters)