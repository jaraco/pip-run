import sys
import os


if sys.version_info < (3, 9):
    PathLike_str_type = 'os.PathLike[str]'
else:
    PathLike_str_type = os.PathLike[str]
