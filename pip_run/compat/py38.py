import platform
import sys

from jaraco.functools import identity

subprocess_path = (
    str if sys.version_info < (3, 9) and platform.system() == 'Windows' else identity
)

if sys.version_info >= (3, 9):
    from importlib.resources import files as files
else:  # pragma: no cover
    from importlib_resources import files as files
