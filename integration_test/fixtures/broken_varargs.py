# pylint: disable=import-error
"""
Registers a target that uses *args. clifunction does not support varargs -- add_target() should
refuse this at decoration time.
"""
from CliFunction import cli_function, cli


@cli_function
def variadic(*args):
    """Uses *args, which clifunction does not support."""
    print(args)


if __name__ == "__main__":
    cli()
