# pylint: disable=import-error
"""
Registers a target that uses **kwargs. clifunction does not support varkw -- add_target() should
refuse this at decoration time.
"""
from clifunction import cli_function, cli


@cli_function
def has_kwargs(**kwargs):
    """Uses **kwargs, which clifunction does not support."""
    print(kwargs)


if __name__ == "__main__":
    cli()
