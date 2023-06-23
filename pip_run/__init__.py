import sys

from . import deps
from . import commands
from . import launch
from . import scripts


def run(args=sys.argv[1:]):
    """
    Main entry point for pip-run.
    """
    pip_args, run_args = commands.infer_ipython(commands.separate(args))
    commands.intercept(pip_args)
    pip_args.extend(scripts.DepsReader.search(run_args))
    with deps.load(*deps.not_installed(pip_args)) as home:
        raise SystemExit(launch.with_path(home, launch.infer_cmd(run_args)))
