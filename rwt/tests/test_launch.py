from rwt import launch


def test_with_path(tmpdir, capfd):
	params = ['-c', 'import sys; print(sys.path)'	]
	launch.with_path(str(tmpdir), params)
	out, err = capfd.readouterr()
	assert str(tmpdir) in out
