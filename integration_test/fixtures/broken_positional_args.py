# pylint: disable=import-error
"""
Registers a target with a positional argument. clifunction requires exclusively keyword-only
arguments (a bare `*` as the first parameter) -- add_target() should refuse this at decoration
time.
"""
from clifunction import cli_function, cli


@cli_function
def positional(name):
    """Takes a positional argument, which clifunction does not allow."""
    print(name)


if __name__ == "__main__":
    cli()
