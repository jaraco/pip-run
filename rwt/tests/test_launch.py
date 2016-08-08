import sys
import subprocess
import textwrap
import os

import pytest

from rwt import launch


def test_with_path(tmpdir, capfd):
	params = ['-c', 'import sys; print(sys.path)']
	launch.with_path(str(tmpdir), params)
	out, err = capfd.readouterr()
	assert str(tmpdir) in out


@pytest.mark.xfail(reason="cleanup can't occur with execv; #4")
def test_with_path_overlay(tmpdir, capfd):
	params = ['-c', 'import sys; print(sys.path)']
	# launch subprocess so as not to overlay the test process
	script = textwrap.dedent("""
		import rwt.launch
		rwt.launch.with_path_overlay({tmpdir!r}, {params!r})
		print("cleanup")
	""").strip().replace('\n', '; ').format(tmpdir=str(tmpdir), params=params)
	subprocess.Popen([sys.executable, '-c', script]).wait()
	out, err = capfd.readouterr()
	assert str(tmpdir) in out
	assert "cleanup" in out

def test_build_env(monkeypatch):
	monkeypatch.setitem(os.environ, 'PYTHONPATH', 'something')
	env = launch._build_env('else')
	expected = os.pathsep.join(('else', 'something'))
	assert env['PYTHONPATH'] == expected

	monkeypatch.setitem(os.environ, 'PYTHONPATH', '')
	env = launch._build_env('something')
	assert env['PYTHONPATH'] == 'something'

	initial = os.pathsep.join(['something', 'else'])
	monkeypatch.setitem(os.environ, 'PYTHONPATH', initial)
	env = launch._build_env('a')
	expected = os.pathsep.join(['a', 'something', 'else'])
	assert env['PYTHONPATH'] == expected
