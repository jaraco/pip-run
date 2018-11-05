collect_ignore = ['examples']


def pytest_configure():
	workaround_sugar_issue_159()


def workaround_sugar_issue_159():
	"https://github.com/Frozenball/pytest-sugar/159"
	import pytest_sugar
	pytest_sugar.SugarTerminalReporter.pytest_runtest_logfinish = \
		lambda self: None
