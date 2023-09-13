#!/usr/bin/env python3

import inspect
import sys
import re


class BakeException(Exception):
    pass


class DefaultArgumentParser:
    def __init__(self):
        pass

    def nameAndAbbreviations(self, *, pythonName: str) -> [str]:
        # Try to figure out if the python name is camel or snake case, and then figure out if there is a valid
        # abbreviation.
        if '_' in pythonName:
            matches = re.findall(r'_[a-zA-Z0-9]', pythonName)
            abbreviation = pythonName[0] + "".join([char[1] for char in matches])
        else:
            matches = re.findall(r'[A-Z0-9]', pythonName)
            abbreviation = pythonName[0] + "".join([char for char in matches])

        return [pythonName, abbreviation, abbreviation.lower()]

    def generateMethodArgs(self, *, args: [str], function):
        """
            should be passed the args string list from the terminal which will look something like this:
            ['Bake.py', 'two', --arg1=5]
            and a function which may or may not be invoke-able given the information in the args string list.

            if the function cannot be invoked from the given arguments, return None
            if the function CAN be invoked from the given arguments, return a dict formatted such that the method can be invoked with that dict for the arguments.
        """

        invokeName = args[1]
        functionName = function.__name__

        if invokeName not in self.nameAndAbbreviations(pythonName=functionName):
            return None

        # Try to build up the kwarg dict.  If anything tries to double add, bail out.
        names, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, annotations = inspect.getfullargspec(function)

        return {}


class Targets:
    def __init__(self):
        self.headingName = "Targets"
        self.targets = []  # These are not in a subdirectory

        self.recursiveTargets: [Targets] = []

    def hasTarget(self, toAdd):
        for function in self.targets:
            if function.__name__ == toAdd.__name__:
                return True
        return False

    def addTarget(self, toAdd):
        for func in self.targets:
            if func.__name__ == toAdd.__name__:
                raise BakeException(f"duplicate target names: {func.__name__}")

        if toAdd.__doc__ is None:
            raise BakeException(
                "Bake requires doc-strings for target functions (denoted by a triple quoted comment as the first thing in the function body)")

        names, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, annotations = inspect.getfullargspec(toAdd)
        if len(names) != 0 or defaults is not None:
            raise BakeException(
                "Bake requires functions with arguments to use exclusively keyword arguments (denoted by a [*] as the first argument to the function)")
        if varargs is not None:
            raise BakeException("Bake does not support varargs")
        if varkw is not None:
            raise BakeException("Bake does not support varargs")
        self.targets.append(toAdd)

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
    targets.addTarget(targetToAdd)
    return targetToAdd


def bake(args: str = None):
    if args is None:
        args = sys.argv

    if len(args) < 3:
        print(targets.man())
        raise SystemExit(1)

    parser = DefaultArgumentParser()
    potentialMatches = {}
    for f in targets.targets:
        methodArgs = parser.generateMethodArgs(function=f, args=args)
        print("--------")
        print(f.__name__)
        print(methodArgs)
        if methodArgs is not None:
            potentialMatches[f.__name__] = methodArgs

    if len(potentialMatches) == 0:
        print("Unable to find function to call")
        print(targets.man)
        raise SystemExit(1)

    if len(potentialMatches) == 1:
        print("Running Function!")

    if len(potentialMatches) > 1:
        print("Invoke Arguments match multiple functions")
        raise SystemExit(1)
