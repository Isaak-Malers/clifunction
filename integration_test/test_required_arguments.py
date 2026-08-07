class TestRequiredArguments:
    """
    Documents *current* behavior for a required (no-default) keyword-only argument omitted at
    call time -- this is a known rough edge, not a spec: generate_method_kwargs() doesn't check
    that every required kwonly arg got filled in before calling the target, so a partially-
    matched candidate reaches key(**value) and blows up with the wrapped function's own
    TypeError instead of a clean "no matches" the way any other unresolvable invocation does.

    If/when that gets fixed, these two assertions are exactly what should flip: the traceback
    disappears and this becomes an ordinary no-match, indistinguishable from any other bad
    invocation. That's the point of writing them this explicitly instead of just asserting
    `returncode != 0` -- the diff when it's fixed is the whole migration story for this behavior.
    """

    def test_missing_required_argument_currently_leaks_a_raw_traceback(self, run_tool):
        result = run_tool("dummy_cli.py", "add", "--first=2")
        assert result.returncode == 1
        # The echo line still prints -- generate_method_kwargs() had already committed to this
        # candidate before the call failed.
        assert result.stdout == "add:  {'first': 2}\n"
        assert "Traceback (most recent call last)" in result.stderr
        assert "TypeError: add() missing 1 required keyword-only argument: 'second'" in result.stderr

    def test_missing_required_argument_does_not_print_a_clean_no_match(self, run_tool):
        # Negative assertion, kept separate from the above so it's unambiguous which specific
        # claim breaks once this gets fixed: no "No Matches found" text appears anywhere today.
        result = run_tool("dummy_cli.py", "add", "--first=2")
        assert "No Matches found" not in result.stdout
