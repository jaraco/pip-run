import os
import sys
import contextlib
import subprocess
import tempfile
import shutil
import itertools
import functools

import packaging.requirements

try:
    from importlib import metadata  # type: ignore
except ImportError:
    import importlib_metadata as metadata  # type: ignore


def _installable(args):
    """
    Return True only if the args to pip install
    indicate something to install.

    >>> _installable(['inflect'])
    True
    >>> _installable(['-q'])
    False
    >>> _installable(['-q', 'inflect'])
    True
    >>> _installable(['-rfoo.txt'])
    True
    >>> _installable(['projects/inflect'])
    True
    >>> _installable(['~/projects/inflect'])
    True
    """
    return any(
        not arg.startswith('-')
        or arg.startswith('-r')
        or arg.startswith('--requirement')
        for arg in args
    )


@contextlib.contextmanager
def load(*args):
    target = tempfile.mkdtemp(prefix='pip-run-')
    cmd = (sys.executable, '-m', 'pip', 'install', '-t', target) + args
    env = dict(os.environ, PIP_QUIET="1")
    _installable(args) and subprocess.check_call(cmd, env=env)
    try:
        yield target
    finally:
        shutil.rmtree(target)


@contextlib.contextmanager
def _save_file(filename):
    """
    Capture the state of filename and restore it after the context
    exits.
    """
    # For now, only supports a missing filename.
    if os.path.exists(filename):
        tmpl = "Unsupported with extant {filename}"
        raise NotImplementedError(tmpl.format(**locals()))
    try:
        yield
    finally:
        if os.path.exists(filename):
            os.remove(filename)


# from jaraco.context
class suppress(contextlib.suppress, contextlib.ContextDecorator):
    """
    A version of contextlib.suppress with decorator support.

    >>> @suppress(KeyError)
    ... def key_error():
    ...     {}['']
    >>> key_error()
    """


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
