import textwrap
import os
import subprocess
import sys
import signal
import itertools
import pathlib


def read_lines(path):
    with path.open() as strm:
        yield from strm


class PathReader:
    @staticmethod
    def _read_file(filename):
        root = filename.parent
        return (
            str(root / path.rstrip())
            for path in read_lines(filename)
            if path.strip()
            and not path.startswith('#')
            and not path.startswith('import ')
        )

    @classmethod
    def _read(cls, target):
        """
        As .pth files aren't honored except in site dirs,
        read the paths indicated by them.
        """
        pth_files = target.glob('*.pth')
        file_items = map(cls._read_file, pth_files)
        return itertools.chain.from_iterable(file_items)


def inject_sitecustomize(target):
    """
    Create a sitecustomize file in the target that will install
    the target as a sitedir.
    """
    hook = textwrap.dedent(
        f"""
        import site
        site.addsitedir({target!r})
        """
    ).lstrip()
    target.joinpath('sitecustomize.py').write_text(hook)


def _pythonpath():
    return 'JYTHONPATH' if sys.platform.startswith('java') else 'PYTHONPATH'


def _build_env(target):
    """
    Prepend target and .pth references in target to PYTHONPATH
    """
    key = _pythonpath()
    env = dict(os.environ)
    previous = env.get(key)
    suffix = (previous,) * bool(previous)
    prefix = (os.fspath(target),)
    items = itertools.chain(prefix, PathReader._read(target), suffix)
    joined = os.pathsep.join(items)
    env[key] = os.fspath(joined)
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


def with_path_overlay(target, params):  # pragma: no cover
    """
    Overlay Python with target on the path and params
    """
    cmd = [sys.executable] + params
    os.execve(sys.executable, cmd, _setup_env(target))
