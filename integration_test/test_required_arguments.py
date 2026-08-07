class TestRequiredArguments:
    """
    A required (no-default) keyword-only argument omitted at call time is treated as an
    ordinary no-match -- the same as any other unresolvable invocation -- rather than reaching
    the target and letting its own TypeError leak through.
    """

    def test_missing_required_argument_is_a_clean_no_match(self, run_tool):
        result = run_tool("dummy_cli.py", "add", "--first=2")
        assert result.returncode == 2  # EXIT_NO_MATCH
        assert "No Matches found" in result.stdout
        assert result.stderr == ""

    def test_missing_required_argument_does_not_reach_the_target(self, run_tool):
        # The echo line ("add:  {...}") only prints once a candidate is committed to and about
        # to run -- it must not appear here, since this should never be treated as a match.
        result = run_tool("dummy_cli.py", "add", "--first=2")
        assert "add:" not in result.stdout
