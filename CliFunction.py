import inspect
import os
import sys
import re


class CliFunctionException(Exception):
    """
    Common exception type for CliFunction.
    This ensures it is obvious when a problem occurs with the CLI wrapper vs the code being called into.
    """


class DefaultArgumentParser:
    """
    The default argument parser.  It is possible to create others (for example one that uses argparse) if so desired.
    """
    def __init__(self):
        pass

    def name_and_abbreviations(self, *, python_name: str) -> [str]:
        """
        Given a string name for a python function or method or argument, returns a list with multiple possible matches.
        Examples:
            python_name='name_and_abbreviations'
            ['name_and_abbreviations', 'naa']

            python_name='myCamelFunc3'
            ['myCamelFunc3', 'mcf3']

            This function is then used in a bunch of places to map what a user might type on the command line
            to what function or argument they are most likely to want to specify in python.
        """
        if '_' in python_name:
            matches = re.findall(r'_[a-zA-Z0-9]', python_name)
            abbreviation = python_name[0] + "".join([char[1] for char in matches])
        else:
            matches = re.findall(r'[A-Z0-9]', python_name)
            # pylint: disable=unnecessary-comprehension
            abbreviation = python_name[0] + "".join([char for char in matches])

        # note:  these don't strictly need to be sorted, but it makes the test cases a lot more consistent/easier to
        # write
        return sorted(list({python_name, abbreviation.lower()}), key=lambda item: -len(item))

    # pylint: disable=too-many-return-statements
    def type_coercer(self, *, arg: str, desired_type: type):
        """
        given a string representation of an argument from the CLI, and a 'desired type' annotation, it will return the type desired or None
        Note that there are only a limited number of types supported.
        """
        if desired_type is str:
            return arg

        if desired_type is bool:
            if arg.lower() in ['true', 't', 'y', 'yes']:
                return True
            if arg.lower() in ['false', 'f', 'n', 'no']:
                return False
            return None

        try:
            if desired_type is int:
                return int(arg)

            if desired_type is float:
                return float(arg)
        # pylint: disable=broad-exception-caught
        except Exception:  # noqa
            return None  # what a vile pythonic thing to do.

        return None

    # pylint: disable=too-many-locals
    def generate_method_kwargs(self, *, args: [str], function) -> dict:
        """
            should be passed the args string list from the terminal which will look something like this:
            ['CliFunction.py', 'two', '--arg1=5']
            and a function which may or may not be invoke-able given the information in the args string list.

            if the function cannot be invoked from the given arguments, return None
            if the function CAN be invoked from the given arguments, return a dict formatted such that the method can be invoked with that dict for the arguments.
        """

        invoke_name = args[1]
        function_name = function.__name__

        if invoke_name not in self.name_and_abbreviations(python_name=function_name):
            return None

        kwargs_to_return = {}

        # Try to build up the kwarg dict.  If anything tries to double add, bail out.
        # pylint: disable=unused-variable
        names, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, annotations = inspect.getfullargspec(function)

        # Check that all args specified have a place to go:
        for arg in args[2:]:
            arg_name = arg.split("=")[0].replace("-", "")
            arg_value = True
            if len(arg.split("=")) == 2:
                arg_value = arg.split("=")[1]

            added = False
            for name in kwonlyargs:
                if arg_name in self.name_and_abbreviations(python_name=name):
                    if name in kwargs_to_return:
                        # TO DO:  See if we can make this give better errors.
                        # The function has an ambiguous naming scheme, this should probably error out?
                        return None

                    # Note:  This means that the user didn't specify a value, so we treated it as a flag.
                    # If this method doesn't allow for a bool on that argument, we cannot match and should return none
                    if arg_value is True:
                        # pylint: disable=unidiomatic-typecheck
                        if type(True) is not annotations[name]:
                            return None
                        kwargs_to_return[name] = arg_value
                    else:  # arg_value is a string
                        # Coerce Type:
                        typed_value = self.type_coercer(arg=arg_value, desired_type=annotations[name])
                        if typed_value is None:
                            return None
                        kwargs_to_return[name] = typed_value
                    added = True
            if added is False:
                return None

        return kwargs_to_return


