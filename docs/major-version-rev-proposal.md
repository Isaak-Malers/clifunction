# clifunction major-version-rev proposal

Status: **proposal only** — nothing in this document has been implemented. Every finding below
was verified against the actual codebase/CI this session (commands shown), not inferred.
Current version: `0.2.4` (pre-1.0 — no public API stability promise yet, which matters for the
sequencing recommendation below).

## Framing

This is a stabilization moment, not a rewrite. The library is small (268 lines, zero runtime
deps, 22 passing tests, clean flake8/pylint) and the goal of a major rev is to fix the things
that are only cheap to fix *because* it's still pre-1.0 — namely the import-name break — then
land at `1.0.0` with a public API worth committing to for the AI-agent-writes-CLIs use case.

Four independent problem areas, verified separately below, then one sequencing plan.

## 1. Namespace normalization

Verified via `uv build` + `unzip -l`: the published wheel contains exactly one file,
`CliFunction.py`, loose at the top level (`[tool.hatch.build] include = ["CliFunction.py"]` —
`__init__.py` is not shipped). Five overlapping names, none reducible to the others:

| Name | What it is |
|---|---|
| `clifunction` | PyPI package name, repo directory name |
| `CliFunction` / `CliFunction.py` | the actual importable module after `pip install clifunction` |
| `cli_function` | the decorator |
| `cli` | the entry-point function |
| `Targets` | the class doing the work |

A user runs `pip install clifunction` and then must know to write `from CliFunction import
cli_function, cli` — the installed package name and the import name disagree in case *and*
punctuation. This is the concrete thing "confusing" refers to; the decorator/entry-point names
(`cli_function`, `cli`) are fine on their own and don't need to change.

**Proposal:** restructure the distribution so `import clifunction` works and ships the real
public surface — `from clifunction import cli_function, cli, CliFunctionException, Targets`.
Retire `CliFunction.py` as the installed artifact.

**Migration cost:** this breaks every existing `from CliFunction import ...` line for anyone
already depending on it. Two options:

- **Clean break** (recommended): ship the rename as part of `1.0.0`, changelog it clearly,
  no shim. Justification: the package is `0.2.4` — no SemVer stability promise has been made
  yet, so this is the last release where breaking the import path is free. A temporary
  `CliFunction.py` shim (`from clifunction import *` + `DeprecationWarning`) is the alternative
  but adds permanent-feeling cruft to a library whose entire value is having none — and per
  standing instruction, backwards-compat shims aren't the default move here.
- **Shim for one release**, only if there's a known external consumer beyond Isaak who needs
  warning. Worth a direct question to Isaak rather than a unilateral call — he's the one who
  knows if anyone else imports this today.

## 2. Type decomposition

Two separate findings under this heading, both verified with `mypy` (not currently in CI —
neither `flake8` nor `pylint` catch these):

```
$ uv run --with mypy mypy CliFunction.py
CliFunction.py:21: error: Bracketed expression "[...]" is not valid as a type  [valid-type]
CliFunction.py:75: error: Bracketed expression "[...]" is not valid as a type  [valid-type]
CliFunction.py:89,110,117,123,127: error: Incompatible return value type (got "None", expected "dict[Any, Any]")
CliFunction.py:147,159,254: error: Bracketed expression "[...]" is not valid as a type
Found 11 errors in 1 file (checked 1 source file)
```

**a) Annotation syntax is wrong, not just unconventional.** `args: [str]`, `-> [str]` (six call
sites: lines 21, 75, 147, 159, 254 and the `recursiveTargets` declaration) use a list *literal*
containing the type, not `List[str]`/`list[str]`. This runs fine today because Python doesn't
evaluate annotations as types at runtime unless something introspects them — but it means the
library's own public method signatures are not type-checker-clean, on a library whose pitch is
"fully annotate your functions." Fix: `list[str]` (project already requires 3.8+; `list[str]`
without `from __future__ import annotations` needs 3.9+, so either bump the floor or use
`typing.List[str]` — decide as part of this line item).

**b) Return types don't account for the `None` sentinel.** `generate_method_kwargs` and
`collect_method_kwargs` are annotated `-> dict` but return `None` on every non-match path (by
design — `None` *is* the "no match" signal). Should be `-> dict | None` / `Optional[dict]`.
This isn't cosmetic: it's the exact shape of the missing-required-arg gap in section 3 — the
type signature currently lies about when the function can fail to produce a dict.

**Proposal:**
- Fix all annotations to be accurate (`list[str]` or `List[str]`, `Optional[dict]` where `None`
  is a real return path).
- Add `mypy` to `code-quality.yml` as a third check alongside flake8/pylint, dev-only dependency
  (passes the zero-runtime-dep bar — see `maintainer-taste` skill).
- **Module decomposition**, separate from the annotation fix, gated on whether it's worth the
  "read in one sitting" tradeoff (`maintainer-taste` skill takes this seriously — don't skip the
  self-check just because a rewrite is already in motion). If pursued, split along actual domain
  boundaries rather than arbitrarily:

  | Module | Domain | Carries |
  |---|---|---|
  | `exceptions.py` | wrapper-vs-target error distinction | nothing, just the exception type |
  | `naming.py` | abbreviation generation — pure string transform, no I/O | nothing persistent |
  | `coercion.py` | string→type conversion — pure, closed set of types | nothing persistent |
  | `parsing.py` | per-invocation kwarg-dict construction (uses naming + coercion) | candidate dict, owned, discarded after `execute` |
  | `targets.py` | registration (import-time, lives for process lifetime) + execution + help rendering | the `targets` list itself — this is the one genuinely long-lived, published piece of state in the whole library |
  | `__init__.py` | public surface only — `cli_function`, `cli`, `CliFunctionException`, `Targets`, nothing else, via `__all__` | — |

  Recommendation: do this. ~6 files, still under 400 total lines, and it makes the
  registration/parsing/execution split (currently readable only by tracing method calls) visible
  in the file tree — which matters more once agents are grepping this repo instead of reading it
  linearly. Keep re-exporting everything through `__init__.py` so `from clifunction import
  cli_function, cli` remains the *one* documented import regardless of internal layout.

