import argparse
import contextlib
import importlib
import os
import pathlib
import shutil
import subprocess
import sys
import types

from jaraco.context import suppress


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


installer_schemes = dict(
    uv=types.SimpleNamespace(
        cmd=['uv', 'pip', 'install', '--python', sys.executable],
    ),
    pip=types.SimpleNamespace(
        cmd=['pip', '--python', sys.executable, 'install'],
    ),
)


def installer(target):
    scheme = installer_schemes[next(filter(shutil.which, installer_schemes))]
    return scheme.cmd + [
        '--target',
        target,
    ]


def default_quiet(cmd):
    """
    Parse command to determine the verbosity, then make it one bit quieter.

    Workaround for astral-sh/uv#12397.
    """

    class Subtract(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            namespace.__dict__[self.dest] -= 1

    parser = argparse.ArgumentParser(description="Control verbosity.")

    parser.add_argument(
        '-q',
        '--quiet',
        action=Subtract,
        dest='verbosity',
        default=0,
        nargs=0,
        help='Decrease verbosity (can be specified multiple times).',
    )

    parser.add_argument(
        '-v',
        '--verbose',
        action='count',
        dest='verbosity',
        default=0,
        help='Increase verbosity (can be specified multiple times).',
    )
    parsed, unused = parser.parse_known_args(cmd)

    # set the verbosity to one level lower than indicated and never lower than -1
    verbosity = max(parsed.verbosity - 1, -1)

    return unused + ['--quiet'] * -verbosity + ['--verbose'] * verbosity


@contextlib.contextmanager
def load(*args):
    with retention_strategy().context(args) as target:
        cmd = list(installer(target)) + default_quiet(args)
        if Install.parse(args) and empty(target):
            subprocess.check_call(cmd)
        yield target
