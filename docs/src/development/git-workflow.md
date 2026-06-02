# Git Workflow

Branch management and release process for **MYCELIUM CORE**.

---

## Branch Model

The project uses a simplified **GitHub Flow**:

```text
main ─────────────────────────────────────────►
  │                                    ▲
  ├── feature/csv-export ──────────────┤ (PR + squash merge)
  │                                    │
  ├── fix/nonce-sync ──────────────────┤
  │                                    │
  └── docs/api-reference ──────────────┘
```

### Branches

| Branch | Purpose | Lifetime |
|---|---|---|
| `main` | Stable, release-ready code | Permanent |
| `feature/*` | New functionality | Until merged |
| `fix/*` | Bug fixes | Until merged |
| `docs/*` | Documentation updates | Until merged |
| `refactor/*` | Code restructuring | Until merged |

---

## Workflow Steps

### 1. Create a branch

```bash
git checkout main
git pull origin main
git checkout -b feature/my-feature
```

### 2. Develop and commit

```bash
git add .
git commit -m "feat(scope): description"
```

Follow [Conventional Commits](https://www.conventionalcommits.org/)
format (see [Contributing Guide](./contributing.md)).

### 3. Push and open PR

```bash
git push origin feature/my-feature
```

Open a Pull Request on GitHub against `main`.

### 4. Review and merge

- All tests must pass.
- At least one approval required.
- Use **Squash and merge** for a clean commit history.

### 5. Clean up

After merge, delete the feature branch:

```bash
git checkout main
git pull origin main
git branch -d feature/my-feature
```

---

## Releases

### Versioning

The project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** — breaking changes (contract ABI change, incompatible API).
- **MINOR** — new features, backward compatible.
- **PATCH** — bug fixes, documentation updates.

### Creating a Release

1. Update version in `src/utils/config.py` (`APP_VERSION`).
2. Update version in `src/ui/widgets/about_dialog.py` (`APP_VERSION`).
3. Update `app.cfg` default version.
4. Update `Changelog` in `docs/src/reference/changelog.md`.
5. Commit: `chore(release): bump version to X.Y.Z`.
6. Tag: `git tag vX.Y.Z`.
7. Push: `git push origin main --tags`.
8. Build EXE: `python scripts/builder.py --build`.
9. Create GitHub Release with the tag, attach EXE and checksums.

---

## Hotfix Process

For critical fixes on the released version:

1. Create branch from latest tag:
   ```bash
   git checkout -b fix/critical-bug vX.Y.Z
   ```

2. Apply fix, commit, push.
3. Open PR against `main`.
4. After merge, tag new patch version: `vX.Y.(Z+1)`.
5. Build and release.