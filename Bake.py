#!/usr/bin/env python3

import inspect
import sys
import re


class BakeException(Exception):
    pass


class DefaultArgumentParser:
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
            abbreviation = python_name[0] + "".join([char for char in matches])

        # note:  these don't strictly need to be sorted, but it makes the test cases a lot more consistent/easier to
        # write
        return sorted(list({python_name, abbreviation.lower()}), key=lambda item: -len(item))

    def generate_method_kwargs(self, *, args: [str], function) -> dict:
        """
            should be passed the args string list from the terminal which will look something like this:
            ['Bake.py', 'two', '--arg1=5']
            and a function which may or may not be invoke-able given the information in the args string list.

            if the function cannot be invoked from the given arguments, return None
            if the function CAN be invoked from the given arguments, return a dict formatted such that the method can be invoked with that dict for the arguments.
        """

        invoke_name = args[1]
        function_name = function.__name__

        if invoke_name not in self.name_and_abbreviations(python_name=function_name):
            return None

        kwargsToReturn = {}

        # Try to build up the kwarg dict.  If anything tries to double add, bail out.
        names, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, annotations = inspect.getfullargspec(function)

        # Check that all args specified have a place to go:
        for arg in args[2:]:
            argName = arg.split("=")[0].replace("-", "")
            argValue = True
            if len(arg.split("=")) == 2:
                argValue = arg.split("=")[1]

            added = False
            for name in kwonlyargs:
                if argName in self.name_and_abbreviations(python_name=name):
                    if name in kwargsToReturn:
                        # TODO:  See if we can make this give better errors.
                        # The function has an ambiguous naming scheme, this should probably error out?
                        return None
                    # TODO: match types, right now only true and str are working
                    kwargsToReturn[name] = argValue
                    added = True
            if added is False:
                return None

        return kwargsToReturn


class Targets:
    def __init__(self):
        self.headingName = "Targets"
        self.targets = []  # These are not in a subdirectory
        self.parser = DefaultArgumentParser()

        self.recursiveTargets: [Targets] = []

    def get_matches(self, args: [str]) -> [(object, dict)]:
        """given an args string, looks through itself and tries to find matching functions to execute."""
        toReturn = []
        for t in self.targets:
            if '-' in args[1]:
                candidate = self.parser.generate_method_kwargs(args=args, function=t)
                if candidate is not None:
                    toReturn.append((t, candidate))

        # TODO: hunt through the recursive targets here.
        return toReturn

    def has_target(self, to_add):
        for function in self.targets:
            if function.__name__ == to_add.__name__:
                return True
        return False

    def add_target(self, to_add):
        for func in self.targets:
            if func.__name__ == to_add.__name__:
                raise BakeException(f"duplicate target names: {func.__name__}")

        if to_add.__doc__ is None:
            raise BakeException(
                "Bake requires doc-strings for target functions (denoted by a triple quoted comment as the first thing in the function body)")

        names, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, annotations = inspect.getfullargspec(to_add)
        if len(names) != 0 or defaults is not None:
            raise BakeException(
                "Bake requires functions with arguments to use exclusively keyword arguments (denoted by a [*] as the first argument to the function)")
        if varargs is not None:
            raise BakeException("Bake does not support varargs")
        if varkw is not None:
            raise BakeException("Bake does not support varargs")
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


def target(targetToAdd):
    targets.add_target(targetToAdd)
    return targetToAdd


def bake(args: [str] = None):
    if args is None:
        args = sys.argv

    print(args)

    if len(args) < 2:
        print(targets.man())
        raise SystemExit(1)

    print("executing")
    matches = targets.get_matches(args)
    if len(matches) == 0:
        print("no matching functions found")
        raise SystemExit(1)

    if len(matches) > 1:
        print("ambiguous command, multiple matching functions found")
        raise SystemExit(1)

