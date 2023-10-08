from Bake import target, bake


@target
def deploy(*, build_first: bool = True, test_first: bool = True):
    """
    Example of how you might set up a deployment script
    """
    if build_first:
        build()
    if test_first:
        test()
    print("Deploying Code!")


@target
def build():
    """
    Example of how you might set up a build script
    """
    print("Building Code!")


@target
def test():
    """
    example of how you might set up a test script
    """
    print("Running Tests!")


@target
def migrate_db(*, start_version: int = 0, end_version: int = 3):
    """
    example of how you might set up a database migration script
    """


if __name__ == "__main__":
    bake()
