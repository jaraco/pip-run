import os
import sys
import contextlib
import subprocess
import itertools
import functools
import argparse
import pathlib
import types
import importlib

import packaging.requirements
from jaraco.context import suppress

from ._py37compat import metadata
from ._py38compat import subprocess_path as sp


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


def mode():
    mode = os.environ.get('PIP_RUN_MODE', 'ephemeral')
    return importlib.import_module(f'.mode.{mode}', package=__package__)


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
    with mode().context(args) as target:
        cmd = (sys.executable, '-m', 'pip', 'install', '-t', sp(target)) + args
        env = dict(os.environ, PIP_QUIET="1")
        if Install.parse(args) and empty(target):
            subprocess.check_call(cmd, env=env)
        yield target


def with_prereleases(spec):
    """
    Allow prereleases to satisfy the spec.
    """
    spec.prereleases = True
    return spec


@suppress(
    packaging.requirements.InvalidRequirement,
    metadata.PackageNotFoundError,  # type: ignore
)
def pkg_installed(spec):
    req = packaging.requirements.Requirement(spec)
    return metadata.version(req.name) in with_prereleases(req.specifier)


not_installed = functools.partial(itertools.filterfalse, pkg_installed)
