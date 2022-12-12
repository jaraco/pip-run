import textwrap
import sys
import subprocess

import pytest
import nbformat
import jaraco.path

from pip_run import scripts


def DALS(str):
    return textwrap.dedent(str).lstrip()


def test_pkg_imported(tmp_path):
    """
    Create a script that loads cython and ensure it runs.
    """
    jaraco.path.build(
        {
            'script': DALS(
                """
                import path
                print("Successfully imported path.py")
                """
            )
        },
        tmp_path,
    )
    script = tmp_path / 'script'
    pip_args = ['path.py']
    cmd = [sys.executable, '-m', 'pip-run'] + pip_args + ['--', str(script)]

    out = subprocess.check_output(cmd, text=True)
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
        script = DALS(
            '''
            # coding: future_fstrings
            __requires__ = 'foo'
            f'boo'
            f'coo'
            '''
        )
        reqs = scripts.DepsReader(script).read()
        assert reqs == ['foo']

    def test_comment_style(self):
        script = textwrap.dedent(
            """
            #! shebang

            # Requirements:
            # foo == 3.1
            """
        )
        reqs = scripts.DepsReader(script).read()
        assert reqs == ['foo==3.1']


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
        reqs = scripts.DepsReader.try_read(notebook_factory.path)
        assert reqs == ['matplotlib']

    def test_multiple_code_blocks(self, notebook_factory):
        notebook_factory.add_code('__requires__ = ["matplotlib"]')
        notebook_factory.add_code("import matplotlib")
        notebook_factory.write()
        reqs = scripts.DepsReader.try_read(notebook_factory.path)
        assert reqs == ['matplotlib']

    def test_code_and_markdown(self, notebook_factory):
        notebook_factory.add_code('__requires__ = ["matplotlib"]')
        notebook_factory.add_markdown("Mark this down please")
        notebook_factory.write()
        reqs = scripts.DepsReader.try_read(notebook_factory.path)
        assert reqs == ['matplotlib']

    def test_jupyter_directives(self, notebook_factory):
        notebook_factory.add_code('__requires__ = ["matplotlib"]')
        notebook_factory.add_code("%matplotlib inline\nimport matplotlib")
        notebook_factory.write()
        reqs = scripts.DepsReader.try_read(notebook_factory.path)
        assert reqs == ['matplotlib']


def test_pkg_loaded_from_alternate_index(tmp_path):
    """
    Create a script that loads cython from an alternate index
    and ensure it runs.
    """
    jaraco.path.build(
        {
            'script': DALS(
                """
                __requires__ = ['path.py']
                __index_url__ = 'https://devpi.net/root/pypi/+simple/'
                import path
                print("Successfully imported path.py")
                """
            )
        },
        tmp_path,
    )
    cmd = [sys.executable, '-m', 'pip-run', '-v', '--', str(tmp_path / 'script')]

    out = subprocess.check_output(cmd, text=True)
    assert 'Successfully imported path.py' in out
    assert 'devpi.net' in out


def test_pkg_loaded_from_url(tmp_path):
    """
    Create a script whose dependency is only installable
    from a custom url and ensure it runs.
    """
    dependency = tmp_path / 'barbazquux-1.0'
    url_req = f'barbazquux @ file://{dependency.as_posix()}'
    jaraco.path.build(
        {
            'barbazquux-1.0': {
                'setup.py': DALS(
                    """
                    from setuptools import setup
                    setup(
                        name='barbazquux', version='1.0',
                        py_modules=['barbazquux'],
                    )
                    """
                ),
                'barbazquux.py': '',
            },
            'script_dir': {
                'script': DALS(
                    f"""
                    __requires__ = [{url_req!r}]
                    import barbazquux
                    print("Successfully imported barbazquux.py")
                    """
                ),
            },
        },
        tmp_path,
    )

    script = tmp_path.joinpath('script_dir', 'script')
    cmd = [sys.executable, '-m', 'pip-run', '--no-index', '--', str(script)]
    out = subprocess.check_output(cmd, text=True)
    assert 'Successfully imported barbazquux.py' in out
