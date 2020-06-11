#!/usr/bin/env python3

import os
import re
import sys

from setuptools import setup, find_packages
from setuptools.command.install import install


ROOT = os.path.dirname(__file__)
VERSION_RE = re.compile(r"""__version__ = ['"]([0-9.]+)['"]""")


requires = ["boto3", "ipaddress", "diagrams>=0.13", "jinja2"]


def get_version():
    init = open(os.path.join(ROOT, "clouddiscovery", "__init__.py")).read()
    return VERSION_RE.search(init).group(1)


class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches our version"""

    description = "verify that the git tag matches our version"

    def run(self):
        tag = os.getenv("CIRCLE_TAG")

        if tag != get_version():
            info = "Git tag: {0} does not match the version of this app: {1}".format(
                tag, get_version()
            )
            sys.exit(info)


setup(
    name="clouddiscovery",
    version=get_version(),
    description="The tool to help you discover resources in the cloud environment",
    long_description="Long description",
    author="Cloud Architects",
    url="https://github.com/Cloud-Architects/cloud-discovery",
    package_data={
        "": [
            "locales/en_US/LC_MESSAGES/messages.mo",
            "locales/pt_BR/LC_MESSAGES/messages.mo",
        ]
    },
    packages=find_packages(exclude=["tests*"]),
    install_requires=requires,
    python_requires=">=3.6",
    scripts=["bin/clouddiscovery", "bin/clouddiscovery.cmd"],
    license="Apache License 2.0",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "Natural Language :: English",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    cmdclass={"verify": VerifyVersionCommand},
)
