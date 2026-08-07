from expected import DUMMY_CLI_MAN_PAGE


class TestAbbreviations:
    """
    Auto-generated shorthand resolution for both target names and argument names, plus the
    ambiguous-collision case where two targets share an abbreviation.
    """

    def test_target_name_abbreviation(self, run_tool):
        result = run_tool("dummy_cli.py", "g", "-n=Bob")
        assert result.returncode == 0
        assert result.stdout == "greet:  {'name': 'Bob'}\nHello, Bob!\n"

    def test_argument_name_abbreviation(self, run_tool):
        result = run_tool("dummy_cli.py", "greet", "-n=Abbreviated")
        assert result.returncode == 0
        assert result.stdout == "greet:  {'name': 'Abbreviated'}\nHello, Abbreviated!\n"

    def test_ambiguous_target_abbreviation_matches_neither(self, run_tool):
        # ambiguous_one and another_option both abbreviate to 'ao' -- on purpose.
        result = run_tool("dummy_cli.py", "ao")
        assert result.returncode == 3  # EXIT_AMBIGUOUS_MATCH
        prefix = "Multiple Matches found for args: ['dummy_cli.py', 'ao']\nambiguous_one:  {}\nanother_option:  {}\n"
        assert result.stdout == prefix + DUMMY_CLI_MAN_PAGE

    def test_disambiguating_by_full_name_still_works(self, run_tool):
        # Even though the abbreviation is ambiguous, the full name is not.
        result = run_tool("dummy_cli.py", "ambiguous_one")
        assert result.returncode == 0
        assert result.stdout == "ambiguous_one:  {}\nambiguous_one:one\n"
