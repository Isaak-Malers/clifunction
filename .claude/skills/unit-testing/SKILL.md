---
name: unit-testing
description: Use when writing or reviewing tests in this repo's test/ directory. Covers the relative-import quirk that determines how tests must be run, the existing one-file-per-method convention, and the currently untested failure modes.
---

# Writing tests for clifunction

## The relative-import quirk (read this first, it will bite you)

Every test file imports with a double-relative import:

```python
from ..CliFunction import Targets
```

That only resolves if `test/` is imported as a subpackage of the repo root package (repo root
has `__init__.py`, `test/` has `__init__.py`). In practice this means:

- Run pytest **from the repo root**: `pytest ./test` or `uv run pytest ./test`. Running pytest
  from inside `test/`, or invoking a single test file by path from elsewhere, breaks the import.
- A new test file goes in `test/`, uses the same `from ..CliFunction import ...` form, and needs
  no new `__init__.py` (one already exists at both levels).
- Do not "fix" this to an absolute `from CliFunction import ...` to make a single file runnable
  standalone — it would silently diverge from every other test file's import style and is a
  larger structural change (see the namespace-normalization discussion in the
  major-version-rev proposal) than a single test warrants.

## Existing convention: one test file per method under test

The suite currently mirrors `CliFunction.py`'s public surface almost 1:1:

| Test file | Exercises |
|---|---|
| `test_abbreviations.py` | `DefaultArgumentParser.name_and_abbreviations` |
| `test_generate_method_kwargs.py` | `DefaultArgumentParser.generate_method_kwargs` (the bulk of the parsing logic) |
| `test_collect_method_kwargs.py` | `Targets.collect_method_kwargs` |
| `test_execute.py` | `Targets.execute` |
| `test_function_help.py` | `Targets.function_help` |
| `test_invalidTargets.py` | `Targets.add_target` failure paths |
| `test_canary.py` | CI plumbing only (both tests are `@pytest.mark.skip`) — don't add real assertions here |

New behavior on an existing method goes in that method's existing file. A genuinely new method
gets a new file named `test_<method_name>.py`. Don't create a `test_misc.py` grab-bag.

## Fixture pattern already in use

Test target functions are `@staticmethod`s on the test class itself, not module-level functions
or a `conftest.py` fixture — e.g. `TestExecute.two`, `TestExecute.some_args`,
`TestExecute.special_address` reappear with identical bodies across multiple test files. This is
duplication *by design*: it keeps each test file self-contained and readable without chasing a
shared fixtures module. Follow it — don't refactor these into a shared `conftest.py` as a
drive-by cleanup; that's a real proposal (fixture consolidation) with its own tradeoff, not free.

## Known coverage gaps (verified empty — grep the suite yourself to recheck)

- **Missing required keyword-only argument is entirely untested.** No test constructs a target
  with a required kwonly arg and calls it with that arg omitted. This path currently raises an
  uncaught `TypeError` from the wrapped function itself (see `usability-audit` skill, item 5) —
  and because it's untested, a fix to validate-before-call has no regression guard today. If you
  fix this behavior, write the test *first*: assert the current (bad) behavior, watch it fail
  after the fix, then assert the new behavior. Don't fix silently untested code paths without a
  test proving what changed.
- **No test on `varargs`/`varkw` rejection at the `generate_method_kwargs` layer** — only
  `add_target` is tested for this (`test_invalidTargets.py`). If `generate_method_kwargs` is ever
  called directly against a `*args`/`**kwargs` function (bypassing `add_target`), behavior is
  unverified.
- **No coverage tool wired in** (`requirements-dev.txt`, `pyproject.toml` — neither declares
  `pytest-cov` or a `[tool.coverage]` section). Coverage gaps like the one above are found by
  reading `CliFunction.py` against `test/*.py` side by side, not by a report. If adding a
  coverage tool, that's a `[dependency-groups]` addition — check it against `maintainer-taste`
  first (dev-only deps are fine; this is not a runtime dependency).

## What a good test here looks like

Tests call `Targets`/`DefaultArgumentParser` methods directly with hand-built `args` lists —
never `subprocess`, never actually invoking `python X.py`. That's consistent with keeping the
suite fast (22 tests run in ~0.05s) and keeps assertions on return values, not on captured
stdout. If you're tempted to assert against printed output, use `Targets.printer` — it's
"only here so that this object is easy to mock/patch for unit tests" per its own docstring; wire
a test double there instead of capturing real stdout.
