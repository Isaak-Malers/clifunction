from ..DecoratorCLI import DefaultArgumentParser, Targets


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

        result = t.collect_method_kwargs(args=['DecoratorCLI.py', 'noMatch'])
        assert len(result.keys()) == 0

        result = t.collect_method_kwargs(args=['DecoratorCLI.py', 'two'])
        assert len(result.keys()) == 1

        result = t.collect_method_kwargs(args=['DecoratorCLI.py', 'some_args'])
        assert len(result.keys()) == 1

        result = t.collect_method_kwargs(args=['DecoratorCLI.py', 'some_args', '--arg=notADefault'])
        assert len(result.keys()) == 1
        assert list(result.values())[0].get('arg') == 'notADefault'

    def test_multiple_matches(self):
        t = Targets()
        t.add_target(self.two)
        t.add_target(self.some_args)
        t.add_target(self.special_address)

        result = t.collect_method_kwargs(args=['DecoratorCLI.py', 'sa'])
        assert len(result.keys()) == 2

        result = t.collect_method_kwargs(args=['DecoratorCLI.py', 'sa', '--arg=ThisSpecifies'])
        assert len(result.keys()) == 1

        result = t.collect_method_kwargs(args=['DecoratorCLI.py', 'sa', '-a=ThisIsNotGoodEnough'])
        assert len(result.keys()) == 2

        result = t.collect_method_kwargs(args=['DecoratorCLI.py', 'some_args'])
        assert len(result.keys()) == 1

        result = t.collect_method_kwargs(args=['DecoratorCLI.py', 'some_args', '--address=ThisShouldBeZero'])
        assert len(result.keys()) == 0