## 3. Unit testing

Two concrete, verified-empty coverage gaps (confirmed via `grep -rn "TypeError\|missing" test/`
— zero hits):

- **Missing required keyword-only argument** is completely untested and currently produces an
  uncaught `TypeError` from the wrapped function (not a `CliFunctionException`) — verified by
  direct reproduction:
  ```
  needs_two:  {'a': 'hi'}
  TypeError: needs_two() missing 1 required keyword-only argument: 'b'
  ```
  This is the highest-value fix in this whole proposal relative to its size: validate that every
  non-defaulted `kwonlyarg` is present in `generate_method_kwargs` before returning a candidate
  dict, raise (or signal) a proper CLI-authored error instead. **This does not need to wait for
  the major version** — it's a bug fix with no API surface change, ship it independently first
  (see sequencing).
- **`recursiveTargets`** (`Targets.__init__`: `self.recursiveTargets: [Targets] = []`) is declared,
  typed, and never read or written anywhere else in the codebase or tests — dead, unfinished
  scaffolding for subcommand nesting that was never built. Under Isaak's own stated principle
  (no half-finished implementations), this needs a decision, not a default: either finish it
  (real nested-subcommand support — a real feature with real design work: how does abbreviation
  matching behave across a nesting boundary?) or delete it. **This is a question for Isaak, not
  a call this proposal makes** — worth surfacing directly rather than guessing.

**Proposal:** close both gaps as independent PRs (see sequencing), and once the module split in
section 2 lands, add one test file per new module boundary rather than per original method name —
`unit-testing` skill's "one file per method" convention should be re-read as "one file per public
boundary" once boundaries are real modules, not just methods on one class.

## 4. AI-first feature proposals

Each evaluated against `maintainer-taste`'s gate (zero runtime deps, no new config surface,
convention over configuration, deterministic plain-text output). Only proposals that pass are
recommended; rejected ones are listed with why, so they don't get silently re-proposed later.

### Recommended

| Proposal | Why it passes the gate |
|---|---|
| **Machine-readable introspection** (`cli(args=['--schema'])` → JSON: target names, abbreviations, docstring, args with type+default) | `json` is stdlib. Lets an agent enumerate a CLI's full contract without regex-scraping the human man page or guessing abbreviations. This is the single highest-leverage "AI-first" change — everything else in this table is secondary to an agent being able to ask "what can I call and how" structurally. |
| **Validate-before-call for required args** (from section 3) | Already justified above; also directly serves agents, who currently get a misattributed traceback instead of a usable error. |
| **Differentiated exit codes** (e.g. `2`=no match, `3`=ambiguous, `4`=target itself raised, `1` reserved for "no args given") | stdlib only. Lets an agent branch on failure *kind* without parsing stdout text. Breaking change to the exit-code contract (currently anything nonzero is just "failed") — bundle with the major bump. |
| **Closed extension of `type_coercer`** for `pathlib.Path`, `enum.Enum` subclasses, and `Optional[T]` unwrapping | All stdlib. Real, common annotation shapes that currently silently fail to coerce (any non-str/bool/int/float annotation → `type_coercer` returns `None` → the whole candidate is dropped as "no match," with no error explaining why). Must stay a **closed, enumerated set** of newly-supported types, not an open coercion-plugin registry — an open registry is exactly the kind of speculative extensibility `maintainer-taste` flags as scope creep. |

### Rejected (don't re-propose without new information)

| Proposal | Why it fails the gate |
|---|---|
| Rich/colorized terminal output, progress bars | New runtime dependency; breaks deterministic plain-text output an agent parses. |
| Config-file-driven behavior (`.clifunctionrc` etc.) | New config surface; contradicts convention-over-configuration, the core pitch. |
| Open plugin/coercion registry | Unbounded surface growth; every future type becomes "just register a plugin" instead of a reviewed addition. |
| Async target functions | Not something anyone has asked for; real design cost (how does `execute` await); no evidence it's needed for the agent-writes-quick-CLIs use case, which skews toward small synchronous scripts. |

## Sequencing (matches the "small, atomic, no long-running branches" habit)

Independent PRs, no major-version bump needed, can ship this week if desired:

1. Fix missing-required-arg → proper `CliFunctionException`, with a regression test written
   first (per `unit-testing` skill).
2. Decision + action on `recursiveTargets` (delete, or scope a real nested-subcommand design) —
   needs Isaak's call before either branch starts.
3. Fix the six `[str]`-literal annotations and the `Optional[dict]` return types; add `mypy` to
   `code-quality.yml`.

Bundled into the `1.0.0` major-version rev, because they share the one genuinely breaking
change (the import path) and there's no value in making users absorb two separate breaking
releases:

4. Package restructure: `CliFunction.py` → `clifunction/` package per the module table in
   section 2. Update `[tool.hatch.build]` include list accordingly (verify the new wheel
   contents with `unzip -l`, per `version-validation` skill step 3 — this is exactly the kind of
   change that step exists for).
5. `--schema` JSON introspection output.
6. Differentiated exit codes.

Evaluate after 4–6 ship and are in real use, not bundled speculatively:

7. Extended type coercion (`Path`, `Enum`, `Optional[T]`).

Each numbered item is its own branch/PR against an issue, per the repo's existing contribution
process in `README.md` — nothing here proposes changing that process.
