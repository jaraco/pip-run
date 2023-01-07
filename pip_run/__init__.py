import os
import sys

from . import deps
from . import commands
from . import launch
from . import scripts


def run(args=sys.argv[1:]):
    """
    Main entry point for pip-run.
    """
    pip_args, py_args = commands.separate(args)
    falsey = ("false", "0")
    if os.environ.get("DEFAULT_TO_IPYTHON_INTERPRETER", "1").lower() not in falsey:
        pip_args, py_args = commands.check_ipython(pip_args, py_args)
    commands.intercept(pip_args)
    pip_args.extend(scripts.DepsReader.search(py_args))
    with deps.load(*deps.not_installed(pip_args)) as home:
        raise SystemExit(launch.with_path(home, py_args))
