from __future__ import print_function

import sys
import contextlib
import subprocess
import tempfile
import shutil


@contextlib.contextmanager
def on_sys_path(*args):
	"""
	Install dependencies via args to pip and ensure they have precedence
	on sys.path.
	"""
	target = tempfile.mkdtemp(prefix='rwt-')
	cmdline = subprocess.list2cmdline(args)
	print("Loading requirements using", cmdline)
	cmd = (
		sys.executable,
		'-m', 'pip',
			'install',
			'-q',
			'-t', target,
	) + args
	subprocess.check_call(cmd)
	sys.path.insert(0, target)
	try:
		yield target
	finally:
		sys.path.remove(target)
		shutil.rmtree(target)
