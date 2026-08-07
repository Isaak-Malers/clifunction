# pylint: disable=import-error
"""
Registers a target with no docstring. add_target() should refuse this at decoration time --
the script should never even reach cli(), let alone print a man page.
"""
from CliFunction import cli_function, cli


@cli_function
def no_docs():
    print("should never run")


if __name__ == "__main__":
    cli()
