import sys
import subprocess
import textwrap

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
