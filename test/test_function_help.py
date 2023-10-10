from ..CliFunction import Targets


class TestFunctionHelp:

    @staticmethod
    def two():
        """two docs"""
        return "two!"

    @staticmethod
    def some_args(*, arg: str = "hi"):
        """docs"""
        return arg

    @staticmethod
    def special_address(*, address: str = "localhost"):
        """collides with some_args when abbreviated."""
        return address

    def test_basic_help(self):
        t = Targets()
        h = t.function_help(func=self.two)
        expected = 'two -- two docs\n\t'
        assert h == expected

    def test_args_help(self):
        t = Targets()
        h = t.function_help(func=self.some_args)
        expected = "some_args -- docs\n\targ | default:hi | type:<class 'str'>"
        assert h == expected
