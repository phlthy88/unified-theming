# AGENTS.md

## Overview

The `unified_theming` package provides a set of parser utilities for extracting tokens from source or theme files. The repository contains:

- `unified_theming/parsers/` – parser implementations, e.g., `json_tokens`.
- `examples/tokens/` – example token files for usage.
- `tests/` – unit tests exercising the parser logic.

## Directory Layout

```
unified_theming/
└─ parsers/
    ├─ __init__.py
    └─ json_tokens.py
examples/
└─ tokens/
tests/
└─ test_json_token_parser.py
```

## Building & Testing

This is a pure Python library; no explicit build step is required. Typical test command (depending on project's convention):

- `pytest` – discovers and runs tests in the `tests/` directory.
  - If `pytest` is not available, the standard library runner may be used: `python -m unittest discover`.

## Code Conventions

- Python 3, snake_case modules.
- Docstrings and comments follow standard PEP 257/8 style.
- Type hints are used sparingly; functions typically return `Iterable` or tuples.

## Usage Example

```python
from unified_theming.parsers.json_tokens import parse_tokens

tokens = parse_tokens("path/to/example.json")
for token in tokens:
    print(token)
```

## Known Gotchas

- JSON parser expects a specific structure (key/value pairs). Unexpected keys may raise `ValueError`.
- Example tokens reside in `examples/tokens`. Ensure file paths are absolute or relative to the current working directory.

## Contributing

- Add tests under `tests/`.
- Keep the code PEP8 compliant.
