#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import setuptools

from typing import List

from xappt.utilities import git_tools

REPOSITORY_PATH = os.path.dirname(os.path.abspath(__file__))
VERSION_PATH = os.path.join(REPOSITORY_PATH, "xappt", "__version__.py")

os.chdir(REPOSITORY_PATH)


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


def long_description() -> str:
    with open("README.md", "r", encoding="utf8") as fh:
        return fh.read()


def get_version() -> str:
    with open(VERSION_PATH, "r") as fp:
        version_contents = fp.read()

    loc = locals()
    exec(version_contents, {}, loc)
    __version__ = loc['__version__']
    assert __version__ is not None

    return __version__


def update_build(new_build: str):
    version = get_version()
    with open(VERSION_PATH, "w") as fp:
        fp.write(f'__version__ = "{version}"\n')
        fp.write(f'__build__ = "{new_build}"\n')


def requirements(variation=None):
    req_file = "requirements"
    if variation is not None:
        req_file = f"requirements-{variation}"
    req_path = os.path.join(os.path.dirname(__file__), f"{req_file}.txt")
    with open(req_path, "rb") as fp:
        for line in fp.readlines():
            line = line.decode('utf-8').strip()
            if len(line) == 0:
                continue
            if line.startswith("#"):
                continue
            yield line


def main():
    if git_tools.is_dirty(REPOSITORY_PATH):
        print("Local repository is not clean")
        while True:
            result = input("Proceed anyway? (y|n): ").lower()
            if result not in ("y", "n"):
                print(f"Invalid response '{result}', please try again.")
                continue
            if result == "n":
                return
            break

    setup_dict = {
        'name': 'xappt',
        'version': get_version(),
        'author': 'Christopher Montesano',
        'author_email': 'cmdev.00+xappt@gmail.com',
        'url': 'https://github.com/cmontesano/xappt',
        'description': 'Extensible Application Toolkit.',
        'long_description': long_description(),
        'long_description_content_type': 'text/markdown',
        'packages': build_package_list('xappt'),
        'include_package_data': True,
        'zip_safe': False,
        'license': 'MIT',
        'platforms': 'any',
        'python_requires': '>=3.7, <4',
        'install_requires': list(requirements()),
        'classifiers': [
            'Topic :: Utilities',
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
        ],
        'entry_points': {
            'console_scripts': ['xappt=xappt.cli:entry_point'],
        },
    }

    commit_id = git_tools.commit_id(REPOSITORY_PATH, short=True)

    update_build(commit_id)
    setuptools.setup(**setup_dict)
    update_build("dev")


if __name__ == '__main__':
    main()
