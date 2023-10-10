# Note:
this information condensed from: https://packaging.python.org/en/latest/tutorials/packaging-projects/

# Building

to build dist.  CD into the root repository directory:
```python -m build```
this will create a "dist" directory with a wheel and a tar.gz file.

# Publishing

To publish (from windows)  Note you must paste an access token for PyPi here:
```python -m twine upload -u __token__ -p [PUT PIPY TOKEN HERE] dist/*```