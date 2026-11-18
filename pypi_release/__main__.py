#!/usr/bin/env python3
import argparse
import re
import shutil
import subprocess
import urllib.error
import urllib.request

from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="name of the package")
    parser.add_argument("version", help="version to be published")
    parser.add_argument("--skip-npm", action="store_true", default=False)
    parser.add_argument("--skip-build", action="store_true", default=False)
    parser.add_argument("--skip-git-check", action="store_true", default=False)
    parser.add_argument("--skip-github-check", action="store_true", default=False)
    parser.add_argument("--skip-twine-check", action="store_true", default=False)
    parser.add_argument("--skip-twine-test-upload", action="store_true", default=False)
    parser.add_argument("--skip-twine-upload", action="store_true", default=False)

    args = parser.parse_args()
    name = args.name
    # normalized name used in sdist and wheel filenames (PEP 625, PEP 427)
    package = re.sub(r"[-_.]+", "_", name).lower()
    version = args.version

    try:
        import build  # noqa: F401
    except ImportError:
        parser.error("build is not installed.")

    try:
        import twine  # noqa: F401
    except ImportError:
        parser.error("twine is not installed.")

    # check if we are on the correct git tag
    if not args.skip_git_check:
        git_tag = subprocess.check_output(["git", "describe", "--tags"]).decode().strip()
        if git_tag != version:
            parser.error(f"git tag mismatch: {git_tag} != {version}.")

    # check that there is a github release for this version
    if not args.skip_github_check:
        git_remote_url = subprocess.check_output(["git", "config", "--get", "remote.origin.url"])
        git_remote_url = git_remote_url.decode().strip()
        if git_remote_url.endswith(".git"):
            git_remote_url = git_remote_url[:-4]

        if git_remote_url.startswith("https://github.com"):
            github_url = git_remote_url
        elif git_remote_url.startswith("git@github.com:"):
            github_url = git_remote_url.replace("git@github.com:", "https://github.com/")
        else:
            parser.error("could not determine GitHub url.")

        release_url = f"{github_url}/releases/tag/{version}"

        try:
            urllib.request.urlopen(release_url)
        except urllib.error.URLError:
            parser.error(f"could not access GitHub release at {release_url}.")

    # run "npm run build:prod"
    if not args.skip_npm:
        if Path("package.json").exists():
            subprocess.check_call([
                "/bin/bash", "-i", "-c", "nvm use && npm ci > /dev/null && npm run build:prod > /dev/null"
            ])

    # run "python -m build"
    if not args.skip_build:
        shutil.rmtree("dist", ignore_errors=True)
        # setuptools keeps the case of the name for the egg-info directory
        for egg_info in {f"{name.replace('-', '_')}.egg-info", f"{package}.egg-info"}:
            shutil.rmtree(egg_info, ignore_errors=True)
        subprocess.check_call(["python3", "-m", "build"])

    # check that the version of the tarball is correct
    tarball_path = Path("dist").joinpath(f"{package}-{version}.tar.gz")
    if not tarball_path.exists():
        parser.error(f"version mismatch: {tarball_path} does not exist.")

    # check that the version of the wheel is correct
    wheel_path = Path("dist").joinpath(f"{package}-{version}-py3-none-any.whl")
    if not wheel_path.exists():
        parser.error(f"version mismatch: {wheel_path} does not exist.")

    # run "twine check dist/*"
    if not args.skip_twine_check:
        subprocess.check_call(["twine", "check", "dist/*"])

    # run "twine upload -r testpypi dist/*"
    if not args.skip_twine_test_upload:
        answer = input("Upload to test.pypi.org. Do you want to continue? [y/N]")
        if answer.lower() in ("y", "yes"):
            subprocess.check_call(["twine", "upload", "-r", "testpypi", "dist/*"])
        else:
            print("Skipping.")

    # run "twine upload dist/*"
    if not args.skip_twine_upload:
        answer = input("Upload to pypi.org. Do you want to continue? [y/N]")
        if answer.lower() in ("y", "yes"):
            subprocess.check_call(["twine", "upload", "dist/*"])
        else:
            print("Abort.")
