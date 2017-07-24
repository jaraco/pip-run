import sys

from . import deps
from . import commands
from . import launch
from . import scripts


def run(args=None):
	if args is None:
		args = sys.argv[1:]
	pip_args, params = commands.parse_script_args(args)
	commands.intercept(pip_args)
	reqs = scripts.DepsReader.search(params)
	reqs.index_url and pip_args.extend(['--index-url', reqs.index_url])
	pip_args.extend(reqs)
	with deps.load(*deps.not_installed(pip_args)) as home:
		raise SystemExit(launch.with_path(home, params))
