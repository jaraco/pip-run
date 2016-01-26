import sys

from . import deps
from . import scripts
from . import commands


if __name__ == '__main__':
	pip_args, script_args = commands.parse_script_args(sys.argv[1:])
	with deps.on_sys_path(*pip_args):
		scripts.run(script_args)
