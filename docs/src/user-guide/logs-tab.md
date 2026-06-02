# Logs Tab

The Logs tab displays the active session log file in real time. Useful
for all roles for debugging and verifying behavior.

---

## What is shown

Contents of `data/logs/active/session.log` — the live log file the
application writes to.

The log is recreated on each application startup. Previous session
logs are auto-archived to `data/logs/archive/<session_id>/session.log`.

---

## Toolbar (left to right)

| Button | Purpose |
|---|---|
| **Refresh** | Reloads the log from disk. Necessary after long operations to see latest entries. |
| **Copy All** | Copies entire log to clipboard. |
| **Save As** | Saves current view to a `.log` or `.txt` file. |
| **Clear Display** | Clears the viewer (file is **not** deleted). |

Toolbar (right):

| Element | Purpose |
|---|---|
| **Search input** | Live filter — shows only lines containing the substring (case-insensitive). |
| **Autoscroll checkbox** | When enabled, the viewer scrolls to the bottom on each refresh. |

---

## Viewer

Read-only QTextEdit with monospaced font. Word-wrap disabled (one log
entry per line for readability).

---

## Bottom info bar

| Field | Description |
|---|---|
| **Lines** | Number of lines currently shown (after search filter). |
| **Size** | Disk size of the log file (formatted: B / KB / MB). |
| **Path** | Full path to `session.log`. Selectable for copy. |

---

## What gets logged

The application logs (via Python `logging`):

- Geth process lifecycle (start, stop, crash).
- Compilation result and contract address after deploy.
- Each admin action (add candidate, whitelist batch, stage change).
- Each `cast_vote` with TX hash.
- Mass vote summary.
- Audit run summary.
- Errors and unexpected exceptions (with stack traces).
- Session lifecycle (create, archive).

---

## What does NOT get logged

A `_SecretFilter` automatically redacts:

- Lines containing `private_key`, `priv_key`, `mnemonic`, `seed phrase`, `secret`.
- Anything matching the regex `0x[a-fA-F0-9]{64}` (private key pattern).

Such entries are replaced with `[REDACTED — secret suppressed]`.

---

## Archive

When you click **New Session** in the header, the current log is
archived:

```text
data/logs/archive/<session_id>/session.log
```

The active log file is then cleared and continues with the new session.