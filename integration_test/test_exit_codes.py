class TestExitCodes:
    """
    Documents *current* behavior: exit codes are binary. 0 means a target ran; every failure
    to dispatch -- no args given, no target matched, more than one target matched -- collapses
    to the same code, 1. A caller (human or agent) can't currently branch on failure *kind* by
    exit code alone, only on pass/fail.

    If exit codes ever get differentiated, this file is exactly what should change: each
    sub-case below would get its own expected code instead of sharing `1`.
    """

    def test_no_args_given_exits_1(self, run_tool):
        result = run_tool("dummy_cli.py")
        assert result.returncode == 1

    def test_no_target_matched_exits_1(self, run_tool):
        result = run_tool("dummy_cli.py", "bogus")
        assert result.returncode == 1

    def test_ambiguous_match_exits_1(self, run_tool):
        result = run_tool("dummy_cli.py", "ao")
        assert result.returncode == 1

    def test_all_three_failure_kinds_share_the_same_code(self, run_tool):
        no_args = run_tool("dummy_cli.py")
        no_match = run_tool("dummy_cli.py", "bogus")
        ambiguous = run_tool("dummy_cli.py", "ao")
        assert no_args.returncode == no_match.returncode == ambiguous.returncode == 1

    def test_success_exits_0(self, run_tool):
        result = run_tool("dummy_cli.py", "greet")
        assert result.returncode == 0
