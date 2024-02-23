from ..CliFunction import Targets


class TestExecute:
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

    def test_matching_and_running(self):
        t = Targets()
        t.add_target(self.two)
        ran = t.execute(args=['CliFunction', 'two'])
        assert ran is True

    def test_no_match(self):
        t = Targets()
        t.add_target(self.two)
        ran = t.execute(args=['CliFunction', 'noMatch'])
        assert ran is False

    def test_multiple_matches(self):
        t = Targets()
        t.add_target(self.two)
        t.add_target(self.some_args)
        t.add_target(self.special_address)
        ran = t.execute(args=['CliFunction', 'sa'])
        assert ran is False
