from expected import DUMMY_CLI_MAN_PAGE


class TestManPage:
    """
    The man page is the tool's only documentation surface -- generated purely from the
    registered targets' docstrings and type annotations, no separate doc source to drift.
    """

    def test_no_args_prints_full_man_page_and_exits_nonzero(self, run_tool):
        result = run_tool("dummy_cli.py")
        assert result.returncode == 1
        assert result.stdout == DUMMY_CLI_MAN_PAGE
        assert result.stderr == ""

    def test_unknown_target_reprints_man_page_after_a_no_matches_line(self, run_tool):
        result = run_tool("dummy_cli.py", "this_target_does_not_exist")
        assert result.returncode == 1
        prefix = "No Matches found for args: ['dummy_cli.py', 'this_target_does_not_exist']\n"
        assert result.stdout == prefix + DUMMY_CLI_MAN_PAGE