class Targets:
    """holds functions to be exposed over CLI"""
    def __init__(self):
        self.headingName = os.path.basename(sys.argv[0])
        self.targets = []  # These are not in a subdirectory
        self.parser = DefaultArgumentParser()

        self.recursiveTargets: [Targets] = []

    def printer(self, to_print: str):
        """
            Note:  This function is only here so that this object is easy to mock/patch for unit tests.
        """
        print(to_print)

    def collect_method_kwargs(self, *, args: [str]) -> dict:
        """
        Generates a dict with keys of functions, and values of kwargs that potentially match.
        """
        to_return = {}

        for t in self.targets:
            candidate = self.parser.generate_method_kwargs(args=args, function=t)
            if candidate is not None:
                to_return[t] = candidate
        return to_return

    def execute(self, *, args: [str]) -> bool:
        """Given some args, attempts to execute the function, returns false if it fails to execute a function"""
        run_candidates = self.collect_method_kwargs(args=args)

        # Happy Path:
        if len(run_candidates.keys()) == 1:
            key, value = list(run_candidates.items())[0]
            self.printer(f"{key.__name__}:  {value}")
            key(**value)
            return True

        # Non-Successful Cases:
        if len(run_candidates.keys()) == 0:
            self.printer(f"No Matches found for args: {args}")
            return False
        if len(run_candidates.keys()) > 1:
            self.printer(f"Multiple Matches found for args: {args}")
            for key, value in run_candidates.items():
                self.printer(f"{key.__name__}:  {value}")
            return False
        return False

    def has_target(self, to_add):
        """
        Returns true if the current object already has a function named similarly as 'to_add'
        """
        for function in self.targets:
            if function.__name__ == to_add.__name__:
                return True
        return False

    def add_target(self, to_add):
        """
        Tries to add a target to this object.  Fails out if there is a problem or if the target to add isn't sufficiently annotated.
        """
        for func in self.targets:
            if func.__name__ == to_add.__name__:
                raise CliFunctionException(f"duplicate function names: {func.__name__}")

        if to_add.__doc__ is None:
            raise CliFunctionException(
                "CliFunction requires doc-strings for exposed functions (denoted by a triple quoted comment as the first thing in the function body)")

        # pylint: disable=unused-variable
        names, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, annotations = inspect.getfullargspec(to_add)
        if len(names) != 0 or defaults is not None:
            raise CliFunctionException(
                "CliFunction requires functions with arguments to use exclusively keyword arguments (denoted by a [*] as the first argument to the function)")
        if varargs is not None:
            raise CliFunctionException("CliFunction does not support varargs")
        if varkw is not None:
            raise CliFunctionException("CliFunction does not support varargs")
        self.targets.append(to_add)

    def function_help(self, func, pad: str = "") -> str:
        """
        Given a function, and a "pad" returns the help string for the function, with indentation equal to the padding.
        """
        header = f"{pad}{func.__name__} -- {func.__doc__.strip()}"
        # pylint: disable=unused-variable
        names, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, annotations = inspect.getfullargspec(func)
        if kwonlydefaults is None:
            kwonlydefaults = {}

        args = []
        for name in kwonlyargs:
            arg = f"{name} | default:{kwonlydefaults.get(name, 'N/A')} | type:{annotations.get(name, 'N/A')}"
            args.append(arg)
        args_string = f"\n\t{pad}".join(args)
        return header + f"\n\t{pad}" + args_string

    def man(self, pad: str = ""):
        """
        Returns the manuel for this instance of a Cli Function object.  Padding allows for indenting recursively nested CLI function objects.
        """
        header = f"{pad}{self.headingName}"
        function_docs = []
        for func in self.targets:
            function_docs.append(self.function_help(func=func, pad=pad + "\t"))
        function_docs_string = "\n".join(function_docs)
        return header + "\n" + function_docs_string


targets = Targets()


def cli_function(target_to_add):
    """
    Decorates a function, and at import time registers that function with the CLI tool.
    This allows the cli function to know what functions are available and should be exposed.
    """
    targets.add_target(target_to_add)
    return target_to_add


def cli(args: [str] = None):
    """
    Runs the CLI tool for the current file
    """
    if args is None:
        args = sys.argv

    if len(args) < 2:
        print(targets.man())
        raise SystemExit(1)

    if not targets.execute(args=args):
        print(targets.man())
        raise SystemExit(1)
