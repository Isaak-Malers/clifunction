# pylint: disable=import-error,function-redefined
"""
Registers two targets with the same name. The second @cli_function application should raise at
decoration time, before the module even finishes importing.
"""
from CliFunction import cli_function, cli


@cli_function
def duplicate():
    """First registration."""
    print("first")


@cli_function
def duplicate():  # noqa: F811
    """Second registration -- same name as above, should fail at decoration time."""
    print("second")


if __name__ == "__main__":
    cli()
