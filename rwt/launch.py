import os
import subprocess
import sys

def with_path(target, params):
	"""
	Launch Python with target on the path and params
	"""
	env = dict(os.environ)
	env['PYTHONPATH'] = target
	subprocess.Popen([sys.executable] + params, env=env).wait()
