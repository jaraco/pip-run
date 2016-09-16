from __future__ import print_function

import sys
import os
import glob
import io


if sys.version_info < (3,):
	def exec_(_code_, _globs_=None, _locs_=None):
		"""Execute code in a namespace."""
		if _globs_ is None:
			frame = sys._getframe(1)
			_globs_ = frame.f_globals
			if _locs_ is None:
				_locs_ = frame.f_locals
			del frame
		elif _locs_ is None:
			_locs_ = _globs_
		exec("""exec _code_ in _globs_, _locs_""")
else:
	exec_ = getattr(builtins, 'exec')


def run_nspkg_pths():
	"""
	rwt issue #1 describes an issue with pip-installed
	namespace packages. On Pythons that don't have
	PEP-420 implicit namespace packages, namespace
	packages installed not into a site-packages directory
	are not visible. This routine works around that
	limitation by explicitly executing those .pth files.

	This approach is not perfect because
	this function needs to be explicitly executed by each
	Python interpreter after rwt has launched it.
	"""
	if sys.version_info > (3, 3):
		return

	# assume the install root is the first thing on PYTHONPATH
	pp = os.environ.get('PYTHONPATH', '')
	root, sep, _ = pp.partition(os.path.pathsep)

	if not root:
		return

	def exec_pth_line(root, line):
		# hack on hack on hack -
		# The -nspkg.pth file calls sys._getframe(1).f_locals() to
		# reach into it's callers namespace. Just replace it with
		# a simple call to locals() and inject the sitedir there.
		line = line.replace('sys._getframe(1).f_locals', 'locals()')
		exec_(line, None, dict(sitedir=root))

	lines = [
		exec_pth_line(root, line)
		for pth_file in glob.glob(root + '/*-nspkg.pth')
		for line in io.open(pth_file)
		if line.startswith('import ')
	]
