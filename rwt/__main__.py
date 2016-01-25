import sys

from . import deps
from . import scripts


if __name__ == '__main__':
	with deps.on_sys_path(sys.argv[1]):
		scripts.run(sys.argv[2:])
