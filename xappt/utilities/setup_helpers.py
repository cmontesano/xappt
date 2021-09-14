#!/usr/bin/env python3
import pathlib
import re
import setuptools
import shutil

from typing import Generator, List, Pattern

from xappt.utilities import git_tools


def build_package_list(base_pkg: str, *, exclude: List[str] = None) -> List[str]:
    if exclude is None:
        exclude = []
    packages = [base_pkg]
    for package in setuptools.find_packages(base_pkg):
        pkg_name = f"{base_pkg}.{package}"
        if pkg_name in exclude:
            continue
        packages.append(pkg_name)
    return packages


def get_version(version_path: pathlib.Path) -> str:
    with version_path.open("r") as fp:
        version_contents = fp.read()

    loc = locals()
    exec(version_contents, {}, loc)
    __version__ = loc['__version__']
    assert __version__ is not None

    return __version__


def update_build(version_path: pathlib.Path, new_build: str):
    version = get_version(version_path)
    with version_path.open("w", newline="\n") as fp:
        fp.write(f'__version__ = "{version}"\n')
        fp.write(f'__build__ = "{new_build}"\n')


def requirements(project_path: pathlib.Path, variation=None) -> Generator[str, None, None]:
    req_file = "requirements"
    if variation is not None:
        req_file = f"requirements-{variation}"
    req_path = project_path.joinpath(f"{req_file}.txt")
    with req_path.open("rb") as fp:
        for line in fp.readlines():
            line = line.decode('utf-8').strip()
            if len(line) == 0:
                continue
            if line.startswith("#"):
                continue
            yield line


def ask(prompt: str) -> bool:
    while True:
        result = input(f"{prompt} (y|n): ").lower()
        if result not in ("y", "n"):
            print(f"Invalid response '{result}', please try again.")
            continue
        if result == "n":
            return False
        return True


def cleanup_build_files(project_root: pathlib.Path) -> bool:
    build_folders = "build", "dist", re.compile(r".*\.egg-info")
    to_clean: list[pathlib.Path] = []
    for item in project_root.iterdir():
        if not item.is_dir():
            continue
        for name_match in build_folders:
            if isinstance(name_match, Pattern):
                re_match = name_match.match(item.name)
                if re_match is not None:
                    to_clean.append(item)
                    break
            else:
                if item.name == name_match:
                    to_clean.append(item)
                    break
    if len(to_clean):
        print("WARNING: The following folders will be permanently deleted:\n")
        for path in to_clean:
            print(f"  {path}")
        print("")
        if ask("Are you sure you want to delete these folders?"):
            for path in to_clean:
                shutil.rmtree(path)
        else:
            if not ask("Proceed anyway?"):
                return False
    return True
