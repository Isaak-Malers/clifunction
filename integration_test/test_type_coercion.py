import pytest

from expected import DUMMY_CLI_MAN_PAGE


class TestTypeCoercion:
    """
    str/bool/int/float coercion, both success and failure. A coercion failure is not a distinct
    error path -- it just makes that candidate fail to match, so the process behaves exactly
    like "no matches found."
    """

    def test_int_success(self, run_tool):
        result = run_tool("dummy_cli.py", "add", "--first=2", "--second=3")
        assert result.returncode == 0
        assert "5" in result.stdout.splitlines()

    def test_int_failure_is_a_no_match(self, run_tool):
        result = run_tool("dummy_cli.py", "add", "--first=notanumber", "--second=1")
        assert result.returncode == 2  # EXIT_NO_MATCH
        prefix = "No Matches found for args: ['dummy_cli.py', 'add', '--first=notanumber', '--second=1']\n"
        assert result.stdout == prefix + DUMMY_CLI_MAN_PAGE

    def test_float_success(self, run_tool):
        result = run_tool("dummy_cli.py", "scale", "--value=3.5", "--factor=2.0")
        assert result.returncode == 0
        assert "7.0" in result.stdout.splitlines()

    def test_float_failure_is_a_no_match(self, run_tool):
        result = run_tool("dummy_cli.py", "scale", "--value=notafloat")
        assert result.returncode == 2  # EXIT_NO_MATCH
        assert "No Matches found" in result.stdout

    @pytest.mark.parametrize("value", ["true", "True", "TRUE", "t", "y", "yes"])
    def test_bool_truthy_values(self, run_tool, value):
        result = run_tool("dummy_cli.py", "toggle", f"--enabled={value}")
        assert result.returncode == 0
        assert "enabled=True" in result.stdout.splitlines()

    @pytest.mark.parametrize("value", ["false", "False", "FALSE", "f", "n", "no"])
    def test_bool_falsy_values(self, run_tool, value):
        result = run_tool("dummy_cli.py", "toggle", f"--enabled={value}")
        assert result.returncode == 0
        assert "enabled=False" in result.stdout.splitlines()

    def test_bool_bare_flag_means_true(self, run_tool):
        result = run_tool("dummy_cli.py", "toggle", "--enabled")
        assert result.returncode == 0
        assert "enabled=True" in result.stdout.splitlines()

    def test_bool_omitted_uses_default(self, run_tool):
        result = run_tool("dummy_cli.py", "toggle")
        assert result.returncode == 0
        assert "enabled=False" in result.stdout.splitlines()

    def test_bool_garbage_value_is_a_no_match(self, run_tool):
        result = run_tool("dummy_cli.py", "toggle", "--enabled=maybe")
        assert result.returncode == 2  # EXIT_NO_MATCH
        assert "No Matches found" in result.stdout

    def test_bare_flag_on_non_bool_argument_is_a_no_match(self, run_tool):
        # `--name` with no value is only valid shorthand for True on a bool-typed argument.
        result = run_tool("dummy_cli.py", "greet", "--name")
        assert result.returncode == 2  # EXIT_NO_MATCH
        assert "No Matches found" in result.stdout
