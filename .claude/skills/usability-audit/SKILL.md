---
name: usability-audit
description: Use when auditing what a clifunction-built CLI actually does at the terminal — help text, error text, exit codes, ambiguity handling — for both a human reading it and an agent driving it. Run against Example.py or any target file.
---

# Auditing clifunction CLI usability

This audits *behavior at the terminal*, not source code style. Run the target file directly and
read the actual output — don't infer it from `CliFunction.py`. Every check below is a command
you actually run.

## Checklist

For a target file `X.py` built with clifunction:

1. **No-args man page.** `python X.py` → must print the full man page and exit non-zero (`1`).
   This is the CLI's self-documentation; it must be complete and correct with zero flags.
   ```
   $ python Example.py; echo "EXIT:$?"
   Example.py
       deploy -- builds*, tests*, and then deploys the code!
           build_first | default:True | type:<class 'bool'>
           ...
   EXIT:1
   ```
2. **Unknown target.** `python X.py bogus` → prints `No Matches found for args: [...]` followed
   by the full man page, exits `1`. Check the man page reprint isn't so long it buries the "no
   matches" line for a human scrolling back — if a target file has 20+ functions, this reprint
   becomes noise; flag it.
3. **Ambiguous abbreviation.** Two+ targets sharing an abbreviation → `Multiple Matches found for
   args: [...]` then each candidate with its resolved kwargs, exits `1`. Verify every listed
   candidate is genuinely plausible from what the user typed — if the list includes a candidate
   that doesn't obviously relate to the input, that's a `name_and_abbreviations` collision worth
   flagging upstream (see `unit-testing`'s abbreviation-collision matrix).
4. **Happy path echo.** A successful call prints `function_name:  {resolved kwargs}` before
   running. Confirm this line alone is enough to tell an agent what actually got invoked and
   with what values — no silent argument coercion (e.g. a typo'd flag name should not silently
   resolve to a same-shaped different argument).
5. **Missing required argument.** Call a target missing a required keyword-only arg. As of this
   audit, this leaks a raw Python `TypeError` traceback instead of a clean CLI error — this is
   the single worst thing in the current UX for an agent, because the traceback looks like a bug
   in the *target* function, not a usage error:
   ```
   $ python -c "...call needs_two(a='hi') missing b..."
   needs_two:  {'a': 'hi'}
   TypeError: needs_two() missing 1 required keyword-only argument: 'b'
   ```
   An agent parsing this will likely try to "fix" the target function instead of retrying with
   the right flag. Flag every occurrence of this as a P1 usability bug, not a style nit.
6. **Bool flag symmetry.** For every bool kwarg, verify both `--flag` (bare, coerces to `True`)
   and `--flag=false`/`--flag=true` work, and that `--flag=maybe` or similar garbage returns "no
   match" rather than silently defaulting. `type_coercer` only accepts
   `true/t/y/yes` / `false/f/n/no` (case-insensitive) — anything else is `None`, which means the
   whole candidate is dropped silently rather than reported as "bad value for `--flag`". A human
   sees "no matches found"; they can't tell if they mistyped the target name or the value. Note
   this ambiguity when auditing.
7. **Docstring quality, not just presence.** `add_target` only requires *a* docstring — it says
   nothing about content. Read every docstring in the man page as a first-time user would: does
   it read as a sentence explaining what happens, or as a code comment? (`Example.py`'s `build`
   docstring — `"Python is Interpreted!"` — is a joke, not documentation; don't let real target
   files ship with placeholder-quality docstrings.)
8. **Zero-arg function formatting.** Functions with no kwonly args currently render a trailing
   empty indented line in the man page (`build -- ...\n\t\t`). Cosmetic, not a blocker — note it,
   don't block a release over it alone.
9. **Exit codes are binary.** Success → `0` (implicit, no `sys.exit` call). Any failure to
   dispatch → `1` (`raise SystemExit(1)`). There is currently no way to distinguish "no such
   target" from "ambiguous target" from "target ran and the target itself failed" by exit code
   alone — an agent scripting around this can't branch on exit code for anything finer than
   pass/fail. Note this as a limitation if the audited use case needs finer-grained scripting.
10. **stdout only, nothing interactive.** Confirm the target file introduces no `input()`
    prompts, no ANSI color, no progress bars. clifunction itself is clean on this; the audit is
    to catch a *target file* author reintroducing it inside their own function bodies.

## Severity guide

- **P1** — output that misattributes a usage error to the wrong place (item 5) or silently
  drops information a human/agent needed to retry correctly (item 6's silent drop).
  - **P2** — missing exit-code granularity, verbose reprints on error (items 2, 9).
  - **P3** — cosmetic (item 8) or docstring-content quality (item 7) — real, but not blocking.

Report findings against this severity guide, not as an undifferentiated list.
