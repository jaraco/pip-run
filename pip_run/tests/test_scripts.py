import os
import textwrap
import sys
import subprocess

import pytest
import nbformat

from pip_run import scripts


def test_pkg_imported(tmpdir):
    """
    Create a script that loads cython and ensure it runs.
    """
    body = textwrap.dedent(
        """
        import path
        print("Successfully imported path.py")
        """
    ).lstrip()
    script_file = tmpdir / 'script'
    script_file.write_text(body, 'utf-8')
    pip_args = ['path.py']
    cmd = [sys.executable, '-m', 'pip-run'] + pip_args + ['--', str(script_file)]

    out = subprocess.check_output(cmd, universal_newlines=True)
    assert 'Successfully imported path.py' in out


class TestSourceDepsReader:
    def test_reads_files_with_attribute_assignment(self):
        script = textwrap.dedent(
            '''
            __requires__=['foo']
            x.a = 'bar'
            '''
        )
        assert scripts.DepsReader(script).read() == ['foo']

    def test_reads_files_with_multiple_assignment(self):
        script = textwrap.dedent(
            '''
            __requires__=['foo']
            x, a = [a, x]
            '''
        )
        assert scripts.DepsReader(script).read() == ['foo']

    def test_single_dep(self):
        script = textwrap.dedent(
            '''
            __requires__='foo'
            '''
        )
        assert scripts.DepsReader(script).read() == ['foo']

    def test_index_url(self):
        script = textwrap.dedent(
            '''
            __requires__ = ['foo']
            __index_url__ = 'https://my.private.index/'
            '''
        )
        reqs = scripts.DepsReader(script).read()
        assert reqs.index_url == 'https://my.private.index/'

    def test_fstrings_allowed(self):
        """
        It should be possible to read dependencies from a script
        with f-strings on all Pythons.
        """
        script = textwrap.dedent(
            '''
            # coding: future_fstrings
            __requires__ = 'foo'
            f'boo'
            f'coo'
            '''
        ).lstrip()
        reqs = scripts.DepsReader(script).read()
        assert reqs == ['foo']


class TestNotebookDepsReader:
    @pytest.fixture
    def notebook_factory(self, tmpdir, request):
        class Factory:
            def __init__(self):
                self.nb = nbformat.v4.new_notebook()
                self.path = tmpdir / (request.node.name + '.ipynb')

            @property
            def filename(self):
                return str(self.path)

            def write(self):
                nbformat.write(self.nb, self.filename)

            def add_code(self, code):
                self.nb['cells'].append(nbformat.v4.new_code_cell(code))

            def add_markdown(self, text):
                self.nb['cells'].append(nbformat.v4.new_markdown_cell(text))

        return Factory()

    def test_one_code_block(self, notebook_factory):
        notebook_factory.add_code('__requires__ = ["matplotlib"]')
        notebook_factory.write()
        reqs = scripts.DepsReader.try_read(notebook_factory.filename)
        assert reqs == ['matplotlib']

    def test_multiple_code_blocks(self, notebook_factory):
        notebook_factory.add_code('__requires__ = ["matplotlib"]')
        notebook_factory.add_code("import matplotlib")
        notebook_factory.write()
        reqs = scripts.DepsReader.try_read(notebook_factory.filename)
        assert reqs == ['matplotlib']

    def test_code_and_markdown(self, notebook_factory):
        notebook_factory.add_code('__requires__ = ["matplotlib"]')
        notebook_factory.add_markdown("Mark this down please")
        notebook_factory.write()
        reqs = scripts.DepsReader.try_read(notebook_factory.filename)
        assert reqs == ['matplotlib']

    def test_jupyter_directives(self, notebook_factory):
        notebook_factory.add_code('__requires__ = ["matplotlib"]')
        notebook_factory.add_code("%matplotlib inline\nimport matplotlib")
        notebook_factory.write()
        reqs = scripts.DepsReader.try_read(notebook_factory.filename)
        assert reqs == ['matplotlib']


def test_pkg_loaded_from_alternate_index(tmpdir):
    """
    Create a script that loads cython from an alternate index
    and ensure it runs.
    """
    body = textwrap.dedent(
        """
        __requires__ = ['path.py']
        __index_url__ = 'https://devpi.net/root/pypi/+simple/'
        import path
        print("Successfully imported path.py")
        """
    ).lstrip()
    script_file = tmpdir / 'script'
    script_file.write_text(body, 'utf-8')
    cmd = [sys.executable, '-m', 'pip-run', '--', str(script_file)]

    out = subprocess.check_output(cmd, universal_newlines=True)
    assert 'Successfully imported path.py' in out
    assert 'devpi.net' in out


def test_pkg_loaded_from_url(tmpdir):
    """
    Create a script whose dependency is only installable
    from a custom url and ensure it runs.
    """
    dependency = tmpdir.ensure_dir('barbazquux-1.0')
    (dependency / 'setup.py').write_text(
        textwrap.dedent(
            '''
        from setuptools import setup
        setup(
            name='barbazquux', version='1.0',
            py_modules=['barbazquux'],
        )
        '''
        ),
        'utf-8',
    )
    (dependency / 'barbazquux.py').write_text('', 'utf-8')
    url_req = 'barbazquux @ file://%s' % (dependency.strpath.replace(os.path.sep, '/'),)
    body = (
        textwrap.dedent(
            """
        __requires__ = [{url_req!r}]
        import barbazquux
        print("Successfully imported barbazquux.py")
        """
        )
        .lstrip()
        .format(**locals())
    )
    script_file = tmpdir.ensure_dir('script_dir') / 'script'
    script_file.write_text(body, 'utf-8')
    cmd = [sys.executable, '-m', 'pip-run', '--no-index', '--', str(script_file)]
    out = subprocess.check_output(cmd, universal_newlines=True)
    assert 'Successfully imported barbazquux.py' in out
