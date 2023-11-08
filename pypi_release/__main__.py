#!/usr/bin/env python3
import argparse
import shutil
import subprocess
import urllib.request

from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project", help="name of the project")
    parser.add_argument("version", help="version to be published")
    parser.add_argument("--package", help="name of the package, if it differs from the project name")
    parser.add_argument("--skip-npm", action="store_true", default=False)
    parser.add_argument("--skip-build", action="store_true", default=False)
    parser.add_argument("--skip-git-check", action="store_true", default=False)
    parser.add_argument("--skip-github-check", action="store_true", default=False)
    parser.add_argument("--skip-twine-check", action="store_true", default=False)
    parser.add_argument("--skip-twine-test-upload", action="store_true", default=False)
    parser.add_argument("--skip-twine-upload", action="store_true", default=False)

    args = parser.parse_args()
    project = args.project
    version = args.version
    package = args.package or project

    try:
        import build  # noqa: F401
    except ImportError:
        parser.error("build is not installed.")

    try:
        import twine  # noqa: F401
    except ImportError:
        parser.error("twine is not installed.")

    # run "npm run build:prod"
    if not args.skip_npm:
        if Path("package.json").exists():
            shutil.rmtree("node_modules", ignore_errors=True)
            subprocess.call(["/bin/bash", "-i", "-c", "nvm use; npm install; npm run build:prod"])

    # run "python -m build"
    if not args.skip_build:
        shutil.rmtree("dist", ignore_errors=True)
        shutil.rmtree(f"{project}.egg-info", ignore_errors=True)
        subprocess.check_call(["python3", "-m", "build"])

    # check that the version of the tarball is correct
    tarball_path = Path("dist").joinpath(f"{project}-{version}.tar.gz")
    if not tarball_path.exists():
        parser.error(f"version missmatch: {tarball_path} does not exist.")

    # check that the version of the wheel is correct
    wheel_path = Path("dist").joinpath(f"{package}-{version}-py3-none-any.whl")
    if not wheel_path.exists():
        parser.error(f"version missmatch: {wheel_path} does not exist.")

    # check if we are on the correct git tag
    if not args.skip_git_check:
        git_tag = subprocess.check_output(["git", "describe", "--tags"]).decode().strip()
        if git_tag != version:
            parser.error(f"git tag missmatch: {git_tag} != {version}.")

    # check that there is a github release for this version
    if not args.skip_github_check:
        git_remote_url = subprocess.check_output(["git", "config", "--get", "remote.origin.url"])
        git_remote_url = git_remote_url.decode().strip()

        if git_remote_url.startswith("https://github.com"):
            github_url = git_remote_url
        elif git_remote_url.startswith("git@github.com:"):
            github_url = git_remote_url.replace("git@github.com:", "https://github.com/")
        else:
            parser.error("could not determine GitHub url.")

        release_url = f"{github_url}/releases/tag/{version}"

        try:
            urllib.request.urlopen(release_url)
        except urllib.error.HTTPError:
            parser.error(f"could not access GitHub release at {release_url}.")

    # run "twine check dist/*"
    if not args.skip_twine_check:
        subprocess.check_call(["twine", "check", "dist/*"])

    # run "twine upload -r testpypi dist/*"
    if not args.skip_twine_test_upload:
        if input("Upload to test.pypi.org. Do you want to continue? [y/N]").lower() in [
            "y",
            "yes",
            "Y",
            "Yes",
        ]:
            subprocess.check_call(["twine", "upload", "-r", "testpypi", "dist/*"])
        else:
            print("Skipping.")

    # run "twine upload dist/*"
    if not args.skip_twine_upload:
        if input("Upload to pypi.org. Do you want to continue? [y/N]").lower() in [
            "y",
            "yes",
            "Y",
            "Yes",
        ]:
            subprocess.check_call(["twine", "upload", "dist/*"])
        else:
            print("Abort.")
