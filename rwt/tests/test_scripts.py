from __future__ import unicode_literals

import textwrap
import sys
import subprocess

from rwt import scripts


def test_pkg_imported(tmpdir):
	"""
	Create a script that loads cython and ensure it runs.
	"""
	body = textwrap.dedent("""
		import path
		print("Successfully imported path.py")
		""").lstrip()
	script_file = tmpdir / 'script'
	script_file.write_text(body, 'utf-8')
	pip_args = ['path.py']
	cmd = [sys.executable, '-m', 'rwt'] + pip_args + ['--', str(script_file)]

	out = subprocess.check_output(cmd, universal_newlines=True)
	assert 'Successfully imported path.py' in out


class TestDepsReader:
	def test_reads_files_with_attribute_assignment(self):
		script = textwrap.dedent('''
			__requires__=['foo']
			x.a = 'bar'
			''')
		assert scripts.DepsReader(script).read() == ['foo']

	def test_reads_files_with_multiple_assignment(self):
		script = textwrap.dedent('''
			__requires__=['foo']
			x, a = [a, x]
			''')
		assert scripts.DepsReader(script).read() == ['foo']

	def test_single_dep(self):
		script = textwrap.dedent('''
			__requires__='foo'
			''')
		assert scripts.DepsReader(script).read() == ['foo']

	def test_index_url(self):
		script = textwrap.dedent('''
			__requires__ = ['foo']
			__index_url__ = 'https://my.private.index/'
			''')
		reqs = scripts.DepsReader(script).read()
		assert reqs.index_url == 'https://my.private.index/'


def test_pkg_loaded_from_alternate_index(tmpdir):
	"""
	Create a script that loads cython from an alternate index
	and ensure it runs.
	"""
	body = textwrap.dedent("""
		__requires__ = ['path.py']
		__index_url__ = 'https://devpi.net/root/pypi/+simple/'
		import path
		print("Successfully imported path.py")
		""").lstrip()
	script_file = tmpdir / 'script'
	script_file.write_text(body, 'utf-8')
	cmd = [sys.executable, '-m', 'rwt', '--', str(script_file)]

	out = subprocess.check_output(cmd, universal_newlines=True)
	assert 'Successfully imported path.py' in out
	assert 'devpi.net' in out
