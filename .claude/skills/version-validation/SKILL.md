---
name: version-validation
description: Use before any push to main, or before recommending Isaak push to main. clifunction auto-publishes to PyPI on every push to main with no approval gate — this is the pre-flight check that CI itself does not provide.
---

# Pre-publish validation for clifunction

## The mechanism this exists to guard

`.github/workflows/publish-package.yml` triggers on **every push to `main`** and runs
`python -m build && twine upload ... dist/*` unconditionally — no "is this a release" check, no
manual approval environment, no version-bump gate. Three other workflows also fire on the same
push: `automated-tests.yml`, `code-quality.yml` (both on push to any branch), and
`deploy-pages.yml` (main only). A push to main is simultaneously: a test run, a lint run, a
PyPI publish attempt, and a docs-site deploy. Treat it as all four.

**The only thing currently stopping an accidental duplicate publish is PyPI itself rejecting a
re-upload of an unchanged version number.** That's a failure discovered mid-CI-run, not a
preventative local check. This skill is that preventative check, run before the push happens.

## Checklist, in order

1. **Tests pass, run the way CI runs them.** `pytest ./test` from repo root (see `unit-testing`
   skill for why "from repo root" matters — the relative imports break otherwise).
   `automated-tests.yml`'s matrix covers Python 3.8–3.12. If the local interpreter is outside
   that range (verify with `python3 --version`), passing locally is not proof CI will pass —
   note the gap explicitly rather than asserting confidence you don't have. As of this check,
   the matrix does not include 3.13/3.14 even though `requires-python = ">=3.8"` has no upper
   bound — flag this mismatch if a change specifically depends on 3.13+ behavior.
2. **Lint is clean, exactly as CI invokes it** (both must exit 0, don't approximate with a
   subset):
   ```bash
   flake8 .
   pylint --disable=line-too-long,invalid-name,missing-module-docstring ./*.py
   pylint --disable=line-too-long,invalid-name,missing-module-docstring,import-error,missing-class-docstring,comparison-of-constants,missing-function-docstring,too-few-public-methods,R0801 ./test/*.py
   ```
3. **Build succeeds and ships what you think it ships.** `python -m build` or `uv build`, then
   actually open the wheel (`unzip -l dist/*.whl`) and confirm the file list matches
   `[tool.hatch.build] include`/`exclude` in `pyproject.toml`. This project's build ships exactly
   one file (`CliFunction.py`) — if a change added a new module, a new resource, or renamed
   something, it will silently *not* be in the published package unless `include` was updated
   too. This has no test coverage; it's a manual check every time `include`/`exclude` or the
   module layout changes.
4. **Version was actually bumped, and bumped in the one place that matters.** `version` lives in
   `pyproject.toml`'s `[project]` table only — there is no `__version__` string inside
   `CliFunction.py` to keep in sync (confirm this is still true; if a future change adds one,
   this checklist needs a second line item). If the version wasn't bumped, the push will still
   fire the publish job and fail there — better to catch it here than watch a red CI run.
5. **`mkdocs build -s` succeeds**, matching what `deploy-pages.yml` runs (`-s` is strict mode —
   it fails on broken links/references, not just build errors). `docs/index.md` is also the
   `readme` referenced in `pyproject.toml`, so it's rendered in two different places (PyPI
   project page, and the docs site) — check it reads correctly as both a standalone doc and a
   PyPI long-description.
6. **Diff the actual change against what four separate CI jobs will do with it**, not just
   against "does the feature work." A one-line change to `pyproject.toml` (e.g. this session's
   `[dependency-groups]` addition) still triggers all four workflows on push — small diff,
   full blast radius, because the trigger is "pushed to main," not "touched publishable code."

## What this skill does not cover

Actually pushing, or authorizing a push — that decision belongs to Isaak per the standing
instruction to review before commit/push (global `CLAUDE.md`). This skill's job is to make sure
that when he does push, nothing above surprises him mid-CI.
