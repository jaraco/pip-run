import textwrap
import os
import subprocess
import sys
import signal
import itertools
import pathlib

from jaraco.context import suppress


def inject_sitecustomize(target: pathlib.Path):
    r"""
    Create a sitecustomize file in the target that will install
    the target as a sitedir.

    >>> tmp_path = getfixture('tmp_path')
    >>> inject_sitecustomize(tmp_path)
    >>> sc = tmp_path / 'sitecustomize.py'
    >>> 'Path' not in sc.read_text(encoding='utf-8')
    True
    """
    hook = textwrap.dedent(
        f"""
        import site
        site.addsitedir({os.fspath(target)!r})
        """
    ).lstrip()
    target.joinpath('sitecustomize.py').write_text(hook, encoding='utf-8')


_unique = dict.fromkeys


def _path_insert(previous, value):
    """
    Given a pathsep-separated env key, insert value.

    >>> orig = os.pathsep.join(['foo', 'bar'])
    >>> addl = _path_insert(orig, 'bing')
    >>> addl.split(os.pathsep)
    ['bing', 'foo', 'bar']
    >>> dupl = _path_insert(orig, 'bar')
    >>> dupl.split(os.pathsep)
    ['bar', 'foo']
    """
    prefix = (value,)
    suffix = filter(None, previous.split(os.pathsep))
    return os.pathsep.join(_unique(itertools.chain(prefix, suffix)))


def _build_env(target, *, orig=os.environ):
    """
    Prepend target to PYTHONPATH and add $target/bin to PATH.

    >>> orig = dict(PYTHONPATH='/orig', PATH='/orig')
    >>> env = _build_env(pathlib.Path('/tmp/pip-run/target'), orig=orig)
    >>> pprint(norm_env_paths(env))
    {'PATH': '/tmp/pip-run/target/bin:/orig',
     'PYTHONPATH': '/tmp/pip-run/target:/orig'}
    """
    overlay = dict(
        PYTHONPATH=_path_insert(orig.get('PYTHONPATH', ''), os.fspath(target)),
        PATH=_path_insert(orig.get('PATH', ''), os.fspath(target / 'bin')),
    )
    return {**orig, **overlay}


def _setup_env(target):
    inject_sitecustomize(target)
    return _build_env(target)


def _ensure_remove_prefix(text: str, prefix: str) -> str:
    start, found, rest = text.partition(prefix)
    if start or not found:
        raise ValueError(f"No prefix {prefix} for {text}")
    return rest


@suppress(KeyError, ValueError)
def _strip_bang(params):
    """
    Strip a literal `!` from the first parameter or return None.
    """
    cmd, rest = params[0], params[1:]
    return [_ensure_remove_prefix(cmd, '!')] + rest


def infer_cmd(params):
    """
    From params, infer command args for a subprocess.

    If the first parameter starts with a ``!``, it's a literal
    subcommand. Otherwise, it's parameters to a Python
    subprocess.

    >>> infer_cmd(['a.py', 'param1'])
    ['...', 'a.py', 'param1']
    >>> infer_cmd(['!an-exe', 'param1'])
    ['an-exe', 'param1']
    """
    return _strip_bang(params) or [sys.executable] + params


def with_path(target: pathlib.Path, cmd):
    """
    Launch cmd with target on the path
    """

    def null_handler(signum, frame):
        pass  # pragma: no cover

    signal.signal(signal.SIGINT, null_handler)
    return subprocess.Popen(cmd, env=_setup_env(target)).wait()
