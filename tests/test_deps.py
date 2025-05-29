import pytest

from pip_run import deps


@pytest.mark.usefixtures('retention_strategy')
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
