# clifunction

### Introduction

clifunction makes building and maintaining command line utilities easier than ever by using the annotations included in modern python versions, Here is a quick look:

### Installation

```bash
pip install clifunction
# or
uv add clifunction
```

How your code looks:
```python
@cli_function
def migrate_data_base(*, start_version: int = 0, end_version: int = 3):
    """
    Runs DB migrations.
    """
    print(f"Migrating DB from {start_version} to {end_version}")
```
How you invoke that function:
```commandline
maintainer@laptop:/mnt/c/Users/maintainer/dev/clifunction$ python3 Example.py migrate_data_base
migrate_data_base:  {}
Migrating DB from 0 to 3
```


### Getting Started

1. Fully annotate a python function you want to call externally, and add the cli_function decorator:

```python
@cli_function
def migrate_data_base(*, start_version: int = 0, end_version: int = 3):
    """
    Runs DB migrations.
    """
    print(f"Migrating DB from {start_version} to {end_version}")
```

2. Call your function from the command line:
```commandline
maintainer@laptop:/mnt/c/Users/maintainer/dev/clifunction$ python3 Example.py migrate_data_base
migrate_data_base:  {}
Migrating DB from 0 to 3
```

3. Call your functions by auto-generated alias's, and handle Pythons built-in types:
```commandline
maintainer@laptop:/mnt/c/Users/maintainer/dev/clifunction$ python3 Example.py mdb -sv=4 --end_version=5
migrate_data_base:  {'start_version': 4, 'end_version': 5}
Migrating DB from 4 to 5
```

4. Documentation, Error handling, and Man pages are all automatically generated:

```commandline
maintainer@laptop:/mnt/c/Users/maintainer/dev/clifunction$ python3 Example.py
Example.py
        deploy -- builds*, tests*, and then deploys the project
                build_first | default:True | type:<class 'bool'>
                test_first | default:True | type:<class 'bool'>
                
        build -- Bundles python project for distribution

        test -- Execs out to PyTest to run the test suite

        migrate_data_base -- Runs DB migrations
                start_version | default:0 | type:<class 'int'>
                end_version | default:3 | type:<class 'int'>
```

5. Every CLI also exposes its full contract as JSON via `--schema`, for scripts and agents that
   need to enumerate targets/arguments/types without parsing the man page:

```commandline
maintainer@laptop:/mnt/c/Users/maintainer/dev/clifunction$ python3 Example.py --schema
[
  {
    "name": "migrate_data_base",
    "abbreviations": ["migrate_data_base", "mdb"],
    "docstring": "Runs DB migrations.",
    "args": [
      {"name": "start_version", "abbreviations": ["start_version", "sv"], "type": "int", "default": 0, "required": false},
      {"name": "end_version", "abbreviations": ["end_version", "ev"], "type": "int", "default": 3, "required": false}
    ]
  }
]
```