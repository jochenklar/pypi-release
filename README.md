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

options:
  -h, --help            show this help message and exit
  --skip-npm
  --skip-build
  --skip-git-check
  --skip-github-check
  --skip-twine-check
  --skip-twine-test-upload
  --skip-twine-upload
```

Steps
-----

The script runs the following steps in the current directory and stops at the first one that fails. Each step can be skipped with the option given in brackets.

1. Check that `build` and `twine` are installed.
2. Check that `git describe --tags` matches `version`, i.e. that the current commit is tagged with this version (`--skip-git-check`).
3. Check that a GitHub release exists for this version at `https://github.com/<owner>/<repo>/releases/tag/<version>`. The URL is built from `remote.origin.url` (`--skip-github-check`).
4. If a `package.json` exists, run `nvm use && npm ci && npm run build:prod` (`--skip-npm`).
5. Remove `dist` and the `.egg-info` directory, then run `python3 -m build` (`--skip-build`).
6. Check that `dist` contains the tarball `<name>-<version>.tar.gz` and the wheel `<name>-<version>-py3-none-any.whl`, using the normalized name (e.g. `my-package` becomes `my_package`).
7. Run `twine check dist/*` (`--skip-twine-check`).
8. Ask for confirmation, then run `twine upload -r testpypi dist/*` (`--skip-twine-test-upload`).
9. Ask for confirmation, then run `twine upload dist/*` (`--skip-twine-upload`).

Example
-------

```bash
pypi-release rdmo 2.0.0
```
