import os
import pathlib

import pytest

from pip_run import launch


def test_with_path(tmp_path, capfd):
    params = ['-c', 'import sys; sys.stdout.write("\\n".join(sys.path))']
    res = launch.with_path(tmp_path, params)
    assert res == 0
    out, err = capfd.readouterr()
    assert str(tmp_path) in out.split(os.linesep)


def test_with_path_result_code(tmp_path):
    """
    result code should be non-zero on error
    """
    params = ['-c', "raise ValueError()"]
    res = launch.with_path(tmp_path, params)
    assert res > 0


@pytest.fixture
def clean_pythonpath(monkeypatch):
    monkeypatch.delitem(os.environ, 'PYTHONPATH', raising=False)


def test_build_env(clean_pythonpath):
    os.environ['PYTHONPATH'] = 'something'
    env = launch._build_env(pathlib.Path('else'))
    expected = os.pathsep.join(('else', 'something'))
    assert env['PYTHONPATH'] == expected

    os.environ['PYTHONPATH'] = ''
    env = launch._build_env(pathlib.Path('something'))
    assert env['PYTHONPATH'] == 'something'

    initial = os.pathsep.join(['something', 'else'])
    os.environ['PYTHONPATH'] = initial
    env = launch._build_env(pathlib.Path('a'))
    expected = os.pathsep.join(['a', 'something', 'else'])
    assert env['PYTHONPATH'] == expected
