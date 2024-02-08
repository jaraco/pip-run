"""
Compatibility for Python 3.10 and earlier.
"""

__all__ = ['tomllib']


try:
    import tomllib  # type: ignore
except ImportError:  # pragma: no cover
    import tomli as tomllib  # type: ignore
