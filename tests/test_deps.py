import sys

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


def test_installer_falls_back_to_interpreter(monkeypatch):
    monkeypatch.setattr(deps.shutil, 'which', lambda name: None)

    assert deps.installer('target') == [
        sys.executable,
        '-m',
        'pip',
        'install',
        '--target',
        'target',
    ]
