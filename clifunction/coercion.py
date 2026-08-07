# pylint: disable=too-many-return-statements
def type_coercer(*, arg: str, desired_type: type):
    """
    given a string representation of an argument from the CLI, and a 'desired type' annotation, it will return the type desired or None
    Note that there are only a limited number of types supported.
    """
    if desired_type is str:
        return arg

    if desired_type is bool:
        if arg.lower() in ['true', 't', 'y', 'yes']:
            return True
        if arg.lower() in ['false', 'f', 'n', 'no']:
            return False
        return None

    try:
        if desired_type is int:
            return int(arg)

        if desired_type is float:
            return float(arg)
    # pylint: disable=broad-exception-caught
    except Exception:  # noqa
        return None  # what a vile pythonic thing to do.

    return None
