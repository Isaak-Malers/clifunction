# clifunction

A small, zero-runtime-dependency library that turns annotated Python functions into a CLI. The
whole contract: `@cli_function` + keyword-only args + type annotations + a docstring → a man
page and an invokable command, for free.

## Where things live

As of the `1.0.0` package restructure, `import clifunction` resolves to a real package
(`clifunction/`), not a loose top-level module — see "Namespace map" below for why that used to
be the confusing part.

| Symbol | Module | Role |
|---|---|---|
| `cli_function`, `cli`, `targets` | `clifunction/__init__.py` | public entry points + the module-level `Targets` singleton; thin glue only |
| `Targets` | `clifunction/targets.py` | registration (import-time, process-lifetime) + execution + help rendering; `add_target`/`execute`/`man`/`function_help` |
| `DefaultArgumentParser` | `clifunction/parsing.py` | per-invocation kwarg-dict construction (`generate_method_kwargs`); delegates to `naming`/`coercion` |
| `name_and_abbreviations` | `clifunction/naming.py` | pure string transform, no I/O |
| `type_coercer` | `clifunction/coercion.py` | pure string→type conversion, closed set of types |
| `CliFunctionException` | `clifunction/exceptions.py` | raised only for wrapper-authored mistakes (bad decoration), never for the wrapped function's own errors — see `maintainer-taste` skill |

Six files, ~230 total lines. `__init__.py` re-exports everything (`__all__`) so `from clifunction
import cli_function, cli, CliFunctionException, Targets, DefaultArgumentParser` remains the one
documented import regardless of internal layout — new code should extend the module whose domain
it belongs to (see the table), not get bolted onto `__init__.py`.

**Gotcha carried over from the old monolith:** a `# pylint: disable=X` comment scopes from where
it appears to the end of the enclosing block, not just "the next line." In the old single-file
layout, `type_coercer`'s `# pylint: disable=too-many-return-statements` silently also suppressed
that check on `generate_method_kwargs` further down the same class body — invisible until the
module split separated them and pylint caught the real violation. Don't assume a disable comment
found above one function is scoped to only that function; check where the enclosing block ends.

## Namespace map (was confusing; the `1.0.0` restructure fixed the load-bearing part)

- `clifunction` — PyPI package name, repo directory name, **and now the actual import name**
  (`from clifunction import ...`). Previously the wheel shipped a loose `CliFunction.py` module
  instead — that's what made `pip install clifunction` and the import disagree in case and
  punctuation. Fixed as part of `docs/major-version-rev-proposal.md` section 1.
- `cli_function` — the decorator. `cli` — the entry-point function end users call in their own
  `if __name__ == "__main__":` block. `Targets` — the class actually doing the work. These three
  names are still distinct on purpose; nothing wrong with them individually.

## Commands

```bash
# unit tests, in-process (from repo root -- pytest's rootdir path insertion is what makes
# `import clifunction` resolve without installing the package; see the unit-testing skill)
uv run pytest ./test -v          # or: pytest ./test -v inside a venv with pytest installed

# system/integration tests, black-box subprocess execs -- separate suite, separate concern
uv run pytest ./integration_test -v

# lint + types (all must be clean before anything merges — CI enforces this)
uv run flake8 .
uv run pylint --disable=line-too-long,invalid-name,missing-module-docstring ./*.py ./clifunction/*.py
uv run mypy clifunction/

# build
uv build                          # or: python -m build
```

`uv sync` / `uv run` work today via the `[dependency-groups]` table in `pyproject.toml` — see
the `uv-setup` skill for what that assumes and how to extend it. `pip install -r
requirements-dev.txt` still works as a parallel path; don't let the two drift silently.

### Python version floor: 3.8, and that's the real ceiling on going lower

`requires-python = ">=3.8"` isn't an arbitrary choice. Audited: the only version-sensitive
construct anywhere in `clifunction/*.py` is `from __future__ import annotations` (PEP 563,
introduced in Python **3.7** — no walrus operator, no positional-only params, no `match`
statement, no explicit `typing` imports). So 3.7 is the true language-feature floor, one version
below what you'd guess from the `list[str]`/`dict | None` annotation style.

