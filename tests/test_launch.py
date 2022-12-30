import sys
import subprocess
import textwrap
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


@pytest.mark.xfail(reason="cleanup can't occur with execv; #4")
def test_with_path_overlay(tmp_path, capfd):
    params = ['-c', 'import sys; sys.stdout.write("\\n".join(sys.path))']
    # launch subprocess so as not to overlay the test process
    script = (
        textwrap.dedent(
            """
            import pip_run.launch, pathlib
            pip_run.launch.with_path_overlay(pathlib.Path({temp_dir!r}), {params!r})
            print("cleanup")
            """
        )
        .strip()
        .replace('\n', '; ')
        .format(temp_dir=str(tmp_path), params=params)
    )
    subprocess.check_call([sys.executable, '-c', script])
    out, err = capfd.readouterr()
    assert str(tmp_path) in out.split(os.linesep)
    assert "cleanup" in out


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


def test_build_env_includes_pth_files(tmp_path, clean_pythonpath):
    """
    If during _build_env, there are .pth files in the target directory,
    they should be processed to include any paths indicated there.
    See #6 for rationale.
    """
    (tmp_path / 'foo.pth').write_text('pkg-1.0', encoding='utf-8')
    env = launch._build_env(tmp_path)
    expected = os.pathsep.join([str(tmp_path), str(tmp_path / 'pkg-1.0')])
    assert env['PYTHONPATH'] == expected
