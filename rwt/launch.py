import os
import subprocess
import sys
import signal
import glob
import itertools


class PathReader:
	@staticmethod
	def _read_file(filename):
		root = os.path.dirname(filename)
		return (
			os.path.join(root, path.rstrip())
			for path in open(filename)
			if path.strip()
			and not path.startswith('#')
			and not path.startswith('import ')
		)

	@classmethod
	def _read(cls, target):
		"""
		As .pth files aren't honored except in site dirs,
		read the paths indicated by them.
		"""
		pth_files = glob.glob(os.path.join(target, '*.pth'))
		file_items = map(cls._read_file, pth_files)
		return itertools.chain.from_iterable(file_items)


def _build_env(target):
	"""
	Prepend target and .pth references in target to PYTHONPATH
	"""
	env = dict(os.environ)
	suffix = env.get('PYTHONPATH')
	prefix = target,
	items = itertools.chain(
		prefix,
		PathReader._read(target),
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
