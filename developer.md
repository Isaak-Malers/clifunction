# Note:
this information condensed from: https://packaging.python.org/en/latest/tutorials/packaging-projects/

# Building

to build dist.  CD into the root repository directory:
```python -m build```
this will create a "dist" directory with a wheel and a tar.gz file.

# Publishing

To publish (from windows)  Note that this requires an .pypirc file in home directory with credentials
```python -m twine upload dist/*```