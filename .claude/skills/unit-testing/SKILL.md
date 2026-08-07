---
name: unit-testing
description: Use when writing or reviewing tests in this repo's test/ directory. Covers how tests import the package, the existing one-file-per-method convention, and the currently untested failure modes.
---

# Writing tests for clifunction

## Imports and how they resolve

As of the `1.0.0` package restructure, tests import the real package directly:

```python
from clifunction import Targets
```

This is a plain absolute import — it works because pytest's default import mode inserts the
first ancestor directory *without* an `__init__.py` onto `sys.path`. `test/` has an
`__init__.py`; the repo root does not (its old one was removed as part of the restructure); so
the repo root lands on `sys.path`, and since `clifunction/` is a real package sitting right
there, `import clifunction` resolves — **without the project needing to be pip-installed**.
Verified by running `pytest ./test` in a venv that has only `pytest` installed, nothing else.

Practically:
- Still run pytest **from the repo root**: `pytest ./test` or `uv run pytest ./test`. That's what
  puts the repo root on `sys.path` in the first place.
- A new test file goes in `test/`, imports with `from clifunction import ...` like every existing
  file, no relative-import tricks needed.

(Before `1.0.0` this was `from ..CliFunction import Targets` — a double-relative import that only
worked because of a root-level `__init__.py` that no longer exists. If you see that old form
anywhere, it's stale and should be updated.)

## Existing convention: one test file per method under test

The suite mirrors the package's public surface almost 1:1 — file names describe the method, not
the module it now lives in (see `CLAUDE.md`'s module table for where each class actually is):

| Test file | Exercises |
|---|---|
| `test_abbreviations.py` | `DefaultArgumentParser.name_and_abbreviations` (→ `clifunction/naming.py`) |
| `test_generate_method_kwargs.py` | `DefaultArgumentParser.generate_method_kwargs` (→ `clifunction/parsing.py`) |
| `test_collect_method_kwargs.py` | `Targets.collect_method_kwargs` (→ `clifunction/targets.py`) |
| `test_execute.py` | `Targets.execute` |
| `test_function_help.py` | `Targets.function_help` |
| `test_invalidTargets.py` | `Targets.add_target` failure paths |
| `test_canary.py` | CI plumbing only (both tests are `@pytest.mark.skip`) — don't add real assertions here |

New behavior on an existing method goes in that method's existing file. A genuinely new method
gets a new file named `test_<method_name>.py`. Don't create a `test_misc.py` grab-bag, and don't
reorganize this file list to mirror the new module boundaries just because the module split
happened — the method-level granularity has been more stable than the file layout so far.

## Fixture pattern already in use

Test target functions are `@staticmethod`s on the test class itself, not module-level functions
or a `conftest.py` fixture — e.g. `TestExecute.two`, `TestExecute.some_args`,
`TestExecute.special_address` reappear with identical bodies across multiple test files. This is
duplication *by design*: it keeps each test file self-contained and readable without chasing a
shared fixtures module. Follow it — don't refactor these into a shared `conftest.py` as a
drive-by cleanup; that's a real proposal (fixture consolidation) with its own tradeoff, not free.

## Known coverage gaps (verified empty — grep the suite yourself to recheck)

- **No test on `varargs`/`varkw` rejection at the `generate_method_kwargs` layer** — only
  `add_target` is tested for this (`test_invalidTargets.py`). If `generate_method_kwargs` is ever
  called directly against a `*args`/`**kwargs` function (bypassing `add_target`), behavior is
  unverified.
- **No coverage tool wired in** (`requirements-dev.txt`, `pyproject.toml` — neither declares
  `pytest-cov` or a `[tool.coverage]` section). Coverage gaps are found by reading
  `clifunction/*.py` against `test/*.py` side by side, not by a report. If adding a coverage
  tool, that's a `[dependency-groups]` addition — check it against `maintainer-taste` first
  (dev-only deps are fine; this is not a runtime dependency).

Resolved, kept here as the template for how a gap gets closed: missing-required-kwonly-arg used
to be entirely untested and leaked a raw `TypeError` (see `usability-audit` skill history). Fixed
by writing the failing test first (`test_missing_required_arg_is_not_a_match`), watching it fail
against the old behavior, then fixing `generate_method_kwargs` to make it pass. That's the
pattern: assert current behavior fails were it should, fix, then assert the new contract — don't
fix a code path with no test proving what changed.

## What a good test here looks like

Tests call `Targets`/`DefaultArgumentParser` methods directly with hand-built `args` lists —
never `subprocess`, never actually invoking `python X.py`. That's consistent with keeping the
suite fast (24 tests run in ~0.02s) and keeps assertions on return values, not on captured
stdout. If you're tempted to assert against printed output, use `Targets.printer` — it's
"only here so that this object is easy to mock/patch for unit tests" per its own docstring; wire
a test double there instead of capturing real stdout.
