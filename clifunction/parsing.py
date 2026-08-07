from __future__ import annotations

import inspect

from .coercion import type_coercer
from .naming import name_and_abbreviations


class DefaultArgumentParser:
    """
    The default argument parser.  It is possible to create others (for example one that uses argparse) if so desired.
    """
    def __init__(self):
        pass

    def name_and_abbreviations(self, *, python_name: str) -> list[str]:
        """
        Given a string name for a python function or method or argument, returns a list with multiple possible matches.
        See clifunction.naming.name_and_abbreviations for the full docstring/examples.
        """
        return name_and_abbreviations(python_name=python_name)

    def type_coercer(self, *, arg: str, desired_type: type):
        """
        given a string representation of an argument from the CLI, and a 'desired type' annotation, it will return the type desired or None
        Note that there are only a limited number of types supported.
        """
        return type_coercer(arg=arg, desired_type=desired_type)

    # pylint: disable=too-many-locals,too-many-return-statements
    def generate_method_kwargs(self, *, args: list[str], function) -> dict | None:
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
            arg_value: str | bool = True
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
                    if isinstance(arg_value, bool):
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

        # A candidate that's missing a required (no-default) kwonly arg cannot actually be
        # invoked -- it isn't a match, it's a crash waiting to happen.  Treat it the same as
        # any other non-match rather than letting the caller hit the wrapped function's own
        # TypeError.
        required = [name for name in kwonlyargs if not kwonlydefaults or name not in kwonlydefaults]
        if any(name not in kwargs_to_return for name in required):
            return None

        return kwargs_to_return
