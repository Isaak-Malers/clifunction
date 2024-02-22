from ..CliFunction import Targets


class TestCollectMethodKwargs:

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
        """collides with some_args when abbreviated."""
        return address

    def test_returning_matches(self):
        t = Targets()
        t.add_target(self.two)
        t.add_target(self.some_args)

        result = t.collect_method_kwargs(args=['CliFunction', 'noMatch'])
        assert len(result.keys()) == 0

        result = t.collect_method_kwargs(args=['CliFunction', 'two'])
        assert len(result.keys()) == 1

        result = t.collect_method_kwargs(args=['CliFunction', 'some_args'])
        assert len(result.keys()) == 1

        result = t.collect_method_kwargs(args=['CliFunction', 'some_args', '--arg=notADefault'])
        assert len(result.keys()) == 1
        assert list(result.values())[0].get('arg') == 'notADefault'

    def test_ambiguous_shorthand(self):
        t = Targets()
        t.add_target(self.two)
        t.add_target(self.some_args)
        t.add_target(self.special_address)

        result = t.collect_method_kwargs(args=['CliFunction', 'sa', '-a=ThisIsNotGoodEnough'])
        assert len(result.keys()) == 2

    def test_multiple_matches(self):
        t = Targets()
        t.add_target(self.two)
        t.add_target(self.some_args)
        t.add_target(self.special_address)

        result = t.collect_method_kwargs(args=['CliFunction', 'sa'])
        assert len(result.keys()) == 2

        result = t.collect_method_kwargs(args=['CliFunction', 'sa', '--arg=ThisSpecifies'])
        assert len(result.keys()) == 1

        result = t.collect_method_kwargs(args=['CliFunction', 'sa', '-a=ThisIsNotGoodEnough'])
        assert len(result.keys()) == 2

        result = t.collect_method_kwargs(args=['CliFunction', 'some_args'])
        assert len(result.keys()) == 1

        result = t.collect_method_kwargs(args=['CliFunction', 'some_args', '--address=ThisShouldBeZero'])
        assert len(result.keys()) == 0
