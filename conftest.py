import ntpath
import posixpath
import pprint
import textwrap

import jaraco.path
import pytest

import pip_run.mode.persist


collect_ignore = ['examples']


@pytest.fixture
def reqs_files(tmp_path):
    """Create a couple of requirements files."""
    jaraco.path.build(
        {
            'reqs1.txt': textwrap.dedent(
                """
                abc
                def
                """
            ).lstrip(),
            'reqs2.txt': textwrap.dedent(
                """
                uvw
                xyz
                """
            ).lstrip(),
        },
        tmp_path,
    )
    return tmp_path.glob('reqs*.txt')


@pytest.fixture(scope="session")
def monkeypatch_session():
    with pytest.MonkeyPatch.context() as mp:
        yield mp


@pytest.fixture(autouse=True, scope='session')
def alt_cache_dir(monkeypatch_session, tmp_path_factory):
    alt_cache = tmp_path_factory.mktemp('cache')

    class Paths:
        user_cache_path = alt_cache

    monkeypatch_session.setattr(pip_run.mode.persist, 'paths', Paths)


@pytest.fixture(params=['persist', 'ephemeral'])
def run_mode(monkeypatch, request):
    monkeypatch.setenv('PIP_RUN_MODE', request.param)


@pytest.fixture
def doctest_namespace():
    def norm_path(path):
        return path.replace(ntpath.sep, posixpath.sep).replace(
            ntpath.pathsep, posixpath.pathsep
        )

    def norm_env_paths(env):
        return {key: norm_path(value) for key, value in env.items()}

    return dict(locals(), pprint=pprint.pprint)
