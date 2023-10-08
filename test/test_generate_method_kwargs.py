from ..DecoratorCLI import DefaultArgumentParser


class TestGenerateMethodKwargs:
    t = DefaultArgumentParser()

    @staticmethod
    def two():
        return "two!"

    @staticmethod
    def some_args(*, arg: str = "hi"):
        return arg

    @staticmethod
    def bool_args(*, arg: bool=False):
        return arg

    @staticmethod
    def complex_method(*, arg1: str, arg2: str, arg3: str, arg4: str, arg5: str, arg6: str, arg7: str, arg8: str, arg9: str):
        return "wtf"

    def test_name_doesnt_match(self):
        assert self.t.generate_method_kwargs(args=['DecoratorCLI.py', "too"], function=self.two) is None

    def test_no_args(self):
        assert self.t.generate_method_kwargs(args=['DecoratorCLI.py', 'two', '--arg1=5'], function=self.two) is None
        assert self.t.generate_method_kwargs(args=['DecoratorCLI.py', 'two'], function=self.two) == {}

    def test_basic(self):
        assert self.t.generate_method_kwargs(args=['DecoratorCLI.py', 'some_args', '--arg=hello'], function=self.some_args) == {"arg": 'hello'}
        assert self.t.generate_method_kwargs(args=['DecoratorCLI.py', 'some_args'], function=self.some_args) == {}

    def test_boolean(self):
        assert self.t.generate_method_kwargs(args=['DecoratorCLI.py', 'bool_args', '--arg'], function=self.bool_args) == {"arg": True}
        assert self.t.generate_method_kwargs(args=['DecoratorCLI.py', 'bool_args'], function=self.bool_args) == {}

    def test_complex(self):
        assert self.t.generate_method_kwargs(args=[
            'DecoratorCLI.py',
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
            'DecoratorCLI.py',
            'complex_method',
            '--arg1=a',
            '--arg2=b'],
            function=self.complex_method) == {"arg1": "a", "arg2": "b"}
