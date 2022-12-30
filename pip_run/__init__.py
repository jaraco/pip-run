import sys

from . import deps
from . import commands
from . import launch
from . import scripts


def run(args=None):
    """
    Main entry point for pip-run.
    """
    if args is None:
        args = sys.argv[1:]
    pip_args, py_args = commands.separate(args)
    commands.intercept(pip_args)
    pip_args.extend(scripts.DepsReader.search(py_args))
    with deps.load(*deps.not_installed(pip_args)) as home:
        raise SystemExit(launch.with_path(home, py_args))
