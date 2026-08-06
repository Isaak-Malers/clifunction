# clifunction

A single-file, zero-runtime-dependency library that turns annotated Python functions into a
CLI. The whole contract: `@cli_function` + keyword-only args + type annotations + a docstring
→ a man page and an invokable command, for free.

## Where things live

| Symbol | File | Role |
|---|---|---|
| `cli_function` | `CliFunction.py` | decorator; registers a function with the module-level `targets` singleton at import time |
| `cli` | `CliFunction.py` | entry point; parses `sys.argv`, dispatches, prints the man page and exits 1 on any failure to match |
| `Targets` | `CliFunction.py` | holds registered functions for one file; `add_target`/`execute`/`man`/`function_help` |
| `DefaultArgumentParser` | `CliFunction.py` | abbreviation generation, string→type coercion, kwarg-dict construction from argv |
| `CliFunctionException` | `CliFunction.py` | raised only for wrapper-authored mistakes (bad decoration), never for the wrapped function's own errors — see `maintainer-taste` skill |

Everything lives in one module. There is no package-internal layering to preserve — see the
`major-version-rev` proposal in `docs/` for the case *for* splitting it, but until that lands,
new code goes in `CliFunction.py` next to what it extends, not into a new file.

## Namespace map (confusing on purpose right now, see proposal)

Five different spellings refer to overlapping things and are **not interchangeable**:

- `clifunction` — the PyPI package name and the repo directory name.
- `CliFunction.py` / `CliFunction` — the actual importable module after `pip install` (the built
  wheel ships this one file loose at the top level; `__init__.py` is **not** shipped — check
  `[tool.hatch.build] include` in `pyproject.toml`).
- `cli_function` — the decorator.
- `cli` — the entry-point function end users call in their own `if __name__ == "__main__":` block.
- `Targets` — the class actually doing the work.

When writing docs, tests, or skills, say which one you mean; "the CLI function thing" is not
resolvable. A major-version proposal to collapse this exists — see `docs/major-version-rev-proposal.md`.

## Commands

```bash
# tests (relative imports in test/*.py require running from repo root)
uv run pytest ./test -v          # or: pytest ./test -v inside a venv with pytest installed

# lint (both must be clean before anything merges — CI enforces this)
uv run flake8 .
uv run pylint --disable=line-too-long,invalid-name,missing-module-docstring ./*.py

# build
uv build                          # or: python -m build
```

`uv sync` / `uv run` work today via the `[dependency-groups]` table in `pyproject.toml` — see
the `uv-setup` skill for what that assumes and how to extend it. `pip install -r
requirements-dev.txt` still works as a parallel path; don't let the two drift silently.

## CI has a live wire

`.github/workflows/publish-package.yml` runs `twine upload` on **every push to `main`**, with no
version-bump guard and no manual approval gate. If `pyproject.toml`'s `version` isn't bumped,
the job fails on the duplicate-version upload (that's the only thing currently preventing an
accidental re-publish). Any change that touches `main` should treat that as a real consequence,
not a hypothetical — see the `version-validation` skill before anything that could land on main.

## Skills for this repo

- `maintainer-taste` — the decision framework for whether a proposed change belongs in this
  codebase at all. Load before proposing or reviewing any addition.
- `usability-audit` — checklist for auditing what a clifunction-built CLI actually does at the
  terminal (help text, error text, exit codes), for both a human and an agent driving it.
- `unit-testing` — how tests are organized here, the relative-import quirk, and where the
  boundary-coverage gaps currently are.
- `version-validation` — pre-publish gate given the auto-publish-on-push CI above.
- `uv-setup` — what `uv` support means for a library (not an app) and what's already wired up.

## Known gaps (found during exploration, not yet fixed)

- Missing required keyword-only args are not validated before the call — the wrapped function's
  own `TypeError` leaks through as a raw traceback instead of a clean CLI error. See
  `usability-audit` skill and the proposal doc.
- No runtime deps, and that's load-bearing — see `maintainer-taste`.
