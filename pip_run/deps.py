import argparse
import contextlib
import importlib
import os
import pathlib
import subprocess
import sys
import types

from jaraco.context import suppress

from .compat.py38 import subprocess_path as sp


class Install(types.SimpleNamespace):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-r',
        '--requirement',
        action='append',
        type=pathlib.Path,
        default=[],
    )
    parser.add_argument('package', nargs='*')

    @classmethod
    def parse(cls, args):
        parsed, unused = cls.parser.parse_known_args(args)
        return cls(**vars(parsed))

    def __bool__(self):
        """
        Return True only if the args to pip install
        indicate something to install.

        >>> bool(Install.parse(['inflect']))
        True
        >>> bool(Install.parse(['-q']))
        False
        >>> bool(Install.parse(['-q', 'inflect']))
        True
        >>> bool(Install.parse(['-rfoo.txt']))
        True
        >>> bool(Install.parse(['projects/inflect']))
        True
        >>> bool(Install.parse(['~/projects/inflect']))
        True
        """
        return bool(self.requirement or self.package)


def retention_strategy():
    strategy = os.environ.get('PIP_RUN_RETENTION_STRATEGY') or 'destroy'
    return importlib.import_module(f'.retention.{strategy}', package=__package__)


@suppress(FileNotFoundError)
def contents(path):
    return list(path.iterdir())


def empty(path):
    """
    >>> target = getfixture('tmp_path')
    >>> empty(target)
    True
    >>> _ = target.joinpath('file.txt').write_text('contents', encoding='utf-8')
    >>> empty(target)
    False

    A non-existent path is considered empty.

    >>> empty(target / 'missing')
    True
    """
    return not bool(contents(path))


@contextlib.contextmanager
def load(*args):
    with retention_strategy().context(args) as target:
        cmd = (sys.executable, '-m', 'pip', 'install', '-t', sp(target)) + args
        env = dict(os.environ, PIP_QUIET="1")
        if Install.parse(args) and empty(target):
            subprocess.check_call(cmd, env=env)
        yield target
