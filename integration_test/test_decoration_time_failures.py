import pytest


class TestDecorationTimeFailures:
    """
    All of these fixtures fail while @cli_function is being applied, i.e. at import time --
    before cli() ever runs. The script never gets as far as printing a man page; it crashes
    with an uncaught CliFunctionException, same as any other uncaught exception at import time.
    """

    @pytest.mark.parametrize("fixture,expected_message", [
        ("broken_missing_docstring.py",
         "CliFunction requires doc-strings for exposed functions"),
        ("broken_positional_args.py",
         "CliFunction requires functions with arguments to use exclusively keyword arguments"),
        ("broken_duplicate_names.py",
         "duplicate function names: duplicate"),
        ("broken_varargs.py",
         "CliFunction does not support varargs"),
        ("broken_varkw.py",
         # Same message text as varargs -- add_target() reuses it for both varargs and varkw.
         # This asserts what the library actually says today, not what it arguably should say.
         "CliFunction does not support varargs"),
    ])
    def test_fails_at_import_time_with_a_clear_message(self, run_tool, fixture, expected_message):
        result = run_tool(fixture)
        assert result.returncode != 0
        assert result.stdout == ""
        assert "CliFunctionException" in result.stderr
        assert expected_message in result.stderr
