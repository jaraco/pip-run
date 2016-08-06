import os
import subprocess
import sys


def with_path(target, params):
	"""
	Launch Python with target on the path and params
	"""
	env = dict(os.environ)
	env['PYTHONPATH'] = target
	try:
		subprocess.Popen([sys.executable] + params, env=env).wait()
	except KeyboardInterrupt:
		pass


def with_path_overlay(target, params):
	"""
	Overlay Python with target on the path and params
	"""
	env = dict(os.environ)
	env['PYTHONPATH'] = target
	os.execve(sys.executable, [sys.executable] + params, env)
