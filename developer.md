# Contributing:

This project uses trunk based development, but with an understanding that open source moves a little slower.  Please following the following steps to contribute.

Steps to Contribute:
1. Create, or find an issue.  All branches must be tied to a github issue.
2. Create a branch for your issue.  It should be named after the issue number and with an optional description
3. Make and test feature/fix/change on the branch
4. Add Pull request for the branch, ensuring issue is linked so that reviewers have context for the changeset.

## Note:
this information condensed from: https://packaging.python.org/en/latest/tutorials/packaging-projects/

## Building

to build dist.  CD into the root repository directory:
```python -m build```
this will create a "dist" directory with a wheel and a tar.gz file.

## Publishing

To publish (from windows)  Note you must paste an access token for PyPi here:
```python -m twine upload -u __token__ -p [PUT PIPY TOKEN HERE] dist/*```