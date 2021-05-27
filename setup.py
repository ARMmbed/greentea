#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""
This module defines the attributes of the
PyPI package for the Greentea CLI and host-tests runner (htrun)
"""

import os
from io import open
from distutils.core import setup
from setuptools import find_packages

DESCRIPTION = "The Greentea CLI and host-tests runner (htrun) is a collection of tools that enable automated testing on Mbed enabled platforms"
OWNER_NAMES = "Mbed team"
OWNER_EMAILS = "support@mbed.com"

repository_dir = os.path.dirname(__file__)


def read(fname):
    """
    Utility function to cat in a file (used for the README)
    @param fname: the name of the file to read,
    relative to the directory containing this file
    @return: The string content of the opened file
    """
    with open(os.path.join(repository_dir, fname), mode="r") as f:
        return f.read()


with open(os.path.join(repository_dir, "requirements.txt")) as fh:
    requirements = fh.readlines()

with open(os.path.join(repository_dir, "test_requirements.txt")) as fh:
    test_requirements = fh.readlines()

python_requires = ">=3.5.*,<4"
setup(
    name="mbed-greentea",
    description=DESCRIPTION,
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author=OWNER_NAMES,
    author_email=OWNER_EMAILS,
    maintainer=OWNER_NAMES,
    maintainer_email=OWNER_EMAILS,
    url="https://github.com/ARMmbed/greentea",
    packages=find_packages("src"),
    package_dir={"": "src"},
    license="Apache-2.0",
    test_suite="test",
    entry_points={
        "console_scripts": ["gt=greentea.greentea_cli:main", "htrun=htrun.htrun:main"],
    },
    classifiers=(
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Embedded Systems",
        "Topic :: Software Development :: Testing",
    ),
    include_package_data=True,
    use_scm_version=True,
    python_requires=python_requires,
    install_requires=requirements,
    tests_require=test_requirements,
)
