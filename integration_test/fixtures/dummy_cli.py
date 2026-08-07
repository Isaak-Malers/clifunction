# pylint: disable=import-error
"""
A CLI built with clifunction, used only by integration_test/ as a real subprocess target.
Covers every argument type the library supports and one deliberate abbreviation collision
(ambiguous_one / another_option both abbreviate to 'ao') -- not a demo, a fixture.
"""
from clifunction import cli_function, cli


@cli_function
def greet(*, name: str = "world"):
    """
    Greets someone by name.
    """
    print(f"Hello, {name}!")


@cli_function
def add(*, first: int, second: int):
    """
    Adds two required integers together.
    """
    print(first + second)


@cli_function
def scale(*, value: float, factor: float = 2.0):
    """
    Multiplies value by factor.
    """
    print(value * factor)


@cli_function
def toggle(*, enabled: bool = False):
    """
    Prints whether the flag is enabled.
    """
    print(f"enabled={enabled}")


@cli_function
def ambiguous_one(*, note: str = "one"):
    """
    First half of an intentional abbreviation collision (both abbreviate to 'ao').
    """
    print(f"ambiguous_one:{note}")


@cli_function
def another_option(*, note: str = "two"):
    """
    Second half of an intentional abbreviation collision (both abbreviate to 'ao').
    """
    print(f"another_option:{note}")


if __name__ == "__main__":
    cli()
