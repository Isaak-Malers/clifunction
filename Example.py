import DecoratorCLI
from DecoratorCLI import target


@target
def deploy(*, build_first: bool = True, test_first: bool = True):
    """
    builds*, tests*, and then deploys the code!
    """
    if build_first:
        build()
    if test_first:
        test()
    print("Deploying Code!")


@target
def build():
    """
    Python is Interpreted!
    """
    print("Building Code!")


@target
def test():
    """
    Execs out to PyTest
    """
    print("Running Tests!")


@target
def migrate_db(*, start_version: int = 0, end_version: int = 3):
    """
    Runs DB migrations.
    """
    print(f"Migrating DB from {start_version} to {end_version}")


if __name__ == "__main__":
    DecoratorCLI.cli()
