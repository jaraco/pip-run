#!/usr/bin/env python

# Project skeleton maintained at https://github.com/jaraco/skeleton

import io

import setuptools

with io.open('README.rst', encoding='utf-8') as readme:
	long_description = readme.read()

name = 'rwt'
description = 'run with this'
nspkg_technique = 'native'
"""
Does this package use "native" namespace packages or
pkg_resources "managed" namespace packages?
"""

params = dict(
	use_scm_version=True,
)
if __name__ == '__main__':
	setuptools.setup(**params)
