from __future__ import annotations

import inspect
import os
import sys

from .exceptions import CliFunctionException
from .parsing import DefaultArgumentParser


class Targets:
    """holds functions to be exposed over CLI"""
    def __init__(self):
        self.headingName = os.path.basename(sys.argv[0])
        self.targets = []
        self.parser = DefaultArgumentParser()

    def printer(self, to_print: str):
        """
            Note:  This function is only here so that this object is easy to mock/patch for unit tests.
        """
        print(to_print)

    def collect_method_kwargs(self, *, args: list[str]) -> dict:
        """
        Generates a dict with keys of functions, and values of kwargs that potentially match.
        """
        to_return = {}

        for t in self.targets:
            candidate = self.parser.generate_method_kwargs(args=args, function=t)
            if candidate is not None:
                to_return[t] = candidate
        return to_return

    def execute(self, *, args: list[str]) -> bool:
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
