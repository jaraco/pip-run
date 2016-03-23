import sys

from . import deps
from . import commands
from . import launch
from . import scripts


if __name__ == '__main__':
	pip_args, params = commands.parse_script_args(sys.argv[1:])
	if params:
		pip_args.extend(scripts.DepsReader.try_read(params[0]))
	with deps.load(*pip_args) as home:
		launch.with_path(home, params)
