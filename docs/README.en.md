# MYCELIUM CORE - Documentation Source

This directory contains the source files for the project's
documentation, including MkDocs markdown files, PlantUML diagrams,
and BPMN process models.

## Documentation Artifacts

| Artifact | Location | Description |
|:---|:---|:---|
| MkDocs Site | `docs/src/` | 70+ pages, EN/RU bilingual |
| PlantUML Diagrams | `docs/src/diagrams/sources/uml/` | 17 UML diagrams |
| BPMN Processes | `docs/src/diagrams/sources/bpmn/` | 6 BPMN 2.0 models |
| Rendered SVG | `docs/src/assets/diagrams/` | Auto-generated from sources |
| Screenshots | `docs/src/assets/images/screenshots/` | 10 application screenshots |
| Figma Mockups | [View in Figma](https://www.figma.com/design/PWzJmLP7TrrbjcL6F85KoU/mycelium-core) | 4 tabs, 53 notes, light theme |

## Documentation Sections

| Section | Pages | Description |
|:---|:---|:---|
| Getting Started | 3 | Installation, first run, quick tour |
| User Guide | 5 | Admin, Vote, Audit, Logs tabs |
| Architecture | 11 | Overview, layers, components, data flow, 7 ADRs |
| Diagrams | 23 | UML + BPMN catalog with notes |
| API Reference | 10 | All core modules |
| UI Design | 6 | Design system, colors, typography, components, icons, Figma |
| Security | 4 | Threat model, SEC checks, audit procedure, limitations |
| Deployment | 4 | Source, PyInstaller, distribution, troubleshooting |
| Development | 5 | Setup, testing, style guide, contributing, git workflow |
| Reference | 5 | SRS, docs SRS, changelog, glossary, FAQ, license |

## Prerequisites

To build the documentation and render the diagrams, you need:

1. **Python 3.11+**
2. **Java Runtime Environment (JRE)** -- required for PlantUML diagram
   generation.

## Setup

Install the required Python dependencies:

```bash
pip install -r requirements-docs.txt
```

To render UML diagrams locally, download
[`plantuml.jar`](https://github.com/plantuml/plantuml/releases/)
and place it inside this `docs/` directory. The file must be named
exactly `plantuml.jar`.

> **Note:** `plantuml.jar` is not included in the repository.
> Download it manually from the official PlantUML releases page
> and place it at `docs/plantuml.jar` before running the build script.

## Running Locally

The project includes a custom builder script that automatically
compiles all `.puml` files into SVG/PNG and starts the MkDocs
live-reload server.

Run from the root of this `docs/` folder:

```bash
python scripts/build_docs.py
```

Then open `http://127.0.0.1:8000` in your browser.

## Strict Build (CI/CD check)

To verify there are no broken links:

```bash
mkdocs build --strict
```

## Links

| Resource | Link |
|:---|:---|
| Figma Mockups | [View only](https://www.figma.com/design/PWzJmLP7TrrbjcL6F85KoU/mycelium-core) |
| MkDocs Material | [Documentation](https://squidfunk.github.io/mkdocs-material/) |
| PlantUML | [Releases](https://github.com/plantuml/plantuml/releases/) |
| Camunda Modeler | [Download](https://camunda.com/download/modeler/) |