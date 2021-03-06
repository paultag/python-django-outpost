#!/usr/bin/env python

from setuptools import setup, find_packages

long_description = ""

setup(
    name='django-outpost',
    version='0.1',
    packages=find_packages(),

    author="Paul Tagliamonte",
    author_email="tag@pault.ag",

    long_description=long_description,
    description='such outpost',
    license="GPLv3",
    url="https://pault.ag/",

    entry_points={
        'console_scripts': [
            'outpostd = outpost.cli:daemon',
        ]
    },

    platforms=['any']
)
