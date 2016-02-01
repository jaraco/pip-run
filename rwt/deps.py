from __future__ import print_function

import sys
import contextlib
import subprocess
import tempfile
import shutil


@contextlib.contextmanager
def _update_working_set():
	"""
	Update the master working_set to include these new packages.

	TODO: would be better to use an officially-supported API,
	but no suitable API is apparent.
	"""
	try:
		pkg_resources = sys.modules['pkg_resources']
		pkg_resources._initialize_master_working_set()
	except KeyError:
		# it's unnecessary to re-initialize when it hasn't
		# yet been initialized.
		pass
	yield


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
		with _update_working_set():
			yield target
	finally:
		sys.path.remove(target)
		shutil.rmtree(target)
