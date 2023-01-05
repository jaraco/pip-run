import textwrap
import os
import subprocess
import sys
import signal
import itertools
import pathlib


def inject_sitecustomize(target: pathlib.Path):
    r"""
    Create a sitecustomize file in the target that will install
    the target as a sitedir.

    >>> tmp_path = getfixture('tmp_path')
    >>> inject_sitecustomize(tmp_path)
    >>> sc = tmp_path / 'sitecustomize.py'
    >>> 'Path' not in sc.read_text()
    True
    """
    hook = textwrap.dedent(
        f"""
        import site
        site.addsitedir({os.fspath(target)!r})
        """
    ).lstrip()
    target.joinpath('sitecustomize.py').write_text(hook)


def _build_env(target):
    """
    Prepend target to PYTHONPATH
    """
    key = 'PYTHONPATH'
    env = dict(os.environ)
    previous = env.get(key)
    suffix = (previous,) * bool(previous)
    prefix = (os.fspath(target),)
    items = itertools.chain(prefix, suffix)
    env[key] = os.pathsep.join(items)
    return env


def _setup_env(target):
    inject_sitecustomize(target)
    return _build_env(target)


def with_path(target: pathlib.Path, params):
    """
    Launch Python with target on the path and params
    """

    def null_handler(signum, frame):
        pass  # pragma: no cover

    signal.signal(signal.SIGINT, null_handler)
    cmd = [sys.executable] + params
    return subprocess.Popen(cmd, env=_setup_env(target)).wait()
