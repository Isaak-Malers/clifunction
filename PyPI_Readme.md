# DecoratorCLI
Enables you to build a CLI with python in the most straightforward way with the fewest lines of code:

turn this:
```
from CliFunction import cli_function, cli

@cli_function
def migrate_data_base(*, start_version: int = 0, end_version: int = 3):
    """
    Runs DB migrations.
    """
    print(f"Migrating DB from {start_version} to {end_version}")


if __name__ == "__main__":
    CliFunction.cli()
```

into a CLI with documentation like this:

```
C:\Users\isaak\dev\clifunction>python Example.py
Targets
        migrate_data_base -- Runs DB migrations.
                start_version | default:0 | type:<class 'int'>
                end_version | default:3 | type:<class 'int'>
```

That can execute your functions via the CLI including type coercion
```
C:\Users\isaak\dev\clifunction>python Example.py mdb -sv=1 -ev=2
migrate_data_base:  {'start_version': 1, 'end_version': 2}
Migrating DB from 1 to 2
```