import copy

import pkg_resources

from rwt import deps


def test_entry_points():
	"""
	Ensure entry points are visible after making packages visible
	"""
	with deps.on_sys_path('jaraco.mongodb'):
		eps = pkg_resources.iter_entry_points('pytest11')
		assert list(eps), "Entry points not found"


class TestInstallCheck:
	def test_installed(self):
		assert deps.pkg_installed('rwt')

	def test_not_installed(self):
		assert not deps.pkg_installed('not_a_package')

	def test_installed_version(self):
		assert not deps.pkg_installed('rwt==0.0')

	def test_not_installed_args(self):
		args = [
			'-i', 'https://devpi.net',
			'-r', 'requirements.txt',
			'rwt',
			'not_a_package',
			'rwt==0.0',
		]
		expected = copy.copy(args)
		expected.remove('rwt')
		filtered = deps.not_installed(args)
		assert list(filtered) == expected


class TestLoad:
	def test_no_args_passes(self):
		"""
		If called with no arguments, load() should still provide
		a context.
		"""
		with deps.load():
			pass

	def test_only_options_passes(self):
		"""
		If called with only options, but no installable targets,
		load() should still provide a context.
		"""
		with deps.load('-q'):
			pass
