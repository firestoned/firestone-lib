![PR Build](https://github.com/ebourgeois/firestone-lib/actions/workflows/pr.yml/badge.svg)

# firestone-lib

Firestone-lib is a shared toolkit that powers Firestone services and any downstream automation that needs to load schema resources, wire up CLI utilities, or work with reusable helpers. It packages common building blocks so projects across the ecosystem can stay consistent without duplicating code.

## Firestone Ecosystem

This library supports companion projects that build on the same patterns:

- [`firestone`](https://github.com/firestoned/firestone) turns JSON Schema resources into OpenAPI, AsyncAPI, CLI, and Streamlit artifacts.
- [`forevd`](https://github.com/firestoned/forevd) uses `firestone-lib`'s CLI and templating helpers to render Apache proxy configs with pluggable auth.

## Features
- Schema helpers that load JSON or YAML, resolve `$ref` links with `jsonref`, and validate against canonical Firestone schemas.
- CLI utilities built on top of `click`, including rich parameter types, templated input handling, and logging bootstrap helpers.
- Lightweight string utilities (for example, `split_capitalize`) that keep naming logic consistent across projects.
- Bundled configuration assets such as default logging definitions.

## Project Structure
- `firestone_lib/cli.py` – click helpers, logging setup, and custom parameter converters.
- `firestone_lib/resource.py` – schema loading, templating, and validation logic.
- `firestone_lib/utils.py` – general-purpose helpers shared by Firestone services.
- `firestone_lib/resources/` – packaged config files (for example, `logging/cli.conf`).
- `test/` – pytest-based regression and unit tests covering the public surface.

## Installation

### Prerequisites
- Python 3.12 or newer (see `pyproject.toml` for the precise compatibility range)
- [Poetry](https://python-poetry.org/docs/#installation)

### From source
```bash
poetry install
```

This installs the library and all development dependencies into Poetry's virtual environment. To enter the environment, run `poetry shell` or prefix commands with `poetry run`.

### From PyPI (consumer projects)
```bash
pip install firestone-lib
```

## Quick Start
Loading and validating a resource definition:

```python
from firestone_lib import resource

schema = resource.get_resource_schema("path/to/resource.yaml")
# Raises jsonschema.ValidationError on failure
resource.validate({"apiVersion": "v1", "kind": "Example", "spec": {}})
```

Setting up CLI logging from a packaged configuration:

```python
from firestone_lib import cli

cli.init_logging("firestone_lib.resources.logging", "cli.conf")
```

Normalizing identifiers for UI display:

```python
from firestone_lib import utils

print(utils.split_capitalize("firestone_resource"))  # Firestone Resource
```

## Development Workflow
- Use type hints and reStructuredText docstrings throughout the codebase (see `.github/instructions/python.instructions.md` for the full style guide).
- Consult `.github/copilot-instructions.md` for architecture notes and expectations when planning larger changes.
- Format changes with `poetry run black .` (line length 100) only when necessary.
- Keep logging statements descriptive and consistent with existing `_LOGGER` usage.

## Testing

Run the test suite before submitting changes:

```bash
poetry run pytest
```

CI mirrors this command through `.github/workflows/pr.yml`.

## Contributing

Issues and pull requests are welcome. When proposing a change, include the context, tests, and any documentation updates that ensure downstream services can adopt the update smoothly.

## License

Licensed under the Apache License 2.0 – see `LICENSE` for details.
