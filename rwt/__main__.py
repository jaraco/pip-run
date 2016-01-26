import sys

from . import deps
from . import scripts


if __name__ == '__main__':
	reqs_file = sys.argv[1]
	with deps.on_sys_path('-r', reqs_file):
		scripts.run(sys.argv[2:])