But it's not achievable in CI, and don't re-derive this without checking first: verified live
(added `'3.7'` to `automated-tests.yml`'s matrix, pushed, watched it fail) that
`actions/setup-python` cannot provision Python 3.7 on `ubuntu-latest` (currently Ubuntu 24.04) —
`The version '3.7' with architecture 'x64' was not found for Ubuntu 24.04.` The
[python-versions manifest](https://raw.githubusercontent.com/actions/python-versions/main/versions-manifest.json)
still lists 3.7.x builds, but their prebuilt binaries only cover Ubuntu 20.04/22.04. Since we
can't test 3.7 in CI, we don't claim it in `requires-python` — 3.8 is the floor that's both
technically sound *and* provable.

## CI has a live wire

`.github/workflows/publish-package.yml` runs `twine upload --skip-existing` on **every push to
`main`** (currently manually disabled in the repo's Actions settings, pending re-enable). With
`--skip-existing`, an unchanged version silently no-ops instead of failing loudly — but a real
version bump still publishes normally, with no approval gate. Any change that touches `main`
should treat that as a real consequence, not a hypothetical — see the `version-validation` skill
before anything that could land on main.

Also: `branches: ['*']` in a workflow's `on.push` does **not** match branch names containing
`/` (GitHub's glob semantics — `*` doesn't cross `/`, only `**` does). `automated-tests.yml` and
`code-quality.yml` both had this bug and silently never ran on any `im/...`-prefixed branch;
fixed by dropping the branch filter entirely (bare `on: [push]`). Worth knowing if a workflow
ever appears to "just not trigger" on a branch — check this before assuming an outage or a
platform issue.

## Skills for this repo

- `maintainer-taste` — the decision framework for whether a proposed change belongs in this
  codebase at all. Load before proposing or reviewing any addition.
- `usability-audit` — checklist for auditing what a clifunction-built CLI actually does at the
  terminal (help text, error text, exit codes), for both a human and an agent driving it.
- `unit-testing` — how tests are organized here and where the boundary-coverage gaps currently are.
- `version-validation` — pre-publish gate given the auto-publish-on-push CI above.
- `uv-setup` — what `uv` support means for a library (not an app) and what's already wired up.

## In progress: major-version-rev (see `docs/major-version-rev-proposal.md`)

Working branch: `im/ver-1.0.0-prep`. Implementation status of the proposal's sequencing plan —
check this list before assuming something is or isn't done yet:

- [x] Missing required kwonly args are now treated as no-match instead of leaking a raw `TypeError`.
- [x] Dead `recursiveTargets` scaffolding removed.
- [x] Type annotations fixed (`list[str]`, `dict | None`, etc. via `from __future__ import
      annotations` — floor stays `>=3.8`); `mypy` added to `code-quality.yml`.
- [x] Package restructure `CliFunction.py` → `clifunction/` package, version bumped to `1.0.0`.
      Verified: clean venv, `pip install` the built wheel, `from clifunction import ...` works
      with zero path hacks.
- [x] `--schema` JSON introspection output (`Targets.schema()`, wired into `cli()` as a reserved
      flag that can't collide with a real target name/abbreviation).
- [x] Differentiated exit codes: `1`=no args, `2`=no match, `3`=ambiguous match, `0`=success
      (`clifunction.EXIT_NO_ARGS`/`EXIT_NO_MATCH`/`EXIT_AMBIGUOUS_MATCH`). "Target itself raised"
      deliberately left as Python's normal uncaught-exception behavior — see the `usability-audit`
      skill for why.
- Not scheduled yet (per the proposal, evaluate only after the above are shipped and in use):
  extended type coercion (`Path`, `Enum`, `Optional[T]`).

No runtime deps, and that's load-bearing — see `maintainer-taste`.
