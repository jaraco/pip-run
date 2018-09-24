from __future__ import print_function

import os
import sys
import re
import contextlib
import subprocess
import tempfile
import shutil
import itertools
import functools

try:
	from pip._vendor import pkg_resources
except ImportError:
	import pkg_resources


filterfalse = getattr(itertools, 'filterfalse', None) or itertools.ifilterfalse


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


def _installable(args):
	"""
	Return True only if the args to pip install
	indicate something to install.
	"""
	return any(
		re.match(r'\w+', arg)
		or arg.startswith('-r')
		or arg.startswith('--requirement')
		for arg in args
	)


@contextlib.contextmanager
def load(*args):
	target = tempfile.mkdtemp(prefix='rwt-')
	cmd = (
		sys.executable,
		'-m', 'pip',
		'install',
		'-t', target,
	) + args
	with _patch_prefix():
		_installable(args) and subprocess.check_call(cmd)
	try:
		yield target
	finally:
		shutil.rmtree(target)


@contextlib.contextmanager
def _patch_prefix():
	"""
	To workaround pypa/pip#4106, override the system prefix with
	a user prefix, restoring the original file after.
	"""
	cfg_fn = os.path.expanduser('~/.pydistutils.cfg')
	with _save_file(cfg_fn):
		with open(cfg_fn, 'w') as cfg:
			cfg.write('[install]\nprefix=\n')
		yield


@contextlib.contextmanager
def _save_file(filename):
	"""
	Capture the state of filename and restore it after the context
	exits.
	"""
	# For now, only supports a missing filename.
	if os.path.exists(filename):
		tmpl = "Unsupported with extant {filename}"
		raise NotImplementedError(tmpl.format(**locals()))
	try:
		yield
	finally:
		if os.path.exists(filename):
			os.remove(filename)


@contextlib.contextmanager
def on_sys_path(*args):
	"""
	Install dependencies via args to pip and ensure they have precedence
	on sys.path.
	"""
	with load(*args) as target:
		sys.path.insert(0, target)
		try:
			with _update_working_set():
				yield target
		finally:
			sys.path.remove(target)


def pkg_installed(spec):
	try:
		pkg_resources.require(spec)
	except Exception:
		return False
	return True


not_installed = functools.partial(filterfalse, pkg_installed)
