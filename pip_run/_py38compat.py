import sys
import platform

subprocess_path = (
    str if sys.version_info < (3, 9) and platform.system() == 'Windows' else lambda x: x
)
