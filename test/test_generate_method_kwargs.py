from ..CliFunction import DefaultArgumentParser


class TestGenerateMethodKwargs:
    t = DefaultArgumentParser()

    @staticmethod
    def two():
        return "two!"

    @staticmethod
    def some_args(*, arg: str = "hi"):
        return arg

    @staticmethod
    def bool_args(*, arg: bool = False):
        return arg

    @staticmethod
    # pylint: disable=too-many-arguments
    # pylint: disable=unused-argument
    def complex_method(*, arg1: str, arg2: str, arg3: str, arg4: str, arg5: str, arg6: str, arg7: str, arg8: str, arg9: str):
        return "wtf"

    @staticmethod
    # pylint: disable=too-many-arguments
    # pylint: disable=unused-argument
    def types(*, st: str, bo: bool, inn: int, fl: float):
        return "yay types"

    @staticmethod
    # pylint: disable=unused-argument
    def types2(*, retries: int):
        return "moreTests"

    @staticmethod
    # pylint: disable=unused-argument
    def bad_shorthands(*, url: str, unicode: bool):
        """These both have the same abbreviation"""
        return "bad"

    def test_bad_shorthands(self):
        assert self.t.generate_method_kwargs(args=['d.py', 'bad_shorthands', '-u=localhost'], function=self.bad_shorthands) is None

    def test_good_shorthands(self):
        assert self.t.generate_method_kwargs(args=['d.py', 'types2', '-r=5'], function=self.types2) == {'retries': 5}

    def test_type_coercion(self):
        assert self.t.generate_method_kwargs(args=['d.py', 'types', '--st=happy', '--bo=false', '--inn=5', '--fl=4.8'], function=self.types) == {'st': 'happy', 'bo': False, 'inn': 5, 'fl': 4.8}

    def test_failed_type_coercion(self):
        assert self.t.generate_method_kwargs(args=['d.py', 'types2', '--retries=notAnInt'], function=self.types2) is None
        assert self.t.generate_method_kwargs(args=['d.py', 'types2', '--retries=5.4'], function=self.types2) is None
        assert self.t.generate_method_kwargs(args=['d.py', 'types2', '--retries=True'], function=self.types2) is None
        assert self.t.generate_method_kwargs(args=['d.py', 'types2', '--retries=5'], function=self.types2) == {'retries': 5}

    def test_shorthands(self):
        assert self.t.generate_method_kwargs(args=['CliFunction', 'bool_args', '-a'], function=self.bool_args) == {"arg": True}
        assert self.t.generate_method_kwargs(args=['CliFunction', 'some_args', '-a=hello'], function=self.some_args) == {"arg": 'hello'}

    def test_name_doesnt_match(self):
        assert self.t.generate_method_kwargs(args=['CliFunction', "too"], function=self.two) is None

    def test_no_args(self):
        assert self.t.generate_method_kwargs(args=['CliFunction', 'two', '--arg1=5'], function=self.two) is None
        assert self.t.generate_method_kwargs(args=['CliFunction', 'two'], function=self.two) == {}

    def test_basic(self):
        assert self.t.generate_method_kwargs(args=['CliFunction', 'some_args', '--arg=hello'], function=self.some_args) == {"arg": 'hello'}
        assert self.t.generate_method_kwargs(args=['CliFunction', 'some_args'], function=self.some_args) == {}

    def test_boolean(self):
        assert self.t.generate_method_kwargs(args=['CliFunction', 'bool_args', '--arg'], function=self.bool_args) == {"arg": True}
        assert self.t.generate_method_kwargs(args=['CliFunction', 'bool_args'], function=self.bool_args) == {}

    def test_flag_on_non_flag_argument(self):
        """
        For this test we pass an argument in with the shorthand for True and expect it to throw if the argument type isn't bool
        """
        assert self.t.generate_method_kwargs(args=['CliFunction', 'some_args', '--arg'], function=self.some_args) is None

    def test_complex(self):
        assert self.t.generate_method_kwargs(args=[
            'CliFunction',
            'complex_method',
            '--arg1=a',
            '--arg2=b',
            '--arg3=c',
            '--arg4=d',
            '--arg5=e',
            '--arg6=f',
            '--arg7=g',
            '--arg8=h',
            '--arg9=i'],
            function=self.complex_method) == {"arg1": "a", "arg2": "b", "arg3": "c", "arg4": "d", "arg5": "e", "arg6": "f", "arg7": "g", "arg8": "h", "arg9": "i"}
        assert self.t.generate_method_kwargs(args=[
            'CliFunction',
            'complex_method',
            '--arg1=a',
            '--arg2=b'],
            function=self.complex_method) == {"arg1": "a", "arg2": "b"}
