import sys


class TestCanary:

    def test_python_version(self):
        version = sys.version
        if sys.version.startswith("3.8"):
            assert True is False
