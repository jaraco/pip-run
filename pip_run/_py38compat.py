import sys
import platform

subprocess_path = (
    str if sys.version_info < (3, 9) and platform.system() == 'Windows' else lambda x: x
)


try:
    from importlib.resources import files  # type: ignore
except ImportError:  # pragma: no cover
    from importlib_resources import files  # type: ignore


files = files
