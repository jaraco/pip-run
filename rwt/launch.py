import os
import subprocess
import sys
import signal
import glob
import itertools


def _read_pth_file(filename):
	root = os.path.dirname(filename)
	return (
		os.path.join(root, path.rstrip())
		for path in open(filename)
		if path.strip()
		and not path.startswith('#')
		and not path.startswith('import ')
	)


def _read_pth_files(target):
	"""
	As .pth files aren't honored except in site dirs,
	read the paths indicated by them.
	"""
	pth_files = glob.glob(os.path.join(target, '*.pth'))
	return itertools.chain.from_iterable(map(_read_pth_file, pth_files))


def _build_env(target):
	"""
	Prepend target and .pth references in target to PYTHONPATH
	"""
	env = dict(os.environ)
	suffix = env.get('PYTHONPATH')
	prefix = target,
	items = itertools.chain(
		prefix,
		_read_pth_files(target),
		(suffix,) if suffix else (),
	)
	joined = os.pathsep.join(items)
	env['PYTHONPATH'] = joined
	return env


def with_path(target, params):
	"""
	Launch Python with target on the path and params
	"""
	def null_handler(signum, frame):
		pass

	signal.signal(signal.SIGINT, null_handler)
	cmd = [sys.executable] + params
	subprocess.Popen(cmd, env=_build_env(target)).wait()


def with_path_overlay(target, params):
	"""
	Overlay Python with target on the path and params
	"""
	cmd = [sys.executable] + params
	os.execve(sys.executable, cmd, _build_env(target))
