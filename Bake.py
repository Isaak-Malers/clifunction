import inspect

class BakeException(Exception):
    pass


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
                raise BakeException(f"duplicate target names: {function.__name__}")

        if toAdd.__doc__ is None:
            raise BakeException("Bake requires doc-strings for target functions (denoted by a triple quoted comment as the first thing in the function body)")

        names, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, annotations = inspect.getfullargspec(toAdd)
        if len(names) != 0 or defaults is not None:
            raise BakeException("Bake requires functions with arguments to use exclusively keyword arguments (denoted by a [*] as the first argument to the function)")
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


@target
def one():
    """doc string for one"""
    print("one")


@target
def two(*, arg1: int=5, arg2):
    """doc string for two"""
    print("two")


print(targets.man())
print(targets.man(two.__name__))
