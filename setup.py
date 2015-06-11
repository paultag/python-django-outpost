#!/usr/bin/env python

from outpost import __appname__, __version__
from setuptools import setup

long_description = ""

setup(
    name=__appname__,
    version=__version__,
    packages=['outpost',],

    author="Paul Tagliamonte",
    author_email="tag@pault.ag",

    long_description=long_description,
    description='such outpost',
    license="GPLv3",
    url="https://pault.ag/",

    entry_points={},

    platforms=['any']
)
