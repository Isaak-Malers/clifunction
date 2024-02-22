import sys
import pytest


class TestCanary:

    @pytest.mark.skip(reason="This test is a canary for verifying CI works as intended.")
    def test_python_version(self):
        if sys.version.startswith("3.8"):
            assert True is False

    @pytest.mark.skip(reason="This test is a canary for verifying CI works as intended.")
    def test_fail(self):
        assert True is False
