pypi-release
============

A command line script to publish python packages to [PyPI](https://pypi.org), with a lot of checking before.

Setup
-----

```bash
pip install git+https://github.com/jochenklar/pypi-release
```

Usage
-----

```bash
usage: pypi-release [-h] [--skip-npm] [--skip-build] [--skip-git-check] [--skip-github-check]
                    [--skip-twine-check] [--skip-twine-test-upload] [--skip-twine-upload]
                    name version

positional arguments:
  name                  name of the package
  version               version to be published

optional arguments:
  -h, --help            show this help message and exit
  --skip-npm
  --skip-build
  --skip-git-check
  --skip-github-check
  --skip-twine-check
  --skip-twine-test-upload
  --skip-twine-upload
```

Example
-------

```bash
pypi-release rdmo 2.0.0
```
