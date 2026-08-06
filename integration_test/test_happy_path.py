class TestHappyPath:
    """
    Successful invocations: full names, defaults, echo line, and process exit code 0.
    """

    def test_default_argument_used_when_omitted(self, run_tool):
        result = run_tool("dummy_cli.py", "greet")
        assert result.returncode == 0
        assert result.stdout == "greet:  {}\nHello, world!\n"
        assert result.stderr == ""

    def test_explicit_argument_overrides_default(self, run_tool):
        result = run_tool("dummy_cli.py", "greet", "--name=Isaak")
        assert result.returncode == 0
        assert result.stdout == "greet:  {'name': 'Isaak'}\nHello, Isaak!\n"

    def test_multiple_required_arguments(self, run_tool):
        result = run_tool("dummy_cli.py", "add", "--first=2", "--second=3")
        assert result.returncode == 0
        assert result.stdout == "add:  {'first': 2, 'second': 3}\n5\n"

    def test_mixed_required_and_defaulted_arguments(self, run_tool):
        result = run_tool("dummy_cli.py", "scale", "--value=3.5")
        assert result.returncode == 0
        assert result.stdout == "scale:  {'value': 3.5}\n7.0\n"

    def test_echo_line_reflects_exactly_what_will_be_invoked(self, run_tool):
        # The `name:  {kwargs}` echo line printed before running is the only thing telling a
        # caller what was actually resolved -- assert it matches the real values, not just that
        # something was printed.
        result = run_tool("dummy_cli.py", "add", "--first=10", "--second=32")
        first_line = result.stdout.splitlines()[0]
        assert first_line == "add:  {'first': 10, 'second': 32}"
