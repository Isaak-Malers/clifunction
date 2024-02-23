import pytest

from ..CliFunction import Targets, FunctionCliException


def one():
    """one"""


def two():
    """two"""


def noDocstring():
    pass


# pylint: disable=unused-argument
def noKwargs(myarg, myarg2):
    """But it does have docstrings"""


def camelCase():
    """camel Case"""


def snake_case():
    """snake_case"""


class TestInvalidTargets:
    def test_no_docstring(self):
        t = Targets()
        with pytest.raises(Exception) as e:
            t.add_target(noDocstring)
        assert e.type == FunctionCliException

    def test_no_kwargs_only(self):
        t = Targets()
        with pytest.raises(Exception) as e:
            t.add_target(noKwargs)
        assert e.type == FunctionCliException
