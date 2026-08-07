class CliFunctionException(Exception):
    """
    Common exception type for CliFunction.
    This ensures it is obvious when a problem occurs with the CLI wrapper vs the code being called into.
    """
