#!/usr/bin/env python3

import inspect
import sys
import re


class DecoratorCliException(Exception):
    pass


class DefaultArgumentParser:
    def __init__(self):
        pass

    def name_and_abbreviations(self, *, python_name: str) -> [str]: # noqa
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
            abbreviation = python_name[0] + "".join([char for char in matches])

        # note:  these don't strictly need to be sorted, but it makes the test cases a lot more consistent/easier to
        # write
        return sorted(list({python_name, abbreviation.lower()}), key=lambda item: -len(item))

    def generate_method_kwargs(self, *, args: [str], function) -> dict:
        """
            should be passed the args string list from the terminal which will look something like this:
            ['DecoratorCLI.py', 'two', '--arg1=5']
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
                        # TODO:  See if we can make this give better errors.
                        # The function has an ambiguous naming scheme, this should probably error out?
                        return None
                    # TODO: match types, right now only true and str are working
                    kwargs_to_return[name] = arg_value
                    added = True
            if added is False:
                return None

        return kwargs_to_return


class Targets:
    def __init__(self):
        self.headingName = "Targets"
        self.targets = []  # These are not in a subdirectory
        self.parser = DefaultArgumentParser()

        self.recursiveTargets: [Targets] = []

    def printer(self, to_print: str):  # noqa
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

    def has_target(self, to_add):
        for function in self.targets:
            if function.__name__ == to_add.__name__:
                return True
        return False

    def add_target(self, to_add):
        for func in self.targets:
            if func.__name__ == to_add.__name__:
                raise DecoratorCliException(f"duplicate target names: {func.__name__}")

        if to_add.__doc__ is None:
            raise DecoratorCliException(
                "Bake requires doc-strings for target functions (denoted by a triple quoted comment as the first thing in the function body)")

        names, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, annotations = inspect.getfullargspec(to_add)
        if len(names) != 0 or defaults is not None:
            raise DecoratorCliException(
                "Bake requires functions with arguments to use exclusively keyword arguments (denoted by a [*] as the first argument to the function)")
        if varargs is not None:
            raise DecoratorCliException("Bake does not support varargs")
        if varkw is not None:
            raise DecoratorCliException("Bake does not support varargs")
        self.targets.append(to_add)

    def man(self, name=None):
        strings = []
        for func in self.targets:
            if name is not None and name != func.__name__:
                continue
            header = f"{func.__name__} -- {func.__doc__}"
            names, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, annotations = inspect.getfullargspec(func)
            if kwonlydefaults is None:
                kwonlydefaults = {}

            if len(kwonlyargs) == 0:
                strings.append(header)
                continue

            args = []
            for name in kwonlyargs:
                arg = f"{name} | default:{kwonlydefaults.get(name, 'N/A')} | type:{annotations.get(name, 'N/A')}"
                args.append(arg)
            strings.append(header + "\n\t\t" + "\n\t\t".join(args))

        return self.headingName + "-----------------------------" + "\n\t" + "\n\t".join(strings)


targets = Targets()


def target(target_to_add):
    targets.add_target(target_to_add)
    return target_to_add


def cli(args: [str] = None):
    if args is None:
        args = sys.argv

    if not targets.execute(args=args):
        print(targets.man())
        raise SystemExit(1)
