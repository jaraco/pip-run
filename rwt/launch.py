import os
import subprocess
import sys
import signal
import itertools

filter = getattr(itertools, 'ifilter', filter)
string_types = getattr(__builtins__, 'basestring', str)


# from jaraco.itertools
def _always_iterable(item):
	if item is None:
		item = ()
	if isinstance(item, string_types) or not hasattr(item, '__iter__'):
		item = item,
	return item


def _build_env(target):
	"""
	Prepend target to PYTHONPATH
	"""
	env = dict(os.environ)
	existing = env.get('PYTHONPATH', '')
	items = itertools.chain(
		_always_iterable(target),
		_always_iterable(existing or None),
	)
	env['PYTHONPATH'] = os.pathsep.join(items)
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
