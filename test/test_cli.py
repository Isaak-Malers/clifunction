import json

import pytest

import clifunction
from clifunction import Targets


class TestCli:
    """
    cli() dispatches through the module-level `clifunction.targets` singleton rather than
    taking a Targets instance -- that's the one piece of this library that isn't naturally
    testable by constructing a fresh object per test.  Swap the singleton out for the duration
    of each test instead of asserting against whatever real targets happen to be registered.
    """

    @staticmethod
    def two():
        """docs"""
        return "two!"

    @staticmethod
    def some_args(*, arg: str = "hi"):
        """docs"""
        return arg

    @staticmethod
    def special_address(*, address: str = "localhost"):
        """collides with some_args when abbreviated to 'sa'."""
        return address

    @pytest.fixture(autouse=True)
    def isolated_targets(self, monkeypatch):
        fresh = Targets()
        monkeypatch.setattr(clifunction, "targets", fresh)
        return fresh

    def test_no_args_exits_with_no_args_code(self, isolated_targets):
        isolated_targets.add_target(self.two)
        with pytest.raises(SystemExit) as exc_info:
            clifunction.cli(args=["prog"])
        assert exc_info.value.code == clifunction.EXIT_NO_ARGS

    def test_no_match_exits_with_no_match_code(self, isolated_targets):
        isolated_targets.add_target(self.two)
        with pytest.raises(SystemExit) as exc_info:
            clifunction.cli(args=["prog", "nonexistent"])
        assert exc_info.value.code == clifunction.EXIT_NO_MATCH

    def test_ambiguous_match_exits_with_ambiguous_code(self, isolated_targets):
        isolated_targets.add_target(self.some_args)
        isolated_targets.add_target(self.special_address)
        # 'sa' abbreviates both targets (see test_generate_method_kwargs.py's
        # test_ambiguous_shorthand for the same collision) and neither specifies which one it
        # means, so both remain candidates.
        with pytest.raises(SystemExit) as exc_info:
            clifunction.cli(args=["prog", "sa"])
        assert exc_info.value.code == clifunction.EXIT_AMBIGUOUS_MATCH

    def test_successful_call_does_not_exit(self, isolated_targets):
        isolated_targets.add_target(self.two)
        clifunction.cli(args=["prog", "two"])  # would raise SystemExit if this failed to match

    def test_schema_flag_prints_json_and_does_not_exit(self, isolated_targets, capsys):
        isolated_targets.add_target(self.some_args)
        clifunction.cli(args=["prog", "--schema"])  # would raise SystemExit on the old codepath
        printed = json.loads(capsys.readouterr().out)
        assert printed == isolated_targets.schema()
