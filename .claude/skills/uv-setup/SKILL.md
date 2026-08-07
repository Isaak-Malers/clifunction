---
name: uv-setup
description: Use when setting up a dev environment for clifunction, adding a dev dependency, or extending package-manager support beyond pip. Documents what's already wired up and what wasn't touched on purpose.
---

# uv support for clifunction

clifunction is a **library**, not an installable app — there's no `[project.scripts]` entry
point and nothing to `uvx` run. "uv support" here means: a contributor (or an agent) can go from
a clean checkout to running tests/lint/build with `uv` alone, without also needing a manually
`pip install`-ed environment:

```bash
uv sync              # creates .venv, installs the project + dev dependency-group
uv run pytest ./test # tests
uv run flake8 .
uv run pylint ...
uv build             # produces the same wheel as `python -m build` — same hatchling backend
```

## What makes that true

- `[dependency-groups]` (PEP 735) in `pyproject.toml`, populated via
  `uv add --dev pytest flake8 mkdocs pylint` — this is the modern equivalent of a
  `requirements-dev.txt`, resolved by uv (and by any PEP-735-aware tool, not uv-specific).
- `uv.lock` — commit this. It's what makes `uv sync`/`uv run` reproducible across machines; without
  it uv still works but re-resolves dependency versions each time.
- `.venv/*` in `.gitignore` (the `venv/*` pattern alone doesn't match uv's default `.venv`
  directory name — both are ignored).
- `.flake8` has `exclude = .venv,venv,dist,build,.git`. Without it, `flake8 .` recurses into
  `.venv/lib/.../site-packages` and reports thousands of unrelated errors from installed
  packages. `pylint` is unaffected because both CI invocations glob explicit paths
  (`./*.py`, `./test/*.py`) rather than recursing from `.`.

Nothing in the library source or the wheel-building mechanism is uv-specific. `uv build` works
against this project's existing `hatchling` backend with zero special-casing — uv doesn't
require its own backend, it drives whatever PEP 517 backend the project already declares. That's
why "uv support" is cheap here: the project is standards-compliant enough that uv has nothing to
work around.

## What's deliberately left alone

- **`requirements-dev.txt` still exists and still works** (`pip install -r requirements-dev.txt`).
  Both paths (`pip` and `uv`) work independently — this is "support uv" not "replace pip." They
  can drift (e.g. a dependency-group version bump not mirrored in the txt file); there's no
  single source of truth between them. Collapsing that is a real proposal, not something to do
  as a drive-by — it touches CI, below.
- **CI workflows stay on plain `pip install`.** `automated-tests.yml` and `code-quality.yml`
  don't use `astral-sh/setup-uv`. Switching is a natural follow-up (faster installs, uses the
  committed lockfile for reproducibility) but CI changes ride on every push to main alongside the
  auto-publish job (see `version-validation` skill) — that's a higher-blast-radius change than a
  local dev-dependency table, and needs the Accountable Maintainer's review before push. Left as
  a recommendation, not applied.
- **No `[project.optional-dependencies]`.** Since there are zero runtime dependencies, there's
  nothing for an extras group to gate. Don't add one speculatively.

## Extending this later

- New dev tool → `uv add --dev <package>`, then run the version-validation checklist's lint/test
  steps to confirm it doesn't change CI-visible behavior, then check it against
  `maintainer-taste` (dev-only deps are cheap to approve; anything imported by the `clifunction`
  package itself is not).
- Other package managers (poetry, pdm, conda) were *not* separately tested — they weren't asked
  for. Since the project already round-trips through the standard `pyproject.toml` +
  `hatchling` PEP 517 interface, there's no structural reason they'd fail, but "no structural
  reason to fail" isn't the same as verified; test before claiming support.
