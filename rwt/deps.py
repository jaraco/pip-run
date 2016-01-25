from __future__ import print_function

import os
import sys
import contextlib
import subprocess
import tempfile
import shutil


@contextlib.contextmanager
def on_sys_path(reqs_file):
	"""
	Install the dependencies in reqs_file and ensure they have precedence
	on sys.path.
	"""
	root = os.path.expanduser('~/.rwt')
	os.path.exists(root) or os.mkdir(root)
	target = tempfile.mkdtemp(dir=root)
	print("Loading requirements from", reqs_file)
	cmd = [
		sys.executable,
		'-m', 'pip',
			'install',
			'-q',
			'-r', reqs_file,
			'-t', target,
	]
	subprocess.check_call(cmd)
	sys.path.insert(0, target)
	try:
		yield target
	finally:
		sys.path.remove(target)
		shutil.rmtree(target)
