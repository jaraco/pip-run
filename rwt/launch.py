import os
import subprocess
import sys
import signal
import itertools


def _build_env(target):
	"""
	Prepend target and .pth references in target to PYTHONPATH
	"""
	env = dict(os.environ)
	suffix = env.get('PYTHONPATH')
	prefix = target,
	items = itertools.chain(
		prefix,
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
