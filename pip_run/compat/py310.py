"""
Compatibility for Python 3.10 and earlier.
"""

import sys

__all__ = ['tomllib']


if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover
    import tomli as tomllib
