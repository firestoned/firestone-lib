# Firestone-lib Copilot Instructions

## Project Scope
- Firestone-lib bundles shared capabilities used across the broader Firestone ecosystem: CLI utilities, schema tooling, and lightweight helpers.
- Consumers expect stable interfaces; keep changes backward-compatible unless a coordinated release states otherwise.

## Ecosystem Awareness
- `firestone` consumes these helpers for spec generation; validate CLI or resource-facing changes against its workflows (see `firestone/__main__.py` and `firestone/spec/`).
- `forevd` depends on `firestone_lib.cli` for logging and config parsing—document any behavior shifts so the proxy can bump in lockstep.
- If a change requires synchronized updates, land `firestone-lib` first and surface follow-up PR references in the release notes or change description.

## Architecture Overview
- `firestone_lib/cli.py`: click-based helpers (logging bootstrap, custom param types, async wrappers). Extend here when exposing new CLI behavior.
- `firestone_lib/resource.py`: schema ingestion/validation built around `jsonref` and `jsonschema`; reuse its loaders to keep `$ref` support intact.
- `firestone_lib/utils.py`: string-centric helpers used across Firestone services.
- `firestone_lib/resources/`: packaged configuration assets (for example, logging config in `logging/cli.conf`).
- Tests mirror the package layout under `test/`.

## Build & Automation
- Poetry drives installs, builds, and test runs (`poetry install`, `poetry build`, `poetry run pytest`).
- Continuous integration is handled via `.github/workflows/pr.yml`; expect linting and tests to run on every pull request.
- Local pre-flight: run `poetry run pylint firestone_lib test` and `poetry run pytest --cov=firestone_lib --cov-report term-missing` before opening a PR. CI enforces both commands, and we aim to keep coverage at 100%.

## Collaboration Notes
- Before adding new modules or resources, confirm they fit the existing structure; prefer evolving current packages.
- Keep logging messages meaningful and consistent with existing `_LOGGER` usage.
- When working on CLI or schema changes, ensure templating, environment-variable substitution, and file loading continue to behave as they do today.

## Coding Conventions
- For language-level expectations (Python 3.9+ compatibility, mandatory type hints, pytest usage, formatting requirements), follow `.github/instructions/python.instructions.md`.
- When adding tests, include docstrings or inline comments for helper classes/overrides so pylint passes without silencing warnings globally. Use targeted `# pylint: disable=` comments with a short justification when you must access module-private APIs like `_jsonloader`.
- Resource loaders rely on the current `file://` / `file:` path normalization; keep that behavior intact and update tests accordingly if you touch it.
