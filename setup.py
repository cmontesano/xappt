#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import setuptools

from typing import List


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


def fetch_version() -> str:
    version_path = os.path.join(os.path.dirname(__file__), "xappt", "__version__.py")

    loc = locals()
    with open(version_path, "r", encoding="utf8") as fp:
        for line in fp:
            if line.startswith("__version__"):
                exec(line.strip(), {}, loc)

    __version__ = loc['__version__']

    assert __version__ is not None
    return __version__


def long_description():
    with open("README.md", "r", encoding="utf8") as fh:
        return fh.read()


if __name__ == '__main__':
    setup_dict = {
        'name': 'xappt',
        'version': fetch_version(),
        'author': 'Christopher Montesano',
        'author_email': 'cmdev.00+xappt@gmail.com',
        'url': 'https://github.com/cmontesano/xappt.git',
        'description': 'Extensible Application Toolkit.',
        'long_description': long_description(),
        'long_description_content_type': 'text/markdown',
        'packages': build_package_list('xappt'),
        'include_package_data': True,
        'zip_safe': False,
        'license': 'MIT',
        'platforms': 'any',
        'python_requires': '>=3.7, <4',
        'install_requires': [],
        'classifiers': [
            # 3 - Alpha, 4 - Beta, 5 - Production/Stable
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
    }

    setuptools.setup(**setup_dict)
