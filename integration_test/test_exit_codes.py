class TestExitCodes:
    """
    Exit codes are differentiated: 0 means a target ran; a caller can branch on failure *kind*
    (no args given / no target matched / ambiguous match) without parsing stdout text.
    """

    def test_no_args_given_exits_1(self, run_tool):
        result = run_tool("dummy_cli.py")
        assert result.returncode == 1

    def test_no_target_matched_exits_2(self, run_tool):
        result = run_tool("dummy_cli.py", "bogus")
        assert result.returncode == 2

    def test_ambiguous_match_exits_3(self, run_tool):
        result = run_tool("dummy_cli.py", "ao")
        assert result.returncode == 3

    def test_all_three_failure_kinds_have_distinct_codes(self, run_tool):
        no_args = run_tool("dummy_cli.py")
        no_match = run_tool("dummy_cli.py", "bogus")
        ambiguous = run_tool("dummy_cli.py", "ao")
        codes = {no_args.returncode, no_match.returncode, ambiguous.returncode}
        assert codes == {1, 2, 3}

    def test_success_exits_0(self, run_tool):
        result = run_tool("dummy_cli.py", "greet")
        assert result.returncode == 0
