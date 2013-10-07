#!/usr/bin/env python

from setuptools import setup, find_packages
from wake_assets import __version__

setup(
    name         = 'wake_assets',
    version      = __version__,
    description  = 'Python HTML helper for assets managed by wake',
    author       = 'James Coglan',
    author_email = 'jcoglan@gmail.com',
    url          = 'http://github.com/jcoglan/wake-assets-python',
    packages     = find_packages(),
)

