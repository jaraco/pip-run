import os
import subprocess
import sys
import signal


def with_path(target, params):
	"""
	Launch Python with target on the path and params
	"""
	def null_handler(signum, frame):
		pass

	signal.signal(signal.SIGINT, null_handler)
	env = dict(os.environ)
	env['PYTHONPATH'] = target
	subprocess.Popen([sys.executable] + params, env=env).wait()


def with_path_overlay(target, params):
	"""
	Overlay Python with target on the path and params
	"""
	env = dict(os.environ)
	env['PYTHONPATH'] = target
	os.execve(sys.executable, [sys.executable] + params, env)
