---
name: maintainer-taste
description: Use when proposing, reviewing, or scoping a change to clifunction itself (not code that merely uses it). Decides whether an addition belongs in a single-file, zero-dependency CLI library, or is scope creep dressed as a feature.
---

# Maintainer taste for clifunction

clifunction's entire value proposition is that it is *small enough to read in one sitting* and
*trustworthy enough that an agent can generate a CLI with it without checking anything else*.
Every proposed change is judged against that, not against "is this a good feature in general."

## The load-bearing constraints

These are not style preferences — breaking them changes what the library *is*:

1. **Zero runtime dependencies.** `CliFunction.py` imports only `inspect`, `os`, `sys`, `re`.
   A change that needs `click`, `pydantic`, `rich`, or anything off PyPI is disqualified by
   default, no matter how good the feature is. If a feature truly cannot be done in stdlib,
   that's a signal it doesn't belong in this library.
2. **One file is the surface.** Someone should be able to `cat CliFunction.py` and understand
   the whole system. Splitting into modules is a packaging decision (see the major-version-rev
   proposal), not a place to smuggle in growth — don't let "let's clean this up" become "let's
   add a plugin system while we're in here."
3. **Convention, not configuration.** The entire contract is: decorator + keyword-only args +
   type annotations + docstring. No YAML, no config file, no `.clifunctionrc`. If a proposed
   feature needs a config file to be usable, it's the wrong feature for this library.
4. **The wrapper's errors and the wrapped function's errors are different species.**
   `CliFunctionException` exists specifically to make it "obvious when a problem occurs with the
   CLI wrapper vs the code being called into" (its own docstring says this — take it literally).
   Don't add a `try/except Exception` around the user's function call to "make errors nicer";
   that blurs the one distinction the exception type exists to preserve. Fixing the missing-arg
   TypeError leak (see `usability-audit`) means validating *before* the call, not catching *after*.
5. **Fail loud at decoration time, fail quiet at parse time.** `add_target` raises on any
   mistake the CLI *author* makes (bad signature, missing docstring) — those are bugs, caught at
   import. `generate_method_kwargs` returns `None` on anything the CLI's *end user* gets wrong
   from the terminal — that's normal input, handled by "no match" in the man page. Don't move
   validation across that line in either direction.

## Questions to ask before adding anything

Ask in this order — the first "no" ends the review:

1. Can this be done with what's already exposed (`cli_function`, `cli`, `Targets`,
   `CliFunctionException`), just used differently? If yes, it's a docs/example problem, not a
   code problem.
2. Does it require a new runtime dependency? If yes, stop — see constraint 1.
3. Does it add a new public symbol? If yes, what existing symbol's job shrinks to make room for
   it? A library that only ever grows its surface stops being "read in one sitting."
4. Does it require the CLI author to write anything beyond a decorated, annotated, documented
   function? If yes, it's raising the floor for every user to serve an edge case — push back
   toward an opt-in shape instead.
5. Is it testable at the same boundary the existing suite uses (`Targets`/`DefaultArgumentParser`
   methods, called directly, no subprocess)? If it needs a subprocess or a mock filesystem to
   test, the design is probably wrong for this codebase — see `unit-testing`.

## What "AI-first" means here, specifically

Isaak's stated reason for investing in this again: agents write throwaway CLIs constantly and
need a library that's cheap to reach for. That pulls in one direction only — *reduce the amount
an agent needs to know to use this correctly* — not "add features agents might want":

- Deterministic, plain-text output (man page, error text) — no ANSI color, no interactive
  prompts, no spinners. An agent piping stdout should get the same string every time.
- Errors that name the fix, not just the failure (`CliFunctionException` messages already do
  this — e.g. "requires exclusively keyword arguments" tells you what to change, not just that
  something's wrong). Hold new error paths to that bar.
- A docstring is the only documentation surface. If a feature can't be explained by "add a
  docstring," it's asking the CLI author to learn a second thing.

Do **not** read "AI-first" as "add a `--json` output mode" or "add a machine-readable schema
dump" without confirming that against constraint 3 above — those are real proposals, but they're
major-version-rev material with their own cost/benefit, not a taste-skill rubber stamp. See
`docs/major-version-rev-proposal.md`.

## Fast rejections (patterns seen in similar libraries — don't reintroduce them here)

- Subcommand nesting deeper than `Targets.recursiveTargets` already stubs, before anyone has
  asked for it.
- A second way to register targets (e.g. explicit `.register()` alongside the decorator).
- Config-file-driven behavior toggles.
- Silently catching and reformatting exceptions from user code (see constraint 4).
