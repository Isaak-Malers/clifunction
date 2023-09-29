from Bake import target, bake


@target
def deploy(*, Build: bool = True, Test: bool = True):
    """
    Example of how you might set up a deployment script
    """
    if Build:
        build()
    if Test:
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
    bake(args=['Example.py', 'deploy', '-T'])
