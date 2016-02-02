import sys

from . import deps
from . import commands
from . import launch


if __name__ == '__main__':
	pip_args, params = commands.parse_script_args(sys.argv[1:])
	with deps.load(*pip_args) as home:
		launch.with_path(home, params)
