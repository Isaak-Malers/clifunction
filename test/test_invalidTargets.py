import pytest

from Bake import Targets


def one():
    """one"""
    pass

def two():
    """two"""
    pass

def noDocstring():
    pass

def camelCase():
    """camel Case"""
    pass

def snake_case():
    """snake_case"""
    pass


class TestInvalidTargets:
    def test_noDocstring(self):
        t = Targets()
        t.addTarget(noDocstring